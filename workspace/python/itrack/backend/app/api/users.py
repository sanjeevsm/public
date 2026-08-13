from typing import List
from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.database import get_database
from app.models.user import UserResponse, AdminUserUpdate
from app.services.auth_service import AuthService
from app.api.auth import get_current_user

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/entity-members", response_model=List[UserResponse])
async def get_entity_members_profiles(
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """Return full profiles of all members in the admin's entity (admin only)."""
    return await AuthService(db).get_entity_members_profiles(current_user.id)


@router.put("/{user_id}", response_model=UserResponse)
async def admin_update_user(
    user_id: str,
    update_data: AdminUserUpdate,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """Allow an entity admin to update a member's username or email (admin only)."""
    return await AuthService(db).admin_update_user(current_user.id, user_id, update_data)
