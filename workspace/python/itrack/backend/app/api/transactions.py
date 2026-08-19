from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status
from fastapi.responses import StreamingResponse
from motor.motor_asyncio import AsyncIOMotorDatabase
from io import BytesIO

from app.core.database import get_database
from app.models.transaction import (
    TransactionCreate,
    TransactionUpdate,
    TransactionResponse,
    TransactionSummary,
)
from app.models.user import UserResponse
from app.services.transaction_service import TransactionService
from app.api.auth import get_current_user

router = APIRouter(prefix="/api/transactions", tags=["transactions"])


@router.post("", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    transaction_data: TransactionCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    return await TransactionService(db).create_transaction(current_user.id, transaction_data)


@router.get("", response_model=List[TransactionResponse])
async def get_transactions(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    transaction_type: Optional[str] = Query(default=None, alias="type"),
    category: Optional[str] = None,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    return await TransactionService(db).get_transactions(
        current_user.id,
        skip=skip,
        limit=limit,
        type_filter=transaction_type,
        category_filter=category,
    )


@router.get("/summary", response_model=TransactionSummary)
async def get_summary(
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
    year: int | None = Query(default=None),
    month: int | None = Query(default=None),
):
    return await TransactionService(db).get_summary(current_user.id, year=year, month=month)


@router.get("/export")
async def export_transactions(
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    csv_content = await TransactionService(db).export_to_csv(current_user.id)
    return StreamingResponse(
        BytesIO(csv_content.encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=transactions.csv"},
    )


@router.post("/import")
async def import_transactions(
    file: UploadFile = File(...),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    return await TransactionService(db).import_from_csv(current_user.id, file)


@router.post("/bulk")
async def bulk_create_transactions(
    transactions: list[TransactionCreate],
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """Accept a JSON array of transactions and create them in a single DB operation."""
    tx_dicts = [t.model_dump() for t in transactions]
    return await TransactionService(db).bulk_create_transactions(current_user.id, tx_dicts)


@router.get("/history")
async def get_monthly_history(
    months: int = Query(default=6, ge=1, le=24),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    return await TransactionService(db).get_monthly_history(str(current_user.id), months)


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    transaction = await TransactionService(db).get_transaction_by_id(current_user.id, transaction_id)
    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    return transaction


@router.put("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: str,
    transaction_data: TransactionUpdate,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    transaction = await TransactionService(db).update_transaction(
        current_user.id, transaction_id, transaction_data
    )
    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    return transaction


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    transaction_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    deleted = await TransactionService(db).delete_transaction(current_user.id, transaction_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    return None
