import httpx
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from metrics import (
    gitlab_api_requests_total as provider_api_requests_total,
    gitlab_api_request_duration_seconds as provider_api_duration,
    gitlab_api_errors_total as provider_api_errors,
)
from services.base_client import BaseProviderClient
from services.cache import get_cached, set_cached

_PROVIDER = "github"

# GitHub run conclusion → normalized status
_STATUS_MAP = {
    "success":   "success",
    "failure":   "failed",
    "cancelled": "canceled",
    "skipped":   "skipped",
    "timed_out": "failed",
    "action_required": "pending",
    "neutral":   "skipped",
    "stale":     "skipped",
}

# PR state mapping
_PR_STATE = {"open": "opened", "closed": "closed", "merged": "merged"}


def _run_status(run: dict) -> str:
    if run.get("status") in ("in_progress", "queued", "waiting", "requested"):
        return "running" if run["status"] == "in_progress" else "pending"
    conclusion = run.get("conclusion") or ""
    return _STATUS_MAP.get(conclusion, "unknown")


def _run_duration(run: dict) -> Optional[float]:
    try:
        start = datetime.fromisoformat(run["run_started_at"].replace("Z", "+00:00"))
        end = datetime.fromisoformat(run["updated_at"].replace("Z", "+00:00"))
        return max(0.0, (end - start).total_seconds())
    except Exception:
        return None


