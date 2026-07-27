from abc import ABC, abstractmethod
from typing import Optional


class BaseProviderClient(ABC):
    """Normalized interface all provider clients must implement.

    Every method returns provider-agnostic dicts so routers never contain
    provider-specific field access.
    """

    PROVIDER_ID: str = ""

    def __init__(self, token: str, base_url: str, username: str = "",
                 project_ids: str = "", project_limit: int = 20, cache_ttl: int = 60):
        self.token = token
        self.base_url = base_url.rstrip("/")
        self.username = username          # org name (GitHub) or workspace (Bitbucket)
        self.project_ids = project_ids    # comma-separated IDs / slugs
        self.project_limit = project_limit
        self.cache_ttl = cache_ttl

    # ── Repository listing ────────────────────────────────────────────────────

    @abstractmethod
    async def get_repos(self) -> list[dict]:
        """Return list of accessible repos.

        Each item: {id, name, full_name, url, default_branch, namespace}
        """

    # ── Pipelines / workflow runs ─────────────────────────────────────────────

    @abstractmethod
    async def get_pipelines(self, repo_id: str, days: int = 30,
                            ref: Optional[str] = None, **kwargs) -> list[dict]:
        """Return pipeline/workflow runs for a repo.

        Each item: {id, repo_id, repo_name, repo_path, status, ref,
                    duration, created_at, web_url, sha, user}
        user is: {name, avatar_url}
        """

    @abstractmethod
    async def get_pipeline_detail(self, repo_id: str, pipeline_id: str) -> dict:
        """Return single pipeline with full user info."""

    # ── Jobs / steps ──────────────────────────────────────────────────────────

    @abstractmethod
    async def get_failed_jobs(self, repo_id: str) -> list[dict]:
        """Return failed jobs/steps.

        Each item: {id, name, stage, status, repo_name, duration,
                    created_at, web_url, ref}
        """

    @abstractmethod
    async def get_all_jobs(self, repo_id: str) -> list[dict]:
        """Return recent jobs/steps (same shape as get_failed_jobs)."""

    # ── Pull / Merge Requests ─────────────────────────────────────────────────

    @abstractmethod
    async def get_pull_requests(self, repo_id: str, days: int = 30,
                                state: str = "all", **kwargs) -> list[dict]:
        """Return PRs/MRs.

        Each item: {id, repo_name, repo_path, title, author, state,
                    source_branch, target_branch, created_at, updated_at,
                    merged_at, closed_at, web_url}
        """

    # ── Deployments ───────────────────────────────────────────────────────────

    @abstractmethod
    async def get_deployments(self, repo_id: str, days: int = 30,
                              **kwargs) -> list[dict]:
        """Return deployments.

        Each item: {id, repo_name, repo_path, environment, status, ref,
                    created_at, updated_at, web_url, deployed_by, deployed_by_avatar}
        """

    # ── Branches ─────────────────────────────────────────────────────────────

    @abstractmethod
    async def get_branch(self, repo_id: str, branch_name: str) -> dict:
        """Return branch info.

        Returns: {name, protected, commit_sha, commit_title,
                  commit_author, committed_at}
        """

    @abstractmethod
    async def get_latest_pipeline(self, repo_id: str,
                                  ref: Optional[str] = None) -> Optional[dict]:
        """Return the most recent pipeline for a repo/branch."""

    # ── Labels ───────────────────────────────────────────────────────────────

    @property
    def pr_label(self) -> str:
        """Human label for PRs/MRs (shown in UI table headers)."""
        return "Pull Requests"

    @property
    def pipeline_label(self) -> str:
        """Human label for pipelines/runs (shown in UI table headers)."""
        return "Pipelines"
