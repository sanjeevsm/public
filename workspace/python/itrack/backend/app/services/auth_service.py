from datetime import timedelta, datetime, timezone
from typing import Optional
from fastapi import HTTPException, status
from bson import ObjectId
from pymongo.errors import DuplicateKeyError
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.config import get_settings
from app.models.user import UserCreate, UserInDB, UserResponse, Token, UserUpdate, AdminUserUpdate

settings = get_settings()


class AuthService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.users

    async def register_user(self, user_data: UserCreate) -> UserResponse:
        user_dict = user_data.model_dump()
        user_dict["password_hash"] = get_password_hash(user_dict.pop("password"))
        user_dict["created_at"] = datetime.now(timezone.utc)

        try:
            result = await self.collection.insert_one(user_dict)
        except DuplicateKeyError as exc:
            detail = "Email already registered"
            if "username" in str(exc):
                detail = "Username already taken"
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

        created_user = await self.collection.find_one({"_id": result.inserted_id})
        return self._to_response(created_user)

    async def authenticate_user(self, email: str, password: str) -> Optional[UserInDB]:
        user = await self.collection.find_one({"email": email})
        if not user:
            return None
        if not verify_password(password, user["password_hash"]):
            return None
        user["_id"] = str(user["_id"])
        if user.get("entity_id"):
            user["entity_id"] = str(user["entity_id"])
        return UserInDB(**user)

    async def get_user_by_id(self, user_id: str) -> Optional[UserResponse]:
        if not ObjectId.is_valid(user_id):
            return None
        user = await self.collection.find_one({"_id": ObjectId(user_id)})
        return self._to_response(user) if user else None

    def create_user_token(self, user_id: str) -> Token:
        access_token = create_access_token(
            data={"sub": user_id},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        return Token(access_token=access_token, token_type="bearer")

    async def update_user(self, user_id: str, update_data: UserUpdate) -> UserResponse:
        """Update the current user's own profile."""
        user = await self.collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        # Password change requires current_password verification
        if update_data.new_password:
            if not update_data.current_password:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="current_password is required to set a new password",
                )
            if not verify_password(update_data.current_password, user["password_hash"]):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Current password is incorrect",
                )

        patch: dict = {}
        if update_data.username is not None:
            patch["username"] = update_data.username
        if update_data.email is not None:
            patch["email"] = update_data.email
        if update_data.new_password:
            patch["password_hash"] = get_password_hash(update_data.new_password)

        if not patch:
            return self._to_response(user)

        try:
            await self.collection.update_one({"_id": ObjectId(user_id)}, {"$set": patch})
        except DuplicateKeyError as exc:
            detail = "Email already in use"
            if "username" in str(exc):
                detail = "Username already taken"
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

        updated = await self.collection.find_one({"_id": ObjectId(user_id)})
        return self._to_response(updated)

    async def admin_update_user(
        self, admin_id: str, target_user_id: str, update_data: AdminUserUpdate
    ) -> UserResponse:
        """Allow an entity admin to update username/email of a member in their entity."""
        # Verify admin exists and has an entity
        admin = await self.collection.find_one({"_id": ObjectId(admin_id)})
        if not admin or admin.get("entity_role") != "admin" or not admin.get("entity_id"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only entity admins can update member profiles",
            )

        # Verify target belongs to the same entity
        target = await self.collection.find_one({"_id": ObjectId(target_user_id)})
        if not target:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        if str(target.get("entity_id", "")) != str(admin["entity_id"]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not belong to your entity",
            )

        patch: dict = {}
        if update_data.username is not None:
            patch["username"] = update_data.username
        if update_data.email is not None:
            patch["email"] = update_data.email

        if not patch:
            return self._to_response(target)

        try:
            await self.collection.update_one({"_id": ObjectId(target_user_id)}, {"$set": patch})
        except DuplicateKeyError as exc:
            detail = "Email already in use"
            if "username" in str(exc):
                detail = "Username already taken"
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

        updated = await self.collection.find_one({"_id": ObjectId(target_user_id)})
        return self._to_response(updated)

    async def get_entity_members_profiles(self, admin_id: str) -> list[UserResponse]:
        """Return full profiles of all members in the admin's entity."""
        admin = await self.collection.find_one({"_id": ObjectId(admin_id)})
        if not admin or not admin.get("entity_id"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You must be an entity admin to view member profiles",
            )
        if admin.get("entity_role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only entity admins can view all member profiles",
            )
        members = await self.collection.find(
            {"entity_id": admin["entity_id"]}
        ).to_list(length=200)
        return [self._to_response(m) for m in members]

    def _to_response(self, user: dict) -> UserResponse:
        return UserResponse(
            id=str(user["_id"]),
            username=user["username"],
            email=user["email"],
            entity_id=str(user["entity_id"]) if user.get("entity_id") else None,
            entity_role=user.get("entity_role"),
            created_at=user["created_at"],
        )
