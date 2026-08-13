import httpx
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from metrics import (
    gitlab_api_requests_total,
    gitlab_api_request_duration_seconds,
    gitlab_api_errors_total,
)
from services.base_client import BaseProviderClient
from services.cache import get_cached, set_cached

_PROVIDER = "gitlab"


class GitLabClient(BaseProviderClient):
    PROVIDER_ID = "gitlab"

    def __init__(self, token: str, base_url: str = "https://gitlab.com",
                 username: str = "", project_ids: str = "",
                 project_limit: int = 20, cache_ttl: int = 60):
        super().__init__(token, base_url, username, project_ids, project_limit, cache_ttl)
        self._api = self.base_url + "/api/v4"

    @property
    def _headers(self) -> Dict[str, str]:
        return {"PRIVATE-TOKEN": self.token}

    async def _get(self, path: str, params: dict = None) -> Any:
        params = params or {}
        cached = get_cached(_PROVIDER, self.token, path, params, self.cache_ttl)
        if cached is not None:
            return cached

        prefix = "/" + path.lstrip("/").split("/")[1] if path.count("/") > 1 else path
        gitlab_api_requests_total.labels(method="get").inc()
        t0 = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=30) as c:
                r = await c.get(f"{self._api}{path}", headers=self._headers, params=params)
                r.raise_for_status()
                data = r.json()
            set_cached(_PROVIDER, self.token, path, params, data)
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
        cache_key = f"all:{path}:{max_items}"
        cached = get_cached(_PROVIDER, self.token, cache_key, p, self.cache_ttl)
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
                    r = await c.get(f"{self._api}{path}", headers=self._headers, params=p)
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
        set_cached(_PROVIDER, self.token, cache_key, p, result)
        return result

    # ── Repo listing ─────────────────────────────────────────────────────────

    async def get_repos(self) -> List[Dict]:
        if self.project_ids:
            ids = [i.strip() for i in self.project_ids.split(",") if i.strip()]
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
            max_items=self.project_limit,
        )

    def _repo_id(self, repo: dict) -> str:
        return str(repo.get("id", ""))

    # ── Pipelines ─────────────────────────────────────────────────────────────

    async def get_pipelines(self, repo_id: str, days: int = 30,
                            ref: Optional[str] = None, **kwargs) -> List[Dict]:
        since = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
        params = {"updated_after": since}
        if ref:
            params["ref"] = ref
        params.update(kwargs)
        return await self._get_all(f"/projects/{repo_id}/pipelines", params, max_items=200)

    async def get_pipeline_detail(self, repo_id: str, pipeline_id: str) -> dict:
        return await self._get(f"/projects/{repo_id}/pipelines/{pipeline_id}")

    async def get_latest_pipeline(self, repo_id: str,
                                  ref: Optional[str] = None) -> Optional[Dict]:
        params = {"per_page": 1, "order_by": "id", "sort": "desc"}
        if ref:
            params["ref"] = ref
        result = await self._get(f"/projects/{repo_id}/pipelines", params)
        if isinstance(result, list) and result:
            return result[0]
        return None

    # ── Jobs ──────────────────────────────────────────────────────────────────

    async def get_failed_jobs(self, repo_id: str) -> List[Dict]:
        return await self._get_all(f"/projects/{repo_id}/jobs",
                                   {"scope": "failed"}, max_items=100)

    async def get_all_jobs(self, repo_id: str) -> List[Dict]:
        return await self._get_all(f"/projects/{repo_id}/jobs", max_items=100)

    # ── Pull / Merge Requests ─────────────────────────────────────────────────

    async def get_pull_requests(self, repo_id: str, days: int = 30,
                                state: str = "all", **kwargs) -> List[Dict]:
        since = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
        params = {"updated_after": since, **kwargs}
        if state != "all":
            params["state"] = state
        return await self._get_all(f"/projects/{repo_id}/merge_requests",
                                   params, max_items=100)

    # ── Deployments ───────────────────────────────────────────────────────────

    async def get_deployments(self, repo_id: str, days: int = 30, **kwargs) -> List[Dict]:
        return await self._get_all(f"/projects/{repo_id}/deployments",
                                   {"order_by": "updated_at", "sort": "desc", **kwargs},
                                   max_items=50)

    # ── Branches ─────────────────────────────────────────────────────────────

    async def get_branch(self, repo_id: str, branch_name: str) -> dict:
        return await self._get(f"/projects/{repo_id}/repository/branches/{branch_name}")

    # ── Labels ───────────────────────────────────────────────────────────────

    @property
    def pr_label(self) -> str:
        return "Merge Requests"

    @property
    def pipeline_label(self) -> str:
        return "Pipelines"
