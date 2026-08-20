from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi import Body
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

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

    # Batch-fetch entity names so we can display labels instead of raw IDs
    entity_ids = [u["entity_id"] for u in users if u.get("entity_id")]
    entity_map: dict[str, str] = {}
    if entity_ids:
        async for ent in db.entities.find({"_id": {"$in": entity_ids}}, {"name": 1}):
            entity_map[str(ent["_id"])] = ent["name"]

    svc = AuthService(db)
    result = []
    for u in users:
        entity_id_str = str(u["entity_id"]) if u.get("entity_id") else None
        resp = svc._to_response(u)
        resp.entity_name = entity_map.get(entity_id_str) if entity_id_str else None
        result.append(resp)
    return result


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user_admin_fields(
    user_id: str,
    payload: dict = Body(...),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """Superadmin-only: update `entity_role`, `entity_id`, and `is_superadmin` for a user."""
    _require_superadmin(current_user)

    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user id")

    patch: dict = {}
    if "entity_role" in payload:
        patch["entity_role"] = payload.get("entity_role")
    if "entity_id" in payload:
        val = payload.get("entity_id")
        patch["entity_id"] = ObjectId(val) if val and ObjectId.is_valid(val) else None
    if "is_superadmin" in payload:
        # prevent removing own superadmin flag accidentally
        if str(current_user.id) == user_id and payload.get("is_superadmin") is False:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot remove your own superadmin flag")
        # If attempting to grant superadmin, ensure there is no other superadmin
        requested = bool(payload.get("is_superadmin"))
        if requested:
            existing = await db.users.find_one({"is_superadmin": True})
            if existing and str(existing.get("_id")) != user_id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only one superadmin allowed")
        patch["is_superadmin"] = requested

    if not patch:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No updatable fields provided")

    await db.users.update_one({"_id": ObjectId(user_id)}, {"$set": patch})
    updated = await db.users.find_one({"_id": ObjectId(user_id)})
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return AuthService(db)._to_response(updated)


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """Superadmin-only: delete a user (cannot delete yourself)."""
    _require_superadmin(current_user)

    if str(current_user.id) == user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete your own account")

    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user id")

    # Prevent deleting any superadmin account
    target = await db.users.find_one({"_id": ObjectId(user_id)})
    if target and target.get("is_superadmin"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete a superadmin account")

    res = await db.users.delete_one({"_id": ObjectId(user_id)})
    if res.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {"message": "User deleted"}
