from calendar import monthrange as cal_monthrange
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import HTTPException, status
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.entity import (
    EntityCreate,
    EntityUpdate,
    EntityResponse,
    EntityMember,
    EntityMemberResponse,
    EntitySummary,
    MemberRole,
)


class EntityService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.entities
        self.users_collection = db.users
        self.transactions_collection = db.transactions

    async def create_entity(self, user_id: str, entity_data: EntityCreate) -> EntityResponse:
        entity_dict = entity_data.model_dump()
        entity_dict["created_by"] = ObjectId(user_id)
        entity_dict["created_at"] = datetime.now(timezone.utc)
        entity_dict["members"] = [
            {"user_id": user_id, "role": "admin", "joined_at": datetime.now(timezone.utc)}
        ]
        result = await self.collection.insert_one(entity_dict)
        await self.users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"entity_id": result.inserted_id, "entity_role": "admin"}},
        )
        created_entity = await self.collection.find_one({"_id": result.inserted_id})
        return self._entity_to_response(created_entity)

    async def get_entity(self, entity_id: str) -> Optional[EntityResponse]:
        if not ObjectId.is_valid(entity_id):
            return None
        entity = await self.collection.find_one({"_id": ObjectId(entity_id)})
        return self._entity_to_response(entity) if entity else None

    async def get_user_entity(self, user_id: str) -> Optional[EntityResponse]:
        user = await self.users_collection.find_one({"_id": ObjectId(user_id)})
        if not user or not user.get("entity_id"):
            return None
        return await self.get_entity(str(user["entity_id"]))

    async def update_entity(
        self, entity_id: str, user_id: str, entity_data: EntityUpdate
    ) -> Optional[EntityResponse]:
        if not await self._is_admin(entity_id, user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only entity admin can update entity",
            )
        update_dict = {
            k: v for k, v in entity_data.model_dump(exclude_unset=True).items()
            if v is not None
        }
        if not update_dict:
            return await self.get_entity(entity_id)
        result = await self.collection.update_one(
            {"_id": ObjectId(entity_id)}, {"$set": update_dict}
        )
        if result.matched_count == 0:
            return None
        return await self.get_entity(entity_id)

    async def invite_member(
        self, entity_id: str, admin_user_id: str, user_email: str, role: MemberRole
    ) -> bool:
        if not await self._is_admin(entity_id, admin_user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only entity admin can invite members",
            )
        user = await self.users_collection.find_one({"email": user_email})
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        if user.get("entity_id"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already belongs to an entity",
            )
        user_id = str(user["_id"])
        await self.collection.update_one(
            {"_id": ObjectId(entity_id)},
            {
                "$push": {
                    "members": {
                        "user_id": user_id,
                        "role": role,
                        "joined_at": datetime.now(timezone.utc),
                    }
                }
            },
        )
        await self.users_collection.update_one(
            {"_id": user["_id"]},
            {"$set": {"entity_id": ObjectId(entity_id), "entity_role": role}},
        )
        return True

    async def leave_entity(self, user_id: str) -> bool:
        user = await self.users_collection.find_one({"_id": ObjectId(user_id)})
        if not user or not user.get("entity_id"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="User is not in any entity"
            )
        entity_id = user["entity_id"]
        entity = await self.collection.find_one({"_id": entity_id})
        admin_count = sum(1 for m in entity.get("members", []) if m["role"] == "admin")
        if user.get("entity_role") == "admin" and admin_count == 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot leave: You are the only admin. Transfer admin rights first.",
            )
        await self.collection.update_one(
            {"_id": entity_id}, {"$pull": {"members": {"user_id": user_id}}}
        )
        await self.users_collection.update_one(
            {"_id": ObjectId(user_id)}, {"$unset": {"entity_id": "", "entity_role": ""}}
        )
        # Clean up user's transactions that were tagged with this entity
        await self.transactions_collection.update_many(
            {"user_id": ObjectId(user_id), "entity_id": entity_id},
            {"$unset": {"entity_id": ""}},
        )
        return True

    async def remove_member(
        self, entity_id: str, admin_user_id: str, member_user_id: str
    ) -> bool:
        if not await self._is_admin(entity_id, admin_user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only entity admin can remove members",
            )
        if admin_user_id == member_user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Use leave_entity to remove yourself",
            )
        # Verify member actually belongs to this entity before touching user record
        member_user = await self.users_collection.find_one({"_id": ObjectId(member_user_id)})
        if not member_user or str(member_user.get("entity_id", "")) != entity_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is not a member of this entity",
            )
        result = await self.collection.update_one(
            {"_id": ObjectId(entity_id)},
            {"$pull": {"members": {"user_id": member_user_id}}},
        )
        if result.modified_count > 0:
            await self.users_collection.update_one(
                {"_id": ObjectId(member_user_id)},
                {"$unset": {"entity_id": "", "entity_role": ""}},
            )
        return True

    async def change_member_role(
        self, entity_id: str, admin_user_id: str, member_user_id: str, new_role: MemberRole
    ) -> bool:
        if not await self._is_admin(entity_id, admin_user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only entity admin can change roles",
            )
        # Guard against demoting the last admin
        if new_role == "member":
            entity = await self.collection.find_one({"_id": ObjectId(entity_id)})
            admin_count = sum(
                1 for m in entity.get("members", []) if m["role"] == "admin"
            )
            is_target_admin = any(
                m["user_id"] == member_user_id and m["role"] == "admin"
                for m in entity.get("members", [])
            )
            if is_target_admin and admin_count == 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot demote the last admin. Promote another member first.",
                )
        await self.collection.update_one(
            {"_id": ObjectId(entity_id), "members.user_id": member_user_id},
            {"$set": {"members.$.role": new_role}},
        )
        await self.users_collection.update_one(
            {"_id": ObjectId(member_user_id)}, {"$set": {"entity_role": new_role}}
        )
        return True

    async def get_entity_members(
        self, entity_id: str, user_id: str
    ) -> List[EntityMemberResponse]:
        if not await self.is_member(entity_id, user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this entity",
            )
        entity = await self.collection.find_one({"_id": ObjectId(entity_id)})
        if not entity:
            return []
        member_entries = entity.get("members", [])
        member_ids = [ObjectId(m["user_id"]) for m in member_entries]
        users = await self.users_collection.find(
            {"_id": {"$in": member_ids}}
        ).to_list(length=len(member_ids))
        user_map = {str(u["_id"]): u for u in users}

        members = []
        for m in member_entries:
            u = user_map.get(m["user_id"])
            if u:
                members.append(
                    EntityMemberResponse(
                        user_id=m["user_id"],
                        username=u["username"],
                        email=u["email"],
                        role=m["role"],
                        joined_at=m["joined_at"],
                    )
                )
        return members

    async def get_entity_summary(
        self, entity_id: str, user_id: str, include_private: bool = False,
        month: Optional[int] = None, year: Optional[int] = None,
    ) -> EntitySummary:
        is_admin = await self._is_admin(entity_id, user_id)
        if include_private and not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admin can view all transactions including private",
            )
        entity = await self.collection.find_one({"_id": ObjectId(entity_id)})
        if not entity:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entity not found")

        # Build date filter when month+year are specified (use datetime, not strings)
        date_filter: dict = {}
        start_dt: Optional[datetime] = None
        end_dt: Optional[datetime] = None
        if month and year:
            last_day = cal_monthrange(year, month)[1]
            start_dt = datetime(year, month, 1, tzinfo=timezone.utc)
            end_dt = datetime(year, month, last_day, 23, 59, 59, tzinfo=timezone.utc)
            # Include transactions with a date in this month (covers all types),
            # PLUS recurring monthly transactions created before this month whose
            # recurrence is still active (avoids double-counting via date < start_dt).
            date_filter = {
                "$or": [
                    {"date": {"$gte": start_dt, "$lte": end_dt}},
                    {
                        "is_recurring": True,
                        "recurrence": "monthly",
                        "date": {"$lt": start_dt},
                        "$or": [
                            {"recurrence_start": {"$exists": False}},
                            {"recurrence_start": None},
                            {"recurrence_start": {"$lte": end_dt}},
                        ],
                    },
                ]
            }

        base_query: dict = {"entity_id": ObjectId(entity_id)}
        if not (is_admin and include_private):
            base_query["mode"] = "shared"

        query: dict = {**base_query}
        if date_filter:
            query["$and"] = [date_filter]

        # All-transactions totals
        pipeline = [
            {"$match": query},
            {"$group": {"_id": "$type", "total": {"$sum": "$amount"}, "count": {"$sum": 1}}},
        ]
        results = await self.transactions_collection.aggregate(pipeline).to_list(length=10)
        total_income = total_expense = transaction_count = 0.0
        for r in results:
            if r["_id"] == "income":
                total_income = r["total"]
            elif r["_id"] == "expense":
                total_expense = r["total"]
            transaction_count += r["count"]

        # Shared-only totals (also date-scoped when filtering)
        shared_match: dict = {"entity_id": ObjectId(entity_id), "mode": "shared"}
        if date_filter:
            shared_match["$and"] = [date_filter]
        shared_pipeline = [
            {"$match": shared_match},
            {"$group": {"_id": "$type", "total": {"$sum": "$amount"}, "count": {"$sum": 1}}},
        ]
        shared_results = await self.transactions_collection.aggregate(shared_pipeline).to_list(length=10)
        shared_income = shared_expense = shared_count = 0.0
        for r in shared_results:
            if r["_id"] == "income":
                shared_income = r["total"]
            elif r["_id"] == "expense":
                shared_expense = r["total"]
            shared_count += r["count"]

        # Category breakdown
        cat_results = await self.transactions_collection.aggregate(
            [{"$match": query}, {"$group": {"_id": "$category", "total": {"$sum": "$amount"}}}]
        ).to_list(length=500)
        categories_breakdown = {r["_id"]: round(r["total"], 2) for r in cat_results}

        # Member breakdown (admin only) — single aggregation + single batch user lookup
        member_breakdown: dict = {}
        if is_admin and include_private:
            member_entries = entity.get("members", [])
            member_ids = [ObjectId(m["user_id"]) for m in member_entries]

            # One aggregation grouped by (user_id, type)
            mb_pipeline = [
                {"$match": {"entity_id": ObjectId(entity_id), "user_id": {"$in": member_ids}}},
                {
                    "$group": {
                        "_id": {"user_id": "$user_id", "type": "$type"},
                        "total": {"$sum": "$amount"},
                    }
                },
            ]
            mb_results = await self.transactions_collection.aggregate(mb_pipeline).to_list(
                length=len(member_ids) * 2 + 1
            )

            # Build per-member totals from aggregation result
            mb_map: dict[str, dict] = {m["user_id"]: {"income": 0.0, "expense": 0.0} for m in member_entries}
            for r in mb_results:
                uid = str(r["_id"]["user_id"])
                t = r["_id"]["type"]
                if uid in mb_map:
                    mb_map[uid][t] = r["total"]

            # Batch user lookup
            users = await self.users_collection.find(
                {"_id": {"$in": member_ids}}
            ).to_list(length=len(member_ids))
            user_map = {str(u["_id"]): u for u in users}

            for uid, totals in mb_map.items():
                u = user_map.get(uid)
                member_breakdown[uid] = {
                    "username": u["username"] if u else "Unknown",
                    "income": round(totals["income"], 2),
                    "expense": round(totals["expense"], 2),
                    "balance": round(totals["income"] - totals["expense"], 2),
                }

        return EntitySummary(
            entity_id=str(entity["_id"]),
            entity_name=entity["name"],
            total_balance=round(total_income - total_expense, 2),
            total_income=round(total_income, 2),
            total_expense=round(total_expense, 2),
            shared_balance=round(shared_income - shared_expense, 2),
            shared_income=round(shared_income, 2),
            shared_expense=round(shared_expense, 2),
            transaction_count=int(transaction_count),
            shared_transaction_count=int(shared_count),
            categories_breakdown=categories_breakdown,
            member_breakdown=member_breakdown,
        )

    async def get_entity_monthly_history(
        self, entity_id: str, user_id: str, months: int = 6, include_private: bool = False
    ) -> list[dict]:
        # Delegate to get_entity_summary per month — same proven code path used by
        # the monthly dashboard tab (confirmed returning correct values).
        now = datetime.now(timezone.utc)
        result = []
        for i in range(months - 1, -1, -1):
            total_m = now.year * 12 + (now.month - 1) - i
            y, m = total_m // 12, (total_m % 12) + 1
            summary = await self.get_entity_summary(
                entity_id, user_id, include_private, month=m, year=y
            )
            result.append({
                "year": y,
                "month": m,
                "income": summary.total_income,
                "expense": summary.total_expense,
                "balance": summary.total_balance,
            })
        return result

    async def get_entity_recurring_transactions(
        self, entity_id: str, user_id: str, include_private: bool = False
    ) -> list[dict]:
        """Return all active monthly recurring transactions for the entity."""
        query: dict = {
            "entity_id": ObjectId(entity_id),
            "is_recurring": True,
            "recurrence": "monthly",
        }
        if not include_private:
            query["mode"] = "shared"
        cursor = self.transactions_collection.find(query)
        result = []
        async for doc in cursor:
            rs = doc.get("recurrence_start")
            result.append({
                "id": str(doc["_id"]),
                "type": doc.get("type"),
                "amount": doc.get("amount", 0),
                "description": doc.get("description", ""),
                "recurrence_start": rs.isoformat() if rs else None,
            })
        return result

    async def delete_entity(self, entity_id: str, user_id: str) -> bool:
        """Delete entity (admin only). Clears all member records and detaches transactions."""
        if not await self._is_admin(entity_id, user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only entity admin can delete the entity",
            )
        entity = await self.collection.find_one({"_id": ObjectId(entity_id)})
        if not entity:
            return False

        member_ids = [ObjectId(m["user_id"]) for m in entity.get("members", [])]

        # Clear entity membership from all member user records
        if member_ids:
            await self.users_collection.update_many(
                {"_id": {"$in": member_ids}},
                {"$unset": {"entity_id": "", "entity_role": ""}},
            )

        # Detach all transactions that were tagged with this entity
        await self.transactions_collection.update_many(
            {"entity_id": ObjectId(entity_id)},
            {"$unset": {"entity_id": ""}},
        )

        result = await self.collection.delete_one({"_id": ObjectId(entity_id)})
        return result.deleted_count > 0

    async def is_member(self, entity_id: str, user_id: str) -> bool:
        entity = await self.collection.find_one(
            {"_id": ObjectId(entity_id), "members.user_id": user_id}
        )
        return entity is not None

    async def _is_admin(self, entity_id: str, user_id: str) -> bool:
        entity = await self.collection.find_one(
            {
                "_id": ObjectId(entity_id),
                "members": {"$elemMatch": {"user_id": user_id, "role": "admin"}},
            }
        )
        return entity is not None

    def _entity_to_response(self, entity: dict) -> EntityResponse:
        members = [
            EntityMember(
                user_id=m["user_id"],
                role=m["role"],
                joined_at=m["joined_at"],
            )
            for m in entity.get("members", [])
        ]
        return EntityResponse(
            id=str(entity["_id"]),
            name=entity["name"],
            entity_type=entity["entity_type"],
            custom_type_name=entity.get("custom_type_name"),
            description=entity.get("description"),
            members=members,
            created_by=str(entity["created_by"]),
            created_at=entity["created_at"],
            member_count=len(members),
        )
