from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.database import get_database
from app.models.budget import BudgetCreate, BudgetUpdate, BudgetResponse, BudgetProgress
from app.models.user import UserResponse
from app.services.budget_service import BudgetService
from app.api.auth import get_current_user

router = APIRouter(prefix="/api/budgets", tags=["budgets"])


@router.post("", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
async def create_budget(
    budget_data: BudgetCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Create a new budget."""
    service = BudgetService(db)
    return await service.create_budget(
        current_user.id,
        budget_data,
        current_user.entity_id
    )


@router.get("", response_model=List[BudgetResponse])
async def get_budgets(
    active_only: bool = False,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get all budgets for the current user."""
    service = BudgetService(db)
    return await service.get_budgets(
        current_user.id,
        current_user.entity_id,
        active_only
    )


@router.get("/progress", response_model=List[BudgetProgress])
async def get_budgets_progress(
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get progress for all active budgets."""
    service = BudgetService(db)
    return await service.get_all_budgets_progress(
        current_user.id,
        current_user.entity_id
    )


@router.get("/alerts", response_model=List[BudgetProgress])
async def get_budget_alerts(
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get budgets that have exceeded alert threshold."""
    service = BudgetService(db)
    return await service.check_budget_alerts(current_user.id)


@router.get("/{budget_id}", response_model=BudgetResponse)
async def get_budget(
    budget_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get a specific budget."""
    service = BudgetService(db)
    budget = await service.get_budget(budget_id, current_user.id)
    
    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found"
        )
    
    return budget


@router.get("/{budget_id}/progress", response_model=BudgetProgress)
async def get_budget_progress(
    budget_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get progress for a specific budget."""
    service = BudgetService(db)
    progress = await service.get_budget_progress(budget_id, current_user.id)
    
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found"
        )
    
    return progress


@router.put("/{budget_id}", response_model=BudgetResponse)
async def update_budget(
    budget_id: str,
    budget_data: BudgetUpdate,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Update a budget."""
    service = BudgetService(db)
    budget = await service.update_budget(
        budget_id,
        current_user.id,
        budget_data
    )
    
    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found"
        )
    
    return budget


@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_budget(
    budget_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Delete a budget."""
    service = BudgetService(db)
    deleted = await service.delete_budget(budget_id, current_user.id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found"
        )
    
    return None
