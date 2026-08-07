from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.database import get_database
from app.models.category import CategoryCreate, CategoryUpdate, CategoryResponse
from app.models.user import UserResponse
from app.services.category_service import CategoryService
from app.api.auth import get_current_user

router = APIRouter(prefix="/api/categories", tags=["categories"])


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: CategoryCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    service = CategoryService(db)
    try:
        return await service.create_category(current_user.id, category_data, current_user.entity_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("", response_model=List[CategoryResponse])
async def get_categories(
    type_filter: Optional[str] = Query(None, alias="type"),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    service = CategoryService(db)
    return await service.get_categories(
        current_user.id,
        type_filter=type_filter,
        entity_id=current_user.entity_id,
    )


@router.get("/stats")
async def get_category_stats(
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    return await CategoryService(db).get_category_usage_stats(current_user.id)


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    category = await CategoryService(db).get_category(category_id, current_user.id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return category


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: str,
    category_data: CategoryUpdate,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    service = CategoryService(db)
    try:
        category = await service.update_category(category_id, current_user.id, category_data)
        if not category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
        return category
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    service = CategoryService(db)
    try:
        deleted = await service.delete_category(category_id, current_user.id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
        return None
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
