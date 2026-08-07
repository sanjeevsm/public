from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime, timezone, timedelta

from app.models.budget import (
    BudgetCreate,
    BudgetUpdate,
    BudgetResponse,
    BudgetInDB,
    BudgetProgress,
    BudgetPeriod,
)


class BudgetService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["budgets"]
        self.transactions_collection = db["transactions"]

    async def _budget_to_response(self, budget: dict) -> BudgetResponse:
        return BudgetResponse(
            id=str(budget["_id"]),
            name=budget["name"],
            amount=budget["amount"],
            period=budget["period"],
            budget_type=budget["budget_type"],
            category=budget.get("category"),
            start_date=budget["start_date"],
            end_date=budget.get("end_date"),
            alert_threshold=budget.get("alert_threshold", 80.0),
            user_id=str(budget["user_id"]),
            entity_id=str(budget["entity_id"]) if budget.get("entity_id") else None,
            created_at=budget["created_at"],
            updated_at=budget.get("updated_at", budget["created_at"]),
        )

    def _get_period_dates(self, period: BudgetPeriod) -> tuple[datetime, datetime]:
        now = datetime.now(timezone.utc)
        if period == "daily":
            period_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            period_end = period_start + timedelta(days=1)
        elif period == "weekly":
            period_start = now - timedelta(days=now.weekday())
            period_start = period_start.replace(hour=0, minute=0, second=0, microsecond=0)
            period_end = period_start + timedelta(days=7)
        elif period == "monthly":
            period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            next_month = period_start.replace(day=28) + timedelta(days=4)
            period_end = next_month.replace(day=1)
        else:  # yearly
            period_start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            period_end = period_start.replace(year=period_start.year + 1)
        return period_start, period_end

    async def create_budget(
        self,
        user_id: str,
        budget_data: BudgetCreate,
        entity_id: Optional[str] = None,
    ) -> BudgetResponse:
        budget = BudgetInDB(
            **budget_data.model_dump(),
            user_id=ObjectId(user_id),
            entity_id=ObjectId(entity_id) if entity_id else None,
        )
        result = await self.collection.insert_one(
            budget.model_dump(by_alias=True, exclude={"id"})
        )
        created_budget = await self.collection.find_one({"_id": result.inserted_id})
        return await self._budget_to_response(created_budget)

    async def get_budgets(
        self,
        user_id: str,
        entity_id: Optional[str] = None,
        active_only: bool = False,
    ) -> List[BudgetResponse]:
        query = {"user_id": ObjectId(user_id)}
        if entity_id:
            query["entity_id"] = ObjectId(entity_id)
        if active_only:
            now = datetime.now(timezone.utc)
            query["$or"] = [{"end_date": None}, {"end_date": {"$gte": now}}]
        cursor = self.collection.find(query).sort("created_at", -1)
        budgets = await cursor.to_list(length=1000)
        return [await self._budget_to_response(b) for b in budgets]

    async def get_budget(self, budget_id: str, user_id: str) -> Optional[BudgetResponse]:
        budget = await self.collection.find_one(
            {"_id": ObjectId(budget_id), "user_id": ObjectId(user_id)}
        )
        return await self._budget_to_response(budget) if budget else None

    async def update_budget(
        self,
        budget_id: str,
        user_id: str,
        budget_data: BudgetUpdate,
    ) -> Optional[BudgetResponse]:
        budget = await self.collection.find_one(
            {"_id": ObjectId(budget_id), "user_id": ObjectId(user_id)}
        )
        if not budget:
            return None

        # Keep all explicitly-set fields, including None (allows clearing end_date)
        update_data = budget_data.model_dump(exclude_unset=True)
        update_data["updated_at"] = datetime.now(timezone.utc)

        await self.collection.update_one(
            {"_id": ObjectId(budget_id)}, {"$set": update_data}
        )
        updated = await self.collection.find_one({"_id": ObjectId(budget_id)})
        return await self._budget_to_response(updated)

    async def delete_budget(self, budget_id: str, user_id: str) -> bool:
        result = await self.collection.delete_one(
            {"_id": ObjectId(budget_id), "user_id": ObjectId(user_id)}
        )
        return result.deleted_count > 0

    async def get_budget_progress(
        self, budget_id: str, user_id: str
    ) -> Optional[BudgetProgress]:
        budget = await self.collection.find_one(
            {"_id": ObjectId(budget_id), "user_id": ObjectId(user_id)}
        )
        if not budget:
            return None
        return self._compute_progress(budget, user_id=user_id)

    def _compute_progress_from_spent(
        self, budget: dict, spent_amount: float
    ) -> BudgetProgress:
        """Build BudgetProgress from an already-computed spent_amount."""
        period_start, period_end = self._get_period_dates(budget["period"])
        budget_amount = budget["amount"]
        remaining = budget_amount - spent_amount
        pct = (spent_amount / budget_amount * 100) if budget_amount > 0 else 0
        now = datetime.now(timezone.utc)
        return BudgetProgress(
            budget_id=str(budget["_id"]),
            budget_name=budget["name"],
            budget_amount=budget_amount,
            spent_amount=spent_amount,
            remaining_amount=remaining,
            percentage_spent=round(pct, 2),
            is_exceeded=spent_amount > budget_amount,
            is_alert=pct >= budget.get("alert_threshold", 80.0),
            period=budget["period"],
            category=budget.get("category"),
            days_remaining=(period_end - now).days if period_end > now else 0,
        )

    async def _compute_progress(self, budget: dict, user_id: str) -> BudgetProgress:
        period_start, period_end = self._get_period_dates(budget["period"])
        query = {
            "user_id": ObjectId(user_id),
            "type": "expense",
            "date": {"$gte": period_start, "$lt": period_end},
        }
        if budget["budget_type"] == "category" and budget.get("category"):
            query["category"] = budget["category"]
        pipeline = [{"$match": query}, {"$group": {"_id": None, "total": {"$sum": "$amount"}}}]
        results = await self.transactions_collection.aggregate(pipeline).to_list(length=1)
        spent_amount = results[0]["total"] if results else 0.0
        return self._compute_progress_from_spent(budget, spent_amount)

    async def get_all_budgets_progress(
        self, user_id: str, entity_id: Optional[str] = None
    ) -> List[BudgetProgress]:
        """Get progress for all active budgets using at most 4 DB round trips."""
        budgets_raw = await self.collection.find(
            self._active_query(user_id, entity_id)
        ).to_list(length=1000)

        if not budgets_raw:
            return []

        # Group budgets by period and pre-fetch spending totals per period
        from collections import defaultdict
        period_groups: dict[str, list] = defaultdict(list)
        for b in budgets_raw:
            period_groups[b["period"]].append(b)

        # For each period, one aggregation returning totals per category
        spending_cache: dict[str, dict[str, float]] = {}
        for period, group in period_groups.items():
            period_start, period_end = self._get_period_dates(period)
            pipeline = [
                {
                    "$match": {
                        "user_id": ObjectId(user_id),
                        "type": "expense",
                        "date": {"$gte": period_start, "$lt": period_end},
                    }
                },
                {"$group": {"_id": "$category", "total": {"$sum": "$amount"}}},
            ]
            results = await self.transactions_collection.aggregate(pipeline).to_list(length=500)
            # Also store a "__total__" key for total-type budgets
            grand_total = sum(r["total"] for r in results)
            spending_cache[period] = {r["_id"]: r["total"] for r in results}
            spending_cache[period]["__total__"] = grand_total

        progress_list = []
        for budget in budgets_raw:
            period = budget["period"]
            cache = spending_cache.get(period, {})
            if budget["budget_type"] == "category" and budget.get("category"):
                spent = cache.get(budget["category"], 0.0)
            else:
                spent = cache.get("__total__", 0.0)
            progress_list.append(self._compute_progress_from_spent(budget, spent))

        return progress_list

    def _active_query(self, user_id: str, entity_id: Optional[str]) -> dict:
        now = datetime.now(timezone.utc)
        q = {
            "user_id": ObjectId(user_id),
            "$or": [{"end_date": None}, {"end_date": {"$gte": now}}],
        }
        if entity_id:
            q["entity_id"] = ObjectId(entity_id)
        return q

    async def check_budget_alerts(self, user_id: str) -> List[BudgetProgress]:
        all_progress = await self.get_all_budgets_progress(user_id)
        return [p for p in all_progress if p.is_alert or p.is_exceeded]
