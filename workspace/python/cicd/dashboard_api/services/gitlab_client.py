import httpx
import json
import time
from typing import Any, Dict, List, Optional
from config import get_settings
from metrics import (
    gitlab_api_requests_total,
    gitlab_api_request_duration_seconds,
    gitlab_api_errors_total,
    cache_hits_total,
    cache_misses_total,
    cache_entries,
)

_cache: Dict[str, tuple] = {}


def _cache_key(path: str, params: dict) -> str:
    return f"{path}:{json.dumps(sorted((params or {}).items()))}"


def _get_cached(key: str, ttl: int) -> Optional[Any]:
    if key in _cache:
        data, ts = _cache[key]
        if time.time() - ts < ttl:
            cache_hits_total.inc()
            return data
    cache_misses_total.inc()
    return None


def _set_cached(key: str, data: Any):
    _cache[key] = (data, time.time())
    cache_entries.set(len(_cache))


class GitLabClient:
    def __init__(self):
        s = get_settings()
        self.base = s.gitlab_url.rstrip("/") + "/api/v4"
        self.token = s.gitlab_token
        self.ttl = s.cache_ttl

    @property
    def _headers(self) -> Dict[str, str]:
        return {"PRIVATE-TOKEN": self.token}

    async def _get(self, path: str, params: dict = None) -> Any:
        key = _cache_key(path, params)
        cached = _get_cached(key, self.ttl)
        if cached is not None:
            return cached
        prefix = "/" + path.lstrip("/").split("/")[1] if path.count("/") > 1 else path
        gitlab_api_requests_total.labels(method="get").inc()
        t0 = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=30) as c:
                r = await c.get(f"{self.base}{path}", headers=self._headers, params=params or {})
                r.raise_for_status()
                data = r.json()
            _set_cached(key, data)
            return data
        except Exception:
            gitlab_api_errors_total.labels(path_prefix=prefix).inc()
            raise
        finally:
            gitlab_api_request_duration_seconds.labels(path_prefix=prefix).observe(
                time.perf_counter() - t0
            )

    async def _get_all(self, path: str, params: dict = None, max_items: int = 200) -> List:
        p = dict(params or {})
        p["per_page"] = 100
        key = _cache_key(f"all:{path}:{max_items}", p)
        cached = _get_cached(key, self.ttl)
        if cached is not None:
            return cached

        prefix = "/" + path.lstrip("/").split("/")[1] if path.count("/") > 1 else path
        gitlab_api_requests_total.labels(method="get_all").inc()
        t0 = time.perf_counter()
        results: List = []
        page = 1
        try:
            async with httpx.AsyncClient(timeout=30) as c:
                while len(results) < max_items:
                    p["page"] = page
                    r = await c.get(f"{self.base}{path}", headers=self._headers, params=p)
                    r.raise_for_status()
                    batch = r.json()
                    if not batch:
                        break
                    results.extend(batch)
                    total_pages = int(r.headers.get("X-Total-Pages", 1))
                    if page >= total_pages:
                        break
                    page += 1
        except Exception:
            gitlab_api_errors_total.labels(path_prefix=prefix).inc()
            raise
        finally:
            gitlab_api_request_duration_seconds.labels(path_prefix=prefix).observe(
                time.perf_counter() - t0
            )

        result = results[:max_items]
        _set_cached(key, result)
        return result

    async def get_projects(self) -> List[Dict]:
        s = get_settings()
        if s.gitlab_project_ids:
            ids = [i.strip() for i in s.gitlab_project_ids.split(",") if i.strip()]
            out = []
            for pid in ids:
                try:
                    out.append(await self._get(f"/projects/{pid}"))
                except Exception:
                    pass
            return out
        return await self._get_all(
            "/projects",
            {"membership": True, "order_by": "last_activity_at", "sort": "desc"},
            max_items=s.gitlab_project_limit,
        )

    async def get_pipelines(self, project_id: int, **params) -> List[Dict]:
        return await self._get_all(f"/projects/{project_id}/pipelines", params, max_items=200)

    async def get_jobs(self, project_id: int, **params) -> List[Dict]:
        return await self._get_all(f"/projects/{project_id}/jobs", params, max_items=100)

    async def get_merge_requests(self, project_id: int, **params) -> List[Dict]:
        return await self._get_all(f"/projects/{project_id}/merge_requests", params, max_items=100)

    async def get_deployments(self, project_id: int, **params) -> List[Dict]:
        return await self._get_all(f"/projects/{project_id}/deployments", params, max_items=50)

    async def get_pipeline(self, project_id: int, pipeline_id: int) -> Dict:
        return await self._get(f"/projects/{project_id}/pipelines/{pipeline_id}")

    async def get_branch(self, project_id: int, branch: str) -> Dict:
        return await self._get(f"/projects/{project_id}/repository/branches/{branch}")

    async def get_latest_pipeline(self, project_id: int, ref: str = None) -> Optional[Dict]:
        params = {"per_page": 1, "order_by": "id", "sort": "desc"}
        if ref:
            params["ref"] = ref
        result = await self._get(f"/projects/{project_id}/pipelines", params)
        if isinstance(result, list) and result:
            return result[0]
        return None
