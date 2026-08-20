from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime, timezone

from app.models.category import CategoryCreate, CategoryUpdate, CategoryResponse, CategoryInDB


class CategoryService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["categories"]

    async def _category_to_response(self, category: dict) -> CategoryResponse:
        return CategoryResponse(
            id=str(category["_id"]),
            name=category["name"],
            type=category["type"],
            color=category.get("color"),
            icon=category.get("icon"),
            description=category.get("description"),
            is_default=category.get("is_default", False),
            user_id=str(category["user_id"]) if category.get("user_id") else None,
            entity_id=str(category["entity_id"]) if category.get("entity_id") else None,
            created_at=category["created_at"],
        )

    async def initialize_default_categories(self):
        default_categories = [
            # Income categories
            {"name": "Salary", "type": "income", "icon": "💰", "color": "#10B981", "is_default": True},
            {"name": "Freelance", "type": "income", "icon": "💼", "color": "#059669", "is_default": True},
            {"name": "Investment", "type": "income", "icon": "📈", "color": "#34D399", "is_default": True},
            {"name": "Business", "type": "income", "icon": "🏢", "color": "#6EE7B7", "is_default": True},
            # Expense categories
            {"name": "Food & Dining", "type": "expense", "icon": "🍔", "color": "#EF4444", "is_default": True},
            {"name": "Transportation", "type": "expense", "icon": "🚗", "color": "#F97316", "is_default": True},
            {"name": "Shopping", "type": "expense", "icon": "🛍️", "color": "#F59E0B", "is_default": True},
            {"name": "Entertainment", "type": "expense", "icon": "🎬", "color": "#8B5CF6", "is_default": True},
            {"name": "Bills & Utilities", "type": "expense", "icon": "💡", "color": "#3B82F6", "is_default": True},
            {"name": "Healthcare", "type": "expense", "icon": "⚕️", "color": "#EC4899", "is_default": True},
            {"name": "Education", "type": "expense", "icon": "📚", "color": "#14B8A6", "is_default": True},
            {"name": "Housing", "type": "expense", "icon": "🏠", "color": "#6366F1", "is_default": True},
            # Asset categories
            {"name": "Cash", "type": "asset", "icon": "💵", "color": "#10B981", "is_default": True},
            {"name": "Investments", "type": "asset", "icon": "📊", "color": "#059669", "is_default": True},
            {"name": "Property", "type": "asset", "icon": "🏡", "color": "#34D399", "is_default": True},
            {"name": "Valuables", "type": "asset", "icon": "💎", "color": "#6EE7B7", "is_default": True},
            # Liability categories
            {"name": "Mortgages", "type": "liability", "icon": "🏦", "color": "#EF4444", "is_default": True},
            {"name": "Loans", "type": "liability", "icon": "💳", "color": "#F97316", "is_default": True},
            {"name": "Credit Cards", "type": "liability", "icon": "💸", "color": "#F59E0B", "is_default": True},
            # General
            {"name": "Other", "type": "both", "icon": "📌", "color": "#6B7280", "is_default": True},
        ]
        for cat_data in default_categories:
            existing = await self.collection.find_one(
                {"name": cat_data["name"], "is_default": True, "user_id": None}
            )
            if not existing:
                await self.collection.insert_one(
                    {
                        **cat_data,
                        "user_id": None,
                        "entity_id": None,
                        "created_at": datetime.now(timezone.utc),
                        "updated_at": datetime.now(timezone.utc),
                    }
                )

    async def create_category(
        self,
        user_id: str,
        category_data: CategoryCreate,
        entity_id: Optional[str] = None,
    ) -> CategoryResponse:
        existing = await self.collection.find_one(
            {"name": category_data.name, "user_id": ObjectId(user_id)}
        )
        if existing:
            raise ValueError("Category with this name already exists")

        category = CategoryInDB(
            **category_data.model_dump(),
            user_id=ObjectId(user_id),
            entity_id=ObjectId(entity_id) if entity_id else None,
        )
        result = await self.collection.insert_one(
            category.model_dump(by_alias=True, exclude={"id"})
        )
        created = await self.collection.find_one({"_id": result.inserted_id})
        return await self._category_to_response(created)

    async def get_categories(
        self,
        user_id: str,
        type_filter: Optional[str] = None,
        entity_id: Optional[str] = None,
    ) -> List[CategoryResponse]:
        or_clauses = [
            {"user_id": None, "is_default": True},
            {"user_id": ObjectId(user_id)},
        ]
        if entity_id:
            # Only include categories explicitly tagged as entity-level (no owner)
            or_clauses.append({"entity_id": ObjectId(entity_id), "user_id": None})

        query: dict = {"$or": or_clauses}
        if type_filter:
            query["type"] = {"$in": [type_filter, "both"]}

        cursor = self.collection.find(query).sort("name", 1)
        categories = await cursor.to_list(length=500)
        return [await self._category_to_response(c) for c in categories]

    async def get_category(self, category_id: str, user_id: str) -> Optional[CategoryResponse]:
        category = await self.collection.find_one(
            {
                "_id": ObjectId(category_id),
                "$or": [
                    {"user_id": None, "is_default": True},
                    {"user_id": ObjectId(user_id)},
                ],
            }
        )
        return await self._category_to_response(category) if category else None

    async def update_category(
        self,
        category_id: str,
        user_id: str,
        category_data: CategoryUpdate,
    ) -> Optional[CategoryResponse]:
        category = await self.collection.find_one(
            {"_id": ObjectId(category_id), "user_id": ObjectId(user_id)}
        )
        if not category:
            raise ValueError("Category not found or cannot be modified")
        if category.get("is_default"):
            raise ValueError("Cannot modify default categories")

        if category_data.name:
            existing = await self.collection.find_one(
                {
                    "name": category_data.name,
                    "user_id": ObjectId(user_id),
                    "_id": {"$ne": ObjectId(category_id)},
                }
            )
            if existing:
                raise ValueError("Category with this name already exists")

        # Allow explicitly-set None values to clear optional fields
        update_data = category_data.model_dump(exclude_unset=True)
        update_data["updated_at"] = datetime.now(timezone.utc)

        await self.collection.update_one(
            {"_id": ObjectId(category_id)}, {"$set": update_data}
        )
        updated = await self.collection.find_one({"_id": ObjectId(category_id)})
        return await self._category_to_response(updated)

    async def delete_category(self, category_id: str, user_id: str) -> bool:
        category = await self.collection.find_one(
            {"_id": ObjectId(category_id), "user_id": ObjectId(user_id)}
        )
        if not category:
            return False
        if category.get("is_default"):
            raise ValueError("Cannot delete default categories")
        result = await self.collection.delete_one(
            {"_id": ObjectId(category_id), "user_id": ObjectId(user_id)}
        )
        return result.deleted_count > 0

    async def get_category_usage_stats(self, user_id: str) -> dict:
        pipeline = [
            {"$match": {"user_id": ObjectId(user_id)}},
            {"$group": {"_id": "$category", "count": {"$sum": 1}, "total_amount": {"$sum": "$amount"}}},
            {"$sort": {"count": -1}},
        ]
        results = await self.db["transactions"].aggregate(pipeline).to_list(length=500)
        return {
            item["_id"]: {"count": item["count"], "total_amount": item["total_amount"]}
            for item in results
        }
