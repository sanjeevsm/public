from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.config import get_settings
from app.core.database import connect_to_mongo, close_mongo_connection, get_database
from app.core.limiter import limiter
from app.core.redis_client import connect_to_redis, close_redis_connection
from app.api import auth, transactions, entities, categories, budgets, users, admin
import logging
import sentry_sdk

settings = get_settings()

# Initialize Sentry if configured
if settings.SENTRY_DSN:
    sentry_sdk.init(dsn=settings.SENTRY_DSN, traces_sample_rate=0.1)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    # Connect to Redis (optional)
    await connect_to_redis()
    # Seed default categories once at startup
    from app.services.category_service import CategoryService
    db = await get_database()
    await CategoryService(db).initialize_default_categories()
    # Ensure a default superadmin exists
    from app.services.admin_service import AdminService
    await AdminService.ensure_superadmin(db)
    yield
    await close_mongo_connection()
    await close_redis_connection()


app = FastAPI(
    title="iTrack+ API",
    description="Personal Finance Tracker API",
    version="1.0.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)

app.include_router(auth.router)
app.include_router(transactions.router)
app.include_router(entities.router)
app.include_router(categories.router)
app.include_router(budgets.router)
app.include_router(users.router)
app.include_router(admin.router)


@app.get("/")
async def root():
    return {"message": "Welcome to iTrack+ API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "itrack-api"}
