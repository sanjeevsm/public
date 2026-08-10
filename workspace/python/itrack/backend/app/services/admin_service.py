from datetime import datetime, timezone
from app.core.security import get_password_hash


class AdminService:
    @staticmethod
    async def ensure_superadmin(db):
        """Ensure a default superadmin user exists with username 'admin' and password 'admin'."""
        users = db.users
        existing = await users.find_one({"username": "admin"})
        if existing:
            # Ensure flag is set
            if not existing.get("is_superadmin"):
                await users.update_one({"_id": existing["_id"]}, {"$set": {"is_superadmin": True}})
            return

        password_hash = get_password_hash("admin")
        now = datetime.now(timezone.utc)
        user_doc = {
            "username": "admin",
            "email": "admin@example.com",
            "password_hash": password_hash,
            "is_superadmin": True,
            "created_at": now,
        }
        await users.insert_one(user_doc)
