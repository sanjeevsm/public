from datetime import datetime, timezone
from typing import List, Optional
from io import StringIO
import csv
import logging
from fastapi import HTTPException, status, UploadFile
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.transaction import (
    TransactionCreate,
    TransactionUpdate,
    TransactionResponse,
    TransactionSummary,
    TransactionImportRow,
)

logger = logging.getLogger(__name__)

_CSV_MAX_BYTES = 5 * 1024 * 1024  # 5 MB


class TransactionService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.transactions

    async def create_transaction(
        self, user_id: str, transaction_data: TransactionCreate
    ) -> TransactionResponse:
        transaction_dict = transaction_data.model_dump()
        transaction_dict["user_id"] = ObjectId(user_id)
        transaction_dict["created_at"] = datetime.now(timezone.utc)
        user = await self.db.users.find_one({"_id": ObjectId(user_id)})
        if user and user.get("entity_id"):
            transaction_dict["entity_id"] = user["entity_id"]
        result = await self.collection.insert_one(transaction_dict)
        created = await self.collection.find_one({"_id": result.inserted_id})
        return self._transaction_to_response(created)

    async def get_transactions(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 100,
        type_filter: Optional[str] = None,
        category_filter: Optional[str] = None,
    ) -> List[TransactionResponse]:
        query: dict = {"user_id": ObjectId(user_id)}
        if type_filter:
            query["type"] = type_filter
        if category_filter:
            query["category"] = category_filter
        cursor = self.collection.find(query).sort("date", -1).skip(skip).limit(limit)
        transactions = await cursor.to_list(length=limit)
        return [self._transaction_to_response(t) for t in transactions]

    async def get_transaction_by_id(
        self, user_id: str, transaction_id: str
    ) -> Optional[TransactionResponse]:
        if not ObjectId.is_valid(transaction_id):
            return None
        transaction = await self.collection.find_one(
            {"_id": ObjectId(transaction_id), "user_id": ObjectId(user_id)}
        )
        return self._transaction_to_response(transaction) if transaction else None

    async def update_transaction(
        self, user_id: str, transaction_id: str, transaction_data: TransactionUpdate
    ) -> Optional[TransactionResponse]:
        if not ObjectId.is_valid(transaction_id):
            return None
        # Allow explicitly-set None values to clear optional fields
        update_dict = transaction_data.model_dump(exclude_unset=True)
        if not update_dict:
            return await self.get_transaction_by_id(user_id, transaction_id)
        result = await self.collection.update_one(
            {"_id": ObjectId(transaction_id), "user_id": ObjectId(user_id)},
            {"$set": update_dict},
        )
        if result.matched_count == 0:
            return None
        return await self.get_transaction_by_id(user_id, transaction_id)

    async def delete_transaction(self, user_id: str, transaction_id: str) -> bool:
        if not ObjectId.is_valid(transaction_id):
            return False
        result = await self.collection.delete_one(
            {"_id": ObjectId(transaction_id), "user_id": ObjectId(user_id)}
        )
        return result.deleted_count > 0

    async def get_summary(self, user_id: str) -> TransactionSummary:
        pipeline = [
            {"$match": {"user_id": ObjectId(user_id)}},
            {"$group": {"_id": "$type", "total": {"$sum": "$amount"}, "count": {"$sum": 1}}},
        ]
        results = await self.collection.aggregate(pipeline).to_list(length=10)
        income_total = expense_total = income_count = expense_count = 0
        for r in results:
            if r["_id"] == "income":
                income_total, income_count = r["total"], r["count"]
            elif r["_id"] == "expense":
                expense_total, expense_count = r["total"], r["count"]

        cat_results = await self.collection.aggregate(
            [
                {"$match": {"user_id": ObjectId(user_id)}},
                {"$group": {"_id": "$category", "total": {"$sum": "$amount"}}},
            ]
        ).to_list(length=500)
        categories_breakdown = {r["_id"]: round(r["total"], 2) for r in cat_results}

        return TransactionSummary(
            total_balance=round(income_total - expense_total, 2),
            total_income=round(income_total, 2),
            total_expense=round(expense_total, 2),
            income_count=income_count,
            expense_count=expense_count,
            categories_breakdown=categories_breakdown,
        )

    async def export_to_csv(self, user_id: str) -> str:
        """Stream all transactions directly from cursor — no memory cap."""
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["description", "amount", "type", "category", "date"])
        cursor = self.collection.find({"user_id": ObjectId(user_id)}).sort("date", -1)
        async for transaction in cursor:
            writer.writerow(
                [
                    transaction["description"],
                    transaction["amount"],
                    transaction["type"],
                    transaction["category"],
                    transaction["date"].isoformat(),
                ]
            )
        return output.getvalue()

    async def import_from_csv(self, user_id: str, file: UploadFile) -> dict:
        if not file.filename.endswith(".csv"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="File must be a CSV"
            )

        content = await file.read(_CSV_MAX_BYTES + 1)
        if len(content) > _CSV_MAX_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"CSV file exceeds the {_CSV_MAX_BYTES // (1024*1024)} MB limit",
            )

        csv_reader = csv.DictReader(StringIO(content.decode("utf-8")))
        imported_count = failed_count = 0
        errors: list[str] = []

        for row_num, row in enumerate(csv_reader, start=2):
            try:
                import_row = TransactionImportRow(
                    description=row.get("description", ""),
                    amount=float(row.get("amount", 0)),
                    type=row.get("type", ""),
                    category=row.get("category", ""),
                    date=row.get("date", ""),
                )
                try:
                    date_obj = datetime.fromisoformat(import_row.date.replace("Z", "+00:00"))
                except ValueError:
                    date_obj = datetime.now(timezone.utc)
                await self.create_transaction(
                    user_id,
                    TransactionCreate(
                        description=import_row.description,
                        amount=import_row.amount,
                        type=import_row.type,
                        category=import_row.category,
                        date=date_obj,
                    ),
                )
                imported_count += 1
            except Exception as exc:
                failed_count += 1
                errors.append(f"Row {row_num}: {exc}")

        return {"imported": imported_count, "failed": failed_count, "errors": errors[:10]}

    def _transaction_to_response(self, transaction: dict) -> TransactionResponse:
        return TransactionResponse(
            id=str(transaction["_id"]),
            description=transaction["description"],
            amount=transaction["amount"],
            type=transaction["type"],
            category=transaction["category"],
            date=transaction["date"],
            mode=transaction.get("mode", "private"),
            created_at=transaction["created_at"],
            user_id=str(transaction["user_id"]),
            entity_id=str(transaction["entity_id"]) if transaction.get("entity_id") else None,
        )