class GitHubClient(BaseProviderClient):
    PROVIDER_ID = "github"

    def __init__(self, token: str, base_url: str = "https://api.github.com",
                 username: str = "", project_ids: str = "",
                 project_limit: int = 20, cache_ttl: int = 60):
        # base_url may be a custom GitHub Enterprise URL; we always append /api/v3 for GHE
        if "api.github.com" in base_url or base_url.rstrip("/") == "https://github.com":
            api_base = "https://api.github.com"
        else:
            api_base = base_url.rstrip("/") + "/api/v3"
        super().__init__(token, api_base, username, project_ids, project_limit, cache_ttl)

    @property
    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

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

    async def _get_pages(self, path: str, params: dict = None,
                         max_items: int = 200, list_key: str = None) -> List:
        """Paginate through GitHub list endpoints (per_page, page)."""
        p = dict(params or {})
        p.setdefault("per_page", 100)
        cache_key = f"pages:{path}:{max_items}:{list_key}"
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
                    raw = r.json()
                    batch = raw[list_key] if list_key and isinstance(raw, dict) else raw
                    if not batch:
                        break
                    results.extend(batch)
                    if len(batch) < p["per_page"]:
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

    def _repo_full_name(self, repo_id: str) -> str:
        """repo_id may be numeric (GitHub ID) or 'owner/repo' full name."""
        return repo_id  # callers always pass full_name

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

        if self.username:
            # username may be an org or a user
            try:
                data = await self._get_pages(
                    f"/orgs/{self.username}/repos",
                    {"type": "all", "sort": "updated"},
                    max_items=self.project_limit,
                )
            except Exception:
                data = await self._get_pages(
                    f"/users/{self.username}/repos",
                    {"sort": "updated"},
                    max_items=self.project_limit,
                )
        else:
            data = await self._get_pages(
                "/user/repos",
                {"sort": "updated", "affiliation": "owner,collaborator,organization_member"},
                max_items=self.project_limit,
            )
        return [self._norm_repo(r) for r in data]

    def _norm_repo(self, r: dict) -> dict:
        return {
            "id":             r.get("full_name", str(r.get("id", ""))),
            "name":           r.get("name", ""),
            "full_name":      r.get("full_name", ""),
            "url":            r.get("html_url", ""),
            "default_branch": r.get("default_branch", "main"),
            "namespace":      (r.get("owner") or {}).get("login", ""),
        }

    # ── Pipelines (Actions workflow runs) ─────────────────────────────────────

    async def get_pipelines(self, repo_id: str, days: int = 30,
                            ref: Optional[str] = None, **kwargs) -> List[Dict]:
        since = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
        params = {"created": f">={since}"}
        if ref:
            params["branch"] = ref
        runs = await self._get_pages(
            f"/repos/{repo_id}/actions/runs",
            params, max_items=200, list_key="workflow_runs",
        )
        return [self._norm_run(r, repo_id) for r in runs]

    def _norm_run(self, r: dict, repo_id: str) -> dict:
        actor = r.get("actor") or {}
        return {
            "id":        str(r.get("id", "")),
            "repo_id":   repo_id,
            "repo_name": r.get("repository", {}).get("name", repo_id.split("/")[-1]),
            "repo_path": repo_id,
            "status":    _run_status(r),
            "ref":       r.get("head_branch", ""),
            "duration":  _run_duration(r),
            "created_at": r.get("created_at", ""),
            "web_url":   r.get("html_url", ""),
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
        params: dict = {"per_page": 1}
        if ref:
            params["branch"] = ref
        data = await self._get(f"/repos/{repo_id}/actions/runs", params)
        runs = data.get("workflow_runs", []) if isinstance(data, dict) else []
        if runs:
            return self._norm_run(runs[0], repo_id)
        return None

    # ── Jobs ──────────────────────────────────────────────────────────────────

    async def _jobs_for_run(self, repo_id: str, run_id: str) -> List[Dict]:
        jobs = await self._get_pages(
            f"/repos/{repo_id}/actions/runs/{run_id}/jobs",
            max_items=50, list_key="jobs",
        )
        return [self._norm_job(j, repo_id) for j in jobs]

    def _norm_job(self, j: dict, repo_id: str) -> dict:
        status = _STATUS_MAP.get(j.get("conclusion") or "", "")
        if not status:
            status = "running" if j.get("status") == "in_progress" else "pending"
        return {
            "id":        str(j.get("id", "")),
            "name":      j.get("name", ""),
            "stage":     j.get("name", ""),   # GitHub has no stages; use job name
            "status":    status,
            "repo_name": repo_id.split("/")[-1],
            "duration":  None,
            "created_at": j.get("started_at", ""),
            "web_url":   j.get("html_url", ""),
            "ref":       "",
        }

    async def get_failed_jobs(self, repo_id: str) -> List[Dict]:
        # Get failed runs and fetch their jobs
        runs = await self._get_pages(
            f"/repos/{repo_id}/actions/runs",
            {"status": "failure", "per_page": 10},
            max_items=10, list_key="workflow_runs",
        )
        jobs: List[Dict] = []
        for run in runs[:5]:
            try:
                jobs.extend(await self._jobs_for_run(repo_id, str(run["id"])))
            except Exception:
                pass
        return [j for j in jobs if j["status"] == "failed"]

    async def get_all_jobs(self, repo_id: str) -> List[Dict]:
        runs = await self._get_pages(
            f"/repos/{repo_id}/actions/runs",
            {"per_page": 10},
            max_items=10, list_key="workflow_runs",
        )
        jobs: List[Dict] = []
        for run in runs[:5]:
            try:
                jobs.extend(await self._jobs_for_run(repo_id, str(run["id"])))
            except Exception:
                pass
        return jobs

    # ── Pull Requests ─────────────────────────────────────────────────────────

    async def get_pull_requests(self, repo_id: str, days: int = 30,
                                state: str = "all", **kwargs) -> List[Dict]:
        # "all" → fetch open + closed (GitHub doesn't support "all" directly)
        gh_state = "closed" if state == "merged" else ("open" if state == "opened" else "all")
        prs = await self._get_pages(
            f"/repos/{repo_id}/pulls",
            {"state": gh_state, "sort": "updated", "direction": "desc", **kwargs},
            max_items=100,
        )
        since = datetime.utcnow() - timedelta(days=days)
        result = []
        for p in prs:
            updated = p.get("updated_at", "")
            try:
                if datetime.fromisoformat(updated.replace("Z", "+00:00")).replace(tzinfo=None) < since:
                    continue
            except Exception:
                pass
            result.append(self._norm_pr(p, repo_id))
        return result

    def _norm_pr(self, p: dict, repo_id: str) -> dict:
        raw_state = p.get("state", "open")
        if p.get("merged_at"):
            state = "merged"
        elif raw_state == "closed":
            state = "closed"
        else:
            state = "opened"
        author = p.get("user") or {}
        return {
            "id":            str(p.get("number", "")),
            "repo_name":     repo_id.split("/")[-1],
            "repo_path":     repo_id,
            "title":         p.get("title", ""),
            "author":        author.get("login", ""),
            "author_name":   author.get("login", ""),
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
        deps = await self._get_pages(
            f"/repos/{repo_id}/deployments",
            max_items=50,
        )
        since = datetime.utcnow() - timedelta(days=days)
        result = []
        for d in deps:
            created = d.get("created_at", "")
            try:
                if datetime.fromisoformat(created.replace("Z", "+00:00")).replace(tzinfo=None) < since:
                    continue
            except Exception:
                pass
            creator = d.get("creator") or {}
            result.append({
                "id":                  str(d.get("id", "")),
                "repo_name":           repo_id.split("/")[-1],
                "repo_path":           repo_id,
                "environment":         d.get("environment", ""),
                "status":              "success",   # GitHub deployments need a separate status API
                "ref":                 d.get("ref", ""),
                "created_at":          created,
                "updated_at":          d.get("updated_at", created),
                "web_url":             d.get("url", ""),
                "deployed_by":         creator.get("login", ""),
                "deployed_by_avatar":  creator.get("avatar_url", ""),
            })
        return result

    # ── Branches ─────────────────────────────────────────────────────────────

    async def get_branch(self, repo_id: str, branch_name: str) -> dict:
        b = await self._get(f"/repos/{repo_id}/branches/{branch_name}")
        commit = b.get("commit") or {}
        commit_detail = commit.get("commit") or {}
        author = commit_detail.get("author") or {}
        return {
            "name":          b.get("name", ""),
            "protected":     b.get("protected", False),
            "commit_sha":    (commit.get("sha") or "")[:8],
            "commit_title":  (commit_detail.get("message") or "")[:80],
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
