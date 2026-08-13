"""Gitea provider client.

Gitea's REST API is broadly GitHub-compatible. We reuse GitHub's data-mapping
helpers and only override the base URL and auth header format.
"""
import httpx
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from metrics import (
    gitlab_api_request_duration_seconds as provider_api_duration,
    gitlab_api_errors_total as provider_api_errors,
)
from services.base_client import BaseProviderClient
from services.cache import get_cached, set_cached

_PROVIDER = "gitea"

_STATUS_MAP = {
    "success":   "success",
    "failure":   "failed",
    "cancelled": "canceled",
    "skipped":   "skipped",
    "waiting":   "pending",
    "running":   "running",
    "pending":   "pending",
}


class GiteaClient(BaseProviderClient):
    PROVIDER_ID = "gitea"

    def __init__(self, token: str, base_url: str = "https://gitea.com",
                 username: str = "", project_ids: str = "",
                 project_limit: int = 20, cache_ttl: int = 60):
        api_base = base_url.rstrip("/") + "/api/v1"
        super().__init__(token, api_base, username, project_ids, project_limit, cache_ttl)
        self.org = username

    @property
    def _headers(self) -> Dict[str, str]:
        return {"Authorization": f"token {self.token}"}

    async def _get(self, path: str, params: dict = None) -> Any:
        params = params or {}
        cached = get_cached(_PROVIDER, self.token, path, params, self.cache_ttl)
        if cached is not None:
            return cached
        t0 = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=30) as c:
                r = await c.get(f"{self.base_url}{path}", headers=self._headers, params=params)
                r.raise_for_status()
                data = r.json()
            set_cached(_PROVIDER, self.token, path, params, data)
            return data
        except Exception:
            provider_api_errors.labels(path_prefix=path.split("/")[1] if "/" in path else path).inc()
            raise
        finally:
            provider_api_duration.labels(path_prefix=path.split("/")[1] if "/" in path else path).observe(
                time.perf_counter() - t0
            )

    async def _get_pages(self, path: str, params: dict = None, max_items: int = 200) -> List:
        p = dict(params or {})
        p.setdefault("limit", 50)
        cache_key = f"pages:{path}:{max_items}"
        cached = get_cached(_PROVIDER, self.token, cache_key, p, self.cache_ttl)
        if cached is not None:
            return cached
        results: List = []
        page = 1
        t0 = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=30) as c:
                while len(results) < max_items:
                    p["page"] = page
                    r = await c.get(f"{self.base_url}{path}", headers=self._headers, params=p)
                    r.raise_for_status()
                    batch = r.json()
                    if not isinstance(batch, list) or not batch:
                        break
                    results.extend(batch)
                    if len(batch) < p["limit"]:
                        break
                    page += 1
        except Exception:
            provider_api_errors.labels(path_prefix=path.split("/")[1] if "/" in path else path).inc()
            raise
        finally:
            provider_api_duration.labels(path_prefix=path.split("/")[1] if "/" in path else path).observe(
                time.perf_counter() - t0
            )
        result = results[:max_items]
        set_cached(_PROVIDER, self.token, cache_key, p, result)
        return result

    # ── Repo listing ─────────────────────────────────────────────────────────

    async def get_repos(self) -> List[Dict]:
        if self.project_ids:
            repos = []
            for full_name in self.project_ids.split(","):
                full_name = full_name.strip()
                if not full_name:
                    continue
                try:
                    data = await self._get(f"/repos/{full_name}")
                    repos.append(self._norm_repo(data))
                except Exception:
                    pass
            return repos

        if self.org:
            try:
                data = await self._get_pages(
                    f"/orgs/{self.org}/repos",
                    {"sort": "newest"},
                    max_items=self.project_limit,
                )
            except Exception:
                data = await self._get_pages(
                    "/repos/search",
                    {"sort": "newest", "limit": self.project_limit},
                    max_items=self.project_limit,
                )
                if isinstance(data, dict):
                    data = data.get("data", [])
        else:
            data = await self._get_pages(
                "/repos/search",
                {"token": self.token, "sort": "newest"},
                max_items=self.project_limit,
            )
            if isinstance(data, dict):
                data = data.get("data", [])

        return [self._norm_repo(r) for r in (data if isinstance(data, list) else [])]

    def _norm_repo(self, r: dict) -> dict:
        full_name = r.get("full_name", "")
        return {
            "id":             full_name,
            "name":           r.get("name", ""),
            "full_name":      full_name,
            "url":            r.get("html_url", ""),
            "default_branch": r.get("default_branch", "main"),
            "namespace":      (r.get("owner") or {}).get("login", ""),
        }

    # ── Pipelines (Gitea Actions runs) ────────────────────────────────────────

    async def get_pipelines(self, repo_id: str, days: int = 30,
                            ref: Optional[str] = None, **kwargs) -> List[Dict]:
        params: dict = {}
        if ref:
            params["branch"] = ref
        runs = await self._get_pages(
            f"/repos/{repo_id}/actions/runs",
            params, max_items=200,
        )
        since = datetime.utcnow() - timedelta(days=days)
        result = []
        for r in (runs if isinstance(runs, list) else []):
            created = r.get("started_at") or r.get("created_at", "")
            try:
                if datetime.fromisoformat(created.replace("Z", "+00:00")).replace(tzinfo=None) < since:
                    continue
            except Exception:
                pass
            result.append(self._norm_run(r, repo_id))
        return result

    def _norm_run(self, r: dict, repo_id: str) -> dict:
        status = _STATUS_MAP.get(r.get("status", ""), r.get("status", "unknown"))
        if r.get("conclusion"):
            status = _STATUS_MAP.get(r.get("conclusion", ""), r.get("conclusion", status))
        actor = r.get("actor") or r.get("triggering_actor") or {}
        return {
            "id":        str(r.get("id", "")),
            "repo_id":   repo_id,
            "repo_name": repo_id.split("/")[-1],
            "repo_path": repo_id,
            "status":    status,
            "ref":       r.get("head_branch", ""),
            "duration":  None,
            "created_at": r.get("created_at", ""),
            "web_url":   r.get("url", ""),
            "sha":       (r.get("head_sha") or "")[:8],
            "user": {
                "name":       actor.get("login", ""),
                "avatar_url": actor.get("avatar_url", ""),
            },
        }

    async def get_pipeline_detail(self, repo_id: str, pipeline_id: str) -> dict:
        r = await self._get(f"/repos/{repo_id}/actions/runs/{pipeline_id}")
        return self._norm_run(r, repo_id)

    async def get_latest_pipeline(self, repo_id: str,
                                  ref: Optional[str] = None) -> Optional[Dict]:
        params: dict = {"limit": 1}
        if ref:
            params["branch"] = ref
        data = await self._get(f"/repos/{repo_id}/actions/runs", params)
        runs = data if isinstance(data, list) else data.get("workflow_runs", [])
        if runs:
            return self._norm_run(runs[0], repo_id)
        return None

    # ── Jobs ──────────────────────────────────────────────────────────────────

    async def get_failed_jobs(self, repo_id: str) -> List[Dict]:
        pls = await self.get_pipelines(repo_id, days=7)
        failed = [p for p in pls if p["status"] == "failed"][:5]
        jobs: List[Dict] = []
        for pl in failed:
            try:
                data = await self._get(f"/repos/{repo_id}/actions/runs/{pl['id']}/jobs")
                for j in (data.get("jobs") if isinstance(data, dict) else []):
                    if j.get("conclusion") in ("failure", "cancelled"):
                        jobs.append(self._norm_job(j, repo_id))
            except Exception:
                pass
        return jobs

    async def get_all_jobs(self, repo_id: str) -> List[Dict]:
        pls = await self.get_pipelines(repo_id, days=7)
        jobs: List[Dict] = []
        for pl in pls[:5]:
            try:
                data = await self._get(f"/repos/{repo_id}/actions/runs/{pl['id']}/jobs")
                for j in (data.get("jobs") if isinstance(data, dict) else []):
                    jobs.append(self._norm_job(j, repo_id))
            except Exception:
                pass
        return jobs

    def _norm_job(self, j: dict, repo_id: str) -> dict:
        status = _STATUS_MAP.get(j.get("status", ""), j.get("status", "unknown"))
        if j.get("conclusion"):
            status = _STATUS_MAP.get(j.get("conclusion", ""), j.get("conclusion", status))
        return {
            "id":        str(j.get("id", "")),
            "name":      j.get("name", ""),
            "stage":     j.get("name", ""),
            "status":    status,
            "repo_name": repo_id.split("/")[-1],
            "duration":  None,
            "created_at": j.get("started_at", ""),
            "web_url":   j.get("html_url", ""),
            "ref":       "",
        }

    # ── Pull Requests ─────────────────────────────────────────────────────────

    async def get_pull_requests(self, repo_id: str, days: int = 30,
                                state: str = "all", **kwargs) -> List[Dict]:
        gt_state = "closed" if state == "merged" else ("open" if state == "opened" else "")
        params: dict = {"sort": "newest", "state": gt_state or "open"}
        prs = await self._get_pages(f"/repos/{repo_id}/pulls", params, max_items=100)
        if state == "all" or state == "closed":
            closed = await self._get_pages(
                f"/repos/{repo_id}/pulls", {"state": "closed", "sort": "newest"}, max_items=100
            )
            prs = prs + closed

        since = datetime.utcnow() - timedelta(days=days)
        result = []
        seen = set()
        for p in prs:
            pid = str(p.get("number", p.get("id", "")))
            if pid in seen:
                continue
            seen.add(pid)
            updated = p.get("updated_at", "")
            try:
                if datetime.fromisoformat(updated.replace("Z", "+00:00")).replace(tzinfo=None) < since:
                    continue
            except Exception:
                pass
            result.append(self._norm_pr(p, repo_id))
        return result

    def _norm_pr(self, p: dict, repo_id: str) -> dict:
        user = p.get("user") or {}
        state = "opened"
        if p.get("merged"):
            state = "merged"
        elif p.get("state") == "closed":
            state = "closed"
        return {
            "id":            str(p.get("number", p.get("id", ""))),
            "repo_name":     repo_id.split("/")[-1],
            "repo_path":     repo_id,
            "title":         p.get("title", ""),
            "author":        user.get("login", ""),
            "author_name":   user.get("login", ""),
            "state":         state,
            "source_branch": (p.get("head") or {}).get("ref", ""),
            "target_branch": (p.get("base") or {}).get("ref", ""),
            "created_at":    p.get("created_at", ""),
            "updated_at":    p.get("updated_at", ""),
            "merged_at":     p.get("merged_at"),
            "closed_at":     p.get("closed_at"),
            "web_url":       p.get("html_url", ""),
        }

    # ── Deployments ───────────────────────────────────────────────────────────

    async def get_deployments(self, repo_id: str, days: int = 30, **kwargs) -> List[Dict]:
        # Gitea does not have a native deployments API; return empty list
        return []

    # ── Branches ─────────────────────────────────────────────────────────────

    async def get_branch(self, repo_id: str, branch_name: str) -> dict:
        b = await self._get(f"/repos/{repo_id}/branches/{branch_name}")
        commit = b.get("commit") or {}
        author = (commit.get("commit") or {}).get("author") or {}
        return {
            "name":          b.get("name", ""),
            "protected":     b.get("protected", False),
            "commit_sha":    (commit.get("id") or commit.get("sha") or "")[:8],
            "commit_title":  ((commit.get("commit") or {}).get("message") or "")[:80],
            "commit_author": author.get("name", ""),
            "committed_at":  author.get("date", ""),
        }

    # ── Labels ───────────────────────────────────────────────────────────────

    @property
    def pr_label(self) -> str:
        return "Pull Requests"

    @property
    def pipeline_label(self) -> str:
        return "Actions"
