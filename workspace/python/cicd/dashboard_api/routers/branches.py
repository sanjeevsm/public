from fastapi import APIRouter, Depends
import asyncio
from services.base_client import BaseProviderClient
from services.provider_factory import get_client

router = APIRouter(prefix="/branches", tags=["branches"])


@router.get("/overview")
async def branches_overview(client: BaseProviderClient = Depends(get_client)):
    repos = await client.get_repos()

    async def repo_branch(repo):
        try:
            default_branch = repo.get("default_branch") or "main"
            branch, pipeline = await asyncio.gather(
                client.get_branch(repo["id"], default_branch),
                client.get_latest_pipeline(repo["id"], ref=default_branch),
                return_exceptions=True,
            )
            if isinstance(branch, Exception):
                return None
            pl = pipeline if isinstance(pipeline, dict) else None
            return {
                "project":       repo.get("name", ""),
                "project_path":  repo.get("full_name", ""),
                "branch":        default_branch,
                "protected":     branch.get("protected", False),
                "commit_sha":    branch.get("commit_sha", ""),
                "commit_title":  branch.get("commit_title", ""),
                "commit_author": branch.get("commit_author", ""),
                "committed_at":  branch.get("committed_at"),
                "pipeline_status": pl.get("status") if pl else None,
                "pipeline_url":    pl.get("web_url") if pl else None,
            }
        except Exception:
            return None

    results = await asyncio.gather(*[repo_branch(r) for r in repos])
    return [r for r in results if r is not None]
