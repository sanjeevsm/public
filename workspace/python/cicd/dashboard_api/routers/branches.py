from fastapi import APIRouter
import asyncio
from services.gitlab_client import GitLabClient

router = APIRouter(prefix="/branches", tags=["branches"])
_client = GitLabClient()


@router.get("/overview")
async def branches_overview():
    projects = await _client.get_projects()

    async def project_branch(project):
        try:
            default_branch = project.get("default_branch") or "main"
            branch, pipeline = await asyncio.gather(
                _client.get_branch(project["id"], default_branch),
                _client.get_latest_pipeline(project["id"], ref=default_branch),
                return_exceptions=True,
            )
            if isinstance(branch, Exception):
                return None
            commit = branch.get("commit") or {}
            pl = pipeline if isinstance(pipeline, dict) else None
            return {
                "project": project.get("name", ""),
                "project_path": project.get("path_with_namespace", ""),
                "branch": default_branch,
                "protected": branch.get("protected", False),
                "commit_sha": (commit.get("id") or "")[:8],
                "commit_title": (commit.get("title") or commit.get("message") or "")[:80],
                "commit_author": commit.get("author_name", ""),
                "committed_at": commit.get("committed_date") or commit.get("authored_date"),
                "pipeline_status": pl.get("status") if pl else None,
                "pipeline_url": pl.get("web_url") if pl else None,
            }
        except Exception:
            return None

    results = await asyncio.gather(*[project_branch(p) for p in projects])
    return [r for r in results if r is not None]
