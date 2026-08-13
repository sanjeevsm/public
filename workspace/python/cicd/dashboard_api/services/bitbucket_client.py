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

_PROVIDER = "bitbucket"

# Bitbucket pipeline state/result → normalized
_PIPELINE_STATUS = {
    "SUCCESSFUL": "success",
    "FAILED":     "failed",
    "ERROR":      "failed",
    "STOPPED":    "canceled",
    "IN_PROGRESS": "running",
    "PENDING":     "pending",
    "HALTED":      "canceled",
}

_PR_STATE = {
    "OPEN":        "opened",
    "MERGED":      "merged",
    "DECLINED":    "closed",
    "SUPERSEDED":  "closed",
}


def _bb_pipeline_status(pl: dict) -> str:
    state = (pl.get("state") or {})
    name = state.get("name", "")
    if name in ("COMPLETED", ""):
        result = (state.get("result") or {}).get("name", "")
        return _PIPELINE_STATUS.get(result, "unknown")
    return _PIPELINE_STATUS.get(name, "unknown")


class BitbucketClient(BaseProviderClient):
    PROVIDER_ID = "bitbucket"

    def __init__(self, token: str, base_url: str = "https://api.bitbucket.org",
                 username: str = "", project_ids: str = "",
                 project_limit: int = 20, cache_ttl: int = 60):
        api_base = base_url.rstrip("/")
        if not api_base.endswith("/2.0"):
            api_base = api_base + "/2.0"
        super().__init__(token, api_base, username, project_ids, project_limit, cache_ttl)
        self.workspace = username  # Bitbucket workspace slug

    @property
    def _headers(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self.token}"}

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
        """Bitbucket uses cursor-based pagination (next link)."""
        p = dict(params or {})
        p.setdefault("pagelen", 50)
        cache_key = f"pages:{path}:{max_items}"
        cached = get_cached(_PROVIDER, self.token, cache_key, p, self.cache_ttl)
        if cached is not None:
            return cached
        results: List = []
        url = f"{self.base_url}{path}"
        t0 = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=30) as c:
                while url and len(results) < max_items:
                    r = await c.get(url, headers=self._headers, params=p)
                    r.raise_for_status()
                    data = r.json()
                    values = data.get("values", [])
                    results.extend(values)
                    url = data.get("next")
                    p = {}  # next URL already has params embedded
        except Exception:
            provider_api_errors.labels(path_prefix=path.split("/")[1] if "/" in path else path).inc()
            raise
        finally:
            provider_api_duration.labels(path_prefix=path.split("/")[1] if "/" in path else path).observe(
                time.perf_counter() - t0
            )
        result = results[:max_items]
        set_cached(_PROVIDER, self.token, cache_key, params or {}, result)
        return result

    def _slug(self, repo_id: str) -> str:
        """repo_id is 'workspace/slug'."""
        return repo_id.split("/")[-1] if "/" in repo_id else repo_id

    # ── Repo listing ─────────────────────────────────────────────────────────

    async def get_repos(self) -> List[Dict]:
        if not self.workspace:
            return []
        if self.project_ids:
            repos = []
            for slug in self.project_ids.split(","):
                slug = slug.strip()
                if not slug:
                    continue
                try:
                    data = await self._get(f"/repositories/{self.workspace}/{slug}")
                    repos.append(self._norm_repo(data))
                except Exception:
                    pass
            return repos

        data = await self._get_pages(
            f"/repositories/{self.workspace}",
            {"role": "member", "sort": "-updated_on"},
            max_items=self.project_limit,
        )
        return [self._norm_repo(r) for r in data]

    def _norm_repo(self, r: dict) -> dict:
        full_name = r.get("full_name", "")
        ws = full_name.split("/")[0] if "/" in full_name else self.workspace
        return {
            "id":             full_name,
            "name":           r.get("name", ""),
            "full_name":      full_name,
            "url":            (r.get("links") or {}).get("html", {}).get("href", ""),
            "default_branch": (r.get("mainbranch") or {}).get("name", "main"),
            "namespace":      ws,
        }

    # ── Pipelines ─────────────────────────────────────────────────────────────

    async def get_pipelines(self, repo_id: str, days: int = 30,
                            ref: Optional[str] = None, **kwargs) -> List[Dict]:
        since = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
        params = {
            "sort": "-created_on",
            "fields": "+values.target,+values.state,+values.creator",
        }
        pls = await self._get_pages(
            f"/repositories/{repo_id}/pipelines/",
            params, max_items=200,
        )
        result = []
        for p in pls:
            created = p.get("created_on", "")
            try:
                if datetime.fromisoformat(created.replace("Z", "+00:00")).replace(tzinfo=None) < datetime.utcnow() - timedelta(days=days):
                    continue
            except Exception:
                pass
            target = p.get("target") or {}
            branch = ref or (target.get("ref_name") or target.get("branch", {}).get("name", ""))
            if ref and branch != ref:
                continue
            creator = p.get("creator") or {}
            result.append({
                "id":        p.get("uuid", str(p.get("build_number", ""))),
                "repo_id":   repo_id,
                "repo_name": repo_id.split("/")[-1],
                "repo_path": repo_id,
                "status":    _bb_pipeline_status(p),
                "ref":       branch,
                "duration":  p.get("duration_in_seconds"),
                "created_at": created,
                "web_url":   f"https://bitbucket.org/{repo_id}/pipelines/{p.get('uuid', '')}",
                "sha":       (target.get("commit") or {}).get("hash", "")[:8],
                "user": {
                    "name":       creator.get("display_name", creator.get("nickname", "")),
                    "avatar_url": (creator.get("links") or {}).get("avatar", {}).get("href", ""),
                },
            })
        return result

    async def get_pipeline_detail(self, repo_id: str, pipeline_id: str) -> dict:
        data = await self._get(f"/repositories/{repo_id}/pipelines/{pipeline_id}")
        target = data.get("target") or {}
        creator = data.get("creator") or {}
        return {
            "id":        pipeline_id,
            "repo_id":   repo_id,
            "repo_name": repo_id.split("/")[-1],
            "repo_path": repo_id,
            "status":    _bb_pipeline_status(data),
            "ref":       (target.get("ref_name") or ""),
            "duration":  data.get("duration_in_seconds"),
            "created_at": data.get("created_on", ""),
            "web_url":   f"https://bitbucket.org/{repo_id}/pipelines/{pipeline_id}",
            "sha":       "",
            "user": {
                "name":       creator.get("display_name", ""),
                "avatar_url": (creator.get("links") or {}).get("avatar", {}).get("href", ""),
            },
        }

    async def get_latest_pipeline(self, repo_id: str,
                                  ref: Optional[str] = None) -> Optional[Dict]:
        pls = await self.get_pipelines(repo_id, days=7, ref=ref)
        return pls[0] if pls else None

    # ── Jobs (pipeline steps) ─────────────────────────────────────────────────

    async def _get_steps(self, repo_id: str, pipeline_id: str) -> List[Dict]:
        steps = await self._get_pages(
            f"/repositories/{repo_id}/pipelines/{pipeline_id}/steps/",
            max_items=50,
        )
        return [self._norm_step(s, repo_id) for s in steps]

    def _norm_step(self, s: dict, repo_id: str) -> dict:
        state = (s.get("state") or {})
        result_name = (state.get("result") or {}).get("name", "")
        state_name = state.get("name", "")
        if result_name:
            status = _PIPELINE_STATUS.get(result_name, "unknown")
        else:
            status = _PIPELINE_STATUS.get(state_name, "pending")
        return {
            "id":        s.get("uuid", ""),
            "name":      s.get("name", ""),
            "stage":     s.get("name", ""),
            "status":    status,
            "repo_name": repo_id.split("/")[-1],
            "duration":  s.get("duration_in_seconds"),
            "created_at": s.get("started_on", ""),
            "web_url":   "",
            "ref":       "",
        }

    async def get_failed_jobs(self, repo_id: str) -> List[Dict]:
        pls = await self.get_pipelines(repo_id, days=7)
        failed_pls = [p for p in pls if p["status"] == "failed"][:5]
        jobs: List[Dict] = []
        for pl in failed_pls:
            try:
                steps = await self._get_steps(repo_id, pl["id"])
                jobs.extend([s for s in steps if s["status"] == "failed"])
            except Exception:
                pass
        return jobs

    async def get_all_jobs(self, repo_id: str) -> List[Dict]:
        pls = await self.get_pipelines(repo_id, days=7)
        jobs: List[Dict] = []
        for pl in pls[:5]:
            try:
                jobs.extend(await self._get_steps(repo_id, pl["id"]))
            except Exception:
                pass
        return jobs

    # ── Pull Requests ─────────────────────────────────────────────────────────

    async def get_pull_requests(self, repo_id: str, days: int = 30,
                                state: str = "all", **kwargs) -> List[Dict]:
        bb_states = {
            "all":    ["OPEN", "MERGED", "DECLINED"],
            "opened": ["OPEN"],
            "merged": ["MERGED"],
            "closed": ["DECLINED"],
        }.get(state, ["OPEN", "MERGED", "DECLINED"])

        since = datetime.utcnow() - timedelta(days=days)
        result = []
        for bb_state in bb_states:
            prs = await self._get_pages(
                f"/repositories/{repo_id}/pullrequests",
                {"state": bb_state, "sort": "-updated_on"},
                max_items=100,
            )
            for p in prs:
                updated = p.get("updated_on", "")
                try:
                    if datetime.fromisoformat(updated.replace("Z", "+00:00")).replace(tzinfo=None) < since:
                        continue
                except Exception:
                    pass
                result.append(self._norm_pr(p, repo_id))
        return result

    def _norm_pr(self, p: dict, repo_id: str) -> dict:
        author = p.get("author") or {}
        return {
            "id":            str(p.get("id", "")),
            "repo_name":     repo_id.split("/")[-1],
            "repo_path":     repo_id,
            "title":         p.get("title", ""),
            "author":        author.get("display_name", author.get("nickname", "")),
            "author_name":   author.get("display_name", author.get("nickname", "")),
            "state":         _PR_STATE.get(p.get("state", "OPEN"), "opened"),
            "source_branch": (p.get("source") or {}).get("branch", {}).get("name", ""),
            "target_branch": (p.get("destination") or {}).get("branch", {}).get("name", ""),
            "created_at":    p.get("created_on", ""),
            "updated_at":    p.get("updated_on", ""),
            "merged_at":     p.get("merge_commit") and p.get("updated_on"),
            "closed_at":     p.get("updated_on") if p.get("state") in ("DECLINED", "SUPERSEDED") else None,
            "web_url":       (p.get("links") or {}).get("html", {}).get("href", ""),
        }

    # ── Deployments ───────────────────────────────────────────────────────────

    async def get_deployments(self, repo_id: str, days: int = 30, **kwargs) -> List[Dict]:
        deps = await self._get_pages(
            f"/repositories/{repo_id}/deployments/",
            {"sort": "-last_update_time"},
            max_items=50,
        )
        since = datetime.utcnow() - timedelta(days=days)
        result = []
        for d in deps:
            updated = d.get("last_update_time", "")
            try:
                if datetime.fromisoformat(updated.replace("Z", "+00:00")).replace(tzinfo=None) < since:
                    continue
            except Exception:
                pass
            deployer = d.get("deployable", {}).get("commit", {}).get("author") or {}
            result.append({
                "id":                  str(d.get("uuid", "")),
                "repo_name":           repo_id.split("/")[-1],
                "repo_path":           repo_id,
                "environment":         (d.get("environment") or {}).get("name", ""),
                "status":              d.get("state", "").lower() or "unknown",
                "ref":                 (d.get("deployable") or {}).get("commit", {}).get("hash", "")[:8],
                "created_at":          d.get("created_on", ""),
                "updated_at":          updated,
                "web_url":             (d.get("links") or {}).get("html", {}).get("href", ""),
                "deployed_by":         deployer.get("display_name", deployer.get("user", {}).get("display_name", "")),
                "deployed_by_avatar":  "",
            })
        return result

    # ── Branches ─────────────────────────────────────────────────────────────

    async def get_branch(self, repo_id: str, branch_name: str) -> dict:
        b = await self._get(f"/repositories/{repo_id}/refs/branches/{branch_name}")
        target = b.get("target") or {}
        author = (target.get("author") or {})
        return {
            "name":          b.get("name", ""),
            "protected":     False,  # Bitbucket doesn't expose protected flag in this API
            "commit_sha":    (target.get("hash") or "")[:8],
            "commit_title":  (target.get("message") or "")[:80],
            "commit_author": author.get("raw", ""),
            "committed_at":  target.get("date", ""),
        }

    # ── Labels ───────────────────────────────────────────────────────────────

    @property
    def pr_label(self) -> str:
        return "Pull Requests"

    @property
    def pipeline_label(self) -> str:
        return "Pipelines"
