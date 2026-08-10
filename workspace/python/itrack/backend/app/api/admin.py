from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.database import get_database
from app.api.auth import get_current_user
from app.models.user import UserResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/api/admin", tags=["admin"])


def _require_superadmin(user: UserResponse):
    if not getattr(user, "is_superadmin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superadmin privileges required",
        )


@router.get("/users", response_model=List[UserResponse])
async def list_users(
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    _require_superadmin(current_user)
    users = await db.users.find().to_list(length=1000)
    return [AuthService(db)._to_response(u) for u in users]
