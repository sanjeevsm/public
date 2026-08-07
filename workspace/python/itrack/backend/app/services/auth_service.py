from datetime import timedelta, datetime, timezone
from typing import Optional
from fastapi import HTTPException, status
from bson import ObjectId
from pymongo.errors import DuplicateKeyError
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.config import get_settings
from app.models.user import UserCreate, UserInDB, UserResponse, Token

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
        return UserResponse(
            id=str(created_user["_id"]),
            username=created_user["username"],
            email=created_user["email"],
            entity_id=str(created_user["entity_id"]) if created_user.get("entity_id") else None,
            entity_role=created_user.get("entity_role"),
            created_at=created_user["created_at"],
        )

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
        if not user:
            return None
        return UserResponse(
            id=str(user["_id"]),
            username=user["username"],
            email=user["email"],
            entity_id=str(user["entity_id"]) if user.get("entity_id") else None,
            entity_role=user.get("entity_role"),
            created_at=user["created_at"],
        )

    def create_user_token(self, user_id: str) -> Token:
        access_token = create_access_token(
            data={"sub": user_id},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        return Token(access_token=access_token, token_type="bearer")
