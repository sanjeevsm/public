import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from config import get_settings
from metrics import PrometheusMiddleware
from routers import overview, pipelines, jobs, mergerequests, deployments, export, ws, branches

settings = get_settings()
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs(settings.export_dir, exist_ok=True)
    logger.info("CI/CD Dashboard starting on port %s", settings.app_port)
    yield
    logger.info("CI/CD Dashboard shutting down")


app = FastAPI(
    title="CI/CD Dashboard",
    description="Real-time CI/CD metrics dashboard — GitLab, GitHub, Bitbucket, Gitea",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)

app.add_middleware(PrometheusMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.include_router(overview.router, prefix="/api")
app.include_router(pipelines.router, prefix="/api")
app.include_router(jobs.router, prefix="/api")
app.include_router(mergerequests.router, prefix="/api")
app.include_router(deployments.router, prefix="/api")
app.include_router(export.router, prefix="/api")
app.include_router(branches.router, prefix="/api")
app.include_router(ws.router)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled error on %s: %s", request.url, exc)
    return JSONResponse(status_code=500, content={"error": str(exc)})


@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "cicd-dashboard", "version": "2.0.0"}


@app.get("/api/config")
async def api_config():
    s = get_settings()
    return {
        "providers": ["gitlab", "github", "bitbucket", "gitea"],
        "cache_ttl": s.cache_ttl,
    }


_STATIC_DIR = Path(__file__).parent / "static"


@app.get("/")
async def serve_index():
    return FileResponse(str(_STATIC_DIR / "index.html"))


app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")
