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
        limit: int = 50,
        type_filter: Optional[str] = None,
        category_filter: Optional[str] = None,
        currency_filter: Optional[str] = None,
    ) -> List[TransactionResponse]:
        query: dict = {"user_id": ObjectId(user_id)}
        if type_filter:
            query["type"] = type_filter
        if category_filter:
            query["category"] = category_filter
        if currency_filter:
            query["currency"] = currency_filter
        # Enforce a reasonable maximum limit to prevent large memory consumption
        MAX_LIMIT = 200
        if limit > MAX_LIMIT:
            limit = MAX_LIMIT
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

    async def get_summary(self, user_id: str, year: int | None = None, month: int | None = None, currency: str = "USD") -> TransactionSummary:
        """Return summary. If year and month are provided, compute totals for that month including monthly recurring items."""
        match_base = {"user_id": ObjectId(user_id), "currency": currency}

        # If monthly view is requested, compute start/end for the month and include recurring monthly items
        if year and month:
            from calendar import monthrange

            start = datetime(year, month, 1, tzinfo=timezone.utc)
            last_day = monthrange(year, month)[1]
            end = datetime(year, month, last_day, 23, 59, 59, tzinfo=timezone.utc)

            pipeline = [
                {"$match": match_base},
                {
                    "$project": {
                        "amount": 1,
                        "type": 1,
                        "category": 1,
                        "date": 1,
                        "is_recurring": 1,
                        "recurrence": 1,
                        "recurrence_start": 1,
                        "in_month": {
                            "$and": [{"$gte": ["$date", start]}, {"$lte": ["$date", end]}]
                        },
                        "is_active_recurring": {
                            "$and": [
                                {"$eq": ["$is_recurring", True]},
                                {"$eq": ["$recurrence", "monthly"]},
                                {"$or": [{"$eq": ["$recurrence_start", None]}, {"$lte": ["$recurrence_start", end]}]}
                            ]
                        },
                    }
                },
                {
                    "$addFields": {
                        "count_included": {"$cond": [{"$or": ["$in_month", "$is_active_recurring"]}, 1, 0]},
                        "amount_included": {"$cond": [{"$or": ["$in_month", "$is_active_recurring"]}, "$amount", 0]},
                    }
                },
                {
                    "$group": {"_id": "$type", "total": {"$sum": "$amount_included"}, "count": {"$sum": "$count_included"}}
                },
            ]
            results = await self.collection.aggregate(pipeline).to_list(length=10)
        else:
            pipeline = [
                {"$match": match_base},
                {"$group": {"_id": "$type", "total": {"$sum": "$amount"}, "count": {"$sum": 1}}},
            ]
            results = await self.collection.aggregate(pipeline).to_list(length=10)

        income_total = expense_total = asset_total = liability_total = 0
        income_count = expense_count = asset_count = liability_count = 0
        for r in results:
            if r["_id"] == "income":
                income_total, income_count = r["total"], r["count"]
            elif r["_id"] == "expense":
                expense_total, expense_count = r["total"], r["count"]
            elif r["_id"] == "asset":
                asset_total, asset_count = r["total"], r["count"]
            elif r["_id"] == "liability":
                liability_total, liability_count = r["total"], r["count"]

        # categories breakdown: for monthly view consider same inclusion logic
        if year and month:
            cat_pipeline = [
                {"$match": match_base},
                {
                    "$project": {
                        "category": 1,
                        "amount": 1,
                        "date": 1,
                        "is_recurring": 1,
                        "recurrence": 1,
                        "recurrence_start": 1,
                        "in_month": {"$and": [{"$gte": ["$date", start]}, {"$lte": ["$date", end]}]},
                        "is_active_recurring": {"$and": [{"$eq": ["$is_recurring", True]}, {"$eq": ["$recurrence", "monthly"]}, {"$or": [{"$eq": ["$recurrence_start", None]}, {"$lte": ["$recurrence_start", end]}]}]},
                    }
                },
                {
                    "$project": {"category": 1, "amount_included": {"$cond": [{"$or": ["$in_month", "$is_active_recurring"]}, "$amount", 0]}}
                },
                {"$group": {"_id": "$category", "total": {"$sum": "$amount_included"}}},
            ]
            cat_results = await self.collection.aggregate(cat_pipeline).to_list(length=500)
        else:
            cat_results = await self.collection.aggregate([
                {"$match": match_base},
                {"$group": {"_id": "$category", "total": {"$sum": "$amount"}}},
            ]).to_list(length=500)

        categories_breakdown = {r["_id"]: round(r["total"], 2) for r in cat_results}

        # Calculate net worth: (income - expense) + (assets - liabilities)
        balance = income_total - expense_total
        net_worth = balance + asset_total - liability_total

        return TransactionSummary(
            total_balance=round(balance, 2),
            total_income=round(income_total, 2),
            total_expense=round(expense_total, 2),
            total_assets=round(asset_total, 2),
            total_liabilities=round(liability_total, 2),
            net_worth=round(net_worth, 2),
            income_count=int(income_count),
            expense_count=int(expense_count),
            asset_count=int(asset_count),
            liability_count=int(liability_count),
            categories_breakdown=categories_breakdown,
            currency=currency,
        )

    async def get_monthly_history(self, user_id: str, months: int = 6, currency: str = "USD") -> list[dict]:
        """Return per-month income/expense/balance for the last N months, newest last."""
        now = datetime.now(timezone.utc)
        result = []
        for i in range(months - 1, -1, -1):
            total_m = now.year * 12 + (now.month - 1) - i
            y, m = total_m // 12, (total_m % 12) + 1
            summary = await self.get_summary(user_id, y, m, currency)
            result.append({
                "year": y,
                "month": m,
                "income": summary.total_income,
                "expense": summary.total_expense,
                "balance": summary.total_balance,
            })
        return result

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

    async def get_multi_currency_summary(self, user_id: str, currencies: List[str]) -> List[TransactionSummary]:
        """Get summary for multiple currencies."""
        summaries = []
        for currency in currencies:
            summary = await self.get_summary(user_id, currency=currency)
            summaries.append(summary)
        return summaries

    async def get_consolidated_summary(self, user_id: str, currencies: List[str]) -> dict:
        """Get consolidated view across all currencies (no conversion, just list)."""
        summaries = await self.get_multi_currency_summary(user_id, currencies)
        return {
            "currencies": summaries,
            "note": "Each currency shown separately. No conversion applied."
        }

    def _transaction_to_response(self, transaction: dict) -> TransactionResponse:
        return TransactionResponse(
            id=str(transaction["_id"]),
            description=transaction["description"],
            amount=transaction["amount"],
            type=transaction["type"],
            category=transaction["category"],
            date=transaction["date"],
            mode=transaction.get("mode", "private"),
            currency=transaction.get("currency", "USD"),
            created_at=transaction["created_at"],
            user_id=str(transaction["user_id"]),
            entity_id=str(transaction["entity_id"]) if transaction.get("entity_id") else None,
        )

    async def get_recurring_transactions(self, user_id: str, currency: Optional[str] = None) -> list[dict]:
        """Return all active monthly recurring transactions for the user."""
        query = {
            "user_id": ObjectId(user_id),
            "is_recurring": True,
            "recurrence": "monthly",
        }
        if currency:
            query["currency"] = currency
        cursor = self.collection.find(query)
        result = []
        async for doc in cursor:
            rs = doc.get("recurrence_start")
            result.append({
                "id": str(doc["_id"]),
                "type": doc.get("type"),
                "amount": doc.get("amount", 0),
                "description": doc.get("description", ""),
                "currency": doc.get("currency", "USD"),  # Add currency field
                "recurrence_start": rs.isoformat() if rs else None,
            })
        return result

    async def bulk_create_transactions(self, user_id: str, transactions: list[dict]) -> dict:
        """Create many transactions in a single DB operation. Returns summary with inserted count and errors.

        Each item in `transactions` should conform to TransactionCreate fields.
        """
        from app.models.transaction import TransactionCreate

        # Validate and prepare documents
        prepared = []
        errors = []
        user = await self.db.users.find_one({"_id": ObjectId(user_id)})
        entity_id = user.get("entity_id") if user else None

        for idx, t in enumerate(transactions):
            try:
                tx = TransactionCreate.model_validate(t)
                doc = tx.model_dump()
                doc["user_id"] = ObjectId(user_id)
                doc["created_at"] = datetime.now(timezone.utc)
                if entity_id:
                    doc["entity_id"] = entity_id
                prepared.append(doc)
            except Exception as exc:
                errors.append({"row": idx, "error": str(exc)})

        if not prepared:
            return {"inserted": 0, "failed": len(errors), "errors": errors}

        try:
            result = await self.collection.insert_many(prepared, ordered=False)
            inserted = len(result.inserted_ids)
        except Exception as exc:
            # If insert_many fails, report partial failure
            return {"inserted": 0, "failed": len(prepared), "errors": errors + [{"db_error": str(exc)}]}

        return {"inserted": inserted, "failed": len(errors), "errors": errors}
