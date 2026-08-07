from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.config import get_settings
from app.core.database import connect_to_mongo, close_mongo_connection, get_database
from app.core.limiter import limiter
from app.api import auth, transactions, entities, categories, budgets

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    # Seed default categories once at startup
    from app.services.category_service import CategoryService
    db = await get_database()
    await CategoryService(db).initialize_default_categories()
    yield
    await close_mongo_connection()


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
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)

app.include_router(auth.router)
app.include_router(transactions.router)
app.include_router(entities.router)
app.include_router(categories.router)
app.include_router(budgets.router)


@app.get("/")
async def root():
    return {"message": "Welcome to iTrack+ API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "itrack-api"}
