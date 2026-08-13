import time
import re
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from prometheus_client import Counter, Histogram, Gauge

# HTTP metrics
http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status_code"],
)
http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)

# GitLab API metrics
gitlab_api_requests_total = Counter(
    "gitlab_api_requests_total",
    "Total GitLab API requests",
    ["method"],
)
gitlab_api_request_duration_seconds = Histogram(
    "gitlab_api_request_duration_seconds",
    "GitLab API request duration in seconds",
    ["path_prefix"],
    buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0],
)
gitlab_api_errors_total = Counter(
    "gitlab_api_errors_total",
    "Total GitLab API errors",
    ["path_prefix"],
)

# Cache metrics
cache_hits_total = Counter("cache_hits_total", "Total cache hits")
cache_misses_total = Counter("cache_misses_total", "Total cache misses")
cache_entries = Gauge("cache_entries", "Current number of cache entries")

# WebSocket metrics
websocket_connections_active = Gauge(
    "websocket_connections_active", "Active WebSocket connections"
)

# Business metrics
gitlab_pipelines_total = Gauge(
    "gitlab_pipelines_total", "Total pipelines by status", ["status"]
)
gitlab_projects_total = Gauge("gitlab_projects_total", "Total monitored projects")


_SKIP_PATHS = {"/metrics", "/health", "/static"}
_PATH_PARAM_RE = re.compile(r"/\d+")


def _normalize_path(path: str) -> str:
    """Replace numeric path segments with {id} to avoid high cardinality."""
    if any(path.startswith(p) for p in _SKIP_PATHS):
        return path
    return _PATH_PARAM_RE.sub("/{id}", path)


class PrometheusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = _normalize_path(request.url.path)
        if path in _SKIP_PATHS or path.startswith("/static"):
            return await call_next(request)

        start = time.perf_counter()
        response = await call_next(request)
        duration = time.perf_counter() - start

        http_requests_total.labels(
            method=request.method,
            endpoint=path,
            status_code=str(response.status_code),
        ).inc()
        http_request_duration_seconds.labels(
            method=request.method,
            endpoint=path,
        ).observe(duration)

        return response
