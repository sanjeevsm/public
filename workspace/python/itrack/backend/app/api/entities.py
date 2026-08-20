from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.database import get_database
from app.models.entity import (
    EntityCreate,
    EntityUpdate,
    EntityResponse,
    EntityMemberResponse,
    EntitySummary,
    EntityInviteRequest,
    MemberRole,
)
from app.models.user import UserResponse
from app.services.entity_service import EntityService
from app.api.auth import get_current_user

router = APIRouter(prefix="/api/entities", tags=["entities"])


@router.post("", response_model=EntityResponse, status_code=status.HTTP_201_CREATED)
async def create_entity(
    entity_data: EntityCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    service = EntityService(db)
    if await service.get_user_entity(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already belong to an entity. Leave it first to create a new one.",
        )
    return await service.create_entity(current_user.id, entity_data)


@router.get("/my-entity", response_model=EntityResponse)
async def get_my_entity(
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    entity = await EntityService(db).get_user_entity(current_user.id)
    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="You are not part of any entity"
        )
    return entity


@router.get("/{entity_id}", response_model=EntityResponse)
async def get_entity(
    entity_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    service = EntityService(db)
    entity = await service.get_entity(entity_id)
    if not entity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entity not found")
    if not await service.is_member(entity_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this entity",
        )
    return entity


@router.put("/{entity_id}", response_model=EntityResponse)
async def update_entity(
    entity_id: str,
    entity_data: EntityUpdate,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    entity = await EntityService(db).update_entity(entity_id, current_user.id, entity_data)
    if not entity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entity not found")
    return entity


@router.delete("/{entity_id}", response_model=dict)
async def delete_entity(
    entity_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """Delete entity (admin only). Detaches all members and their transactions."""
    deleted = await EntityService(db).delete_entity(entity_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entity not found")
    return {"message": "Entity deleted successfully"}


@router.post("/{entity_id}/invite", response_model=dict)
async def invite_member(
    entity_id: str,
    invite_data: EntityInviteRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    await EntityService(db).invite_member(
        entity_id, current_user.id, invite_data.user_email, invite_data.role
    )
    return {"message": "User invited successfully"}


@router.post("/leave", response_model=dict)
async def leave_entity(
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    await EntityService(db).leave_entity(current_user.id)
    return {"message": "Left entity successfully"}


@router.delete("/{entity_id}/members/{member_id}", response_model=dict)
async def remove_member(
    entity_id: str,
    member_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    await EntityService(db).remove_member(entity_id, current_user.id, member_id)
    return {"message": "Member removed successfully"}


@router.put("/{entity_id}/members/{member_id}/role", response_model=dict)
async def change_member_role(
    entity_id: str,
    member_id: str,
    role: MemberRole,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    await EntityService(db).change_member_role(entity_id, current_user.id, member_id, role)
    return {"message": "Member role updated successfully"}


@router.get("/{entity_id}/members", response_model=List[EntityMemberResponse])
async def get_entity_members(
    entity_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    return await EntityService(db).get_entity_members(entity_id, current_user.id)


@router.get("/{entity_id}/summary", response_model=EntitySummary)
async def get_entity_summary(
    entity_id: str,
    include_private: bool = False,
    month: Optional[int] = Query(default=None, ge=1, le=12),
    year: Optional[int] = Query(default=None, ge=2000, le=2100),
    currency: Optional[str] = Query(default=None),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    return await EntityService(db).get_entity_summary(
        entity_id, current_user.id, include_private, month=month, year=year, currency=currency
    )


@router.get("/{entity_id}/recurring-transactions")
async def get_entity_recurring_transactions(
    entity_id: str,
    include_private: bool = False,
    currency: Optional[str] = Query(default=None),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    return await EntityService(db).get_entity_recurring_transactions(
        entity_id, current_user.id, include_private, currency=currency
    )


@router.get("/{entity_id}/history")
async def get_entity_monthly_history(
    entity_id: str,
    months: int = Query(default=6, ge=1, le=24),
    include_private: bool = False,
    currency: Optional[str] = Query(default=None),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    return await EntityService(db).get_entity_monthly_history(
        entity_id, current_user.id, months, include_private, currency=currency
    )
