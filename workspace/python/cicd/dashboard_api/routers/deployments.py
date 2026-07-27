from fastapi import APIRouter, Depends
from services.base_client import BaseProviderClient
from services.provider_factory import get_client

router = APIRouter(prefix="/deployments", tags=["deployments"])


@router.get("/recent")
async def recent_deployments(limit: int = 20, client: BaseProviderClient = Depends(get_client)):
    repos = await client.get_repos()
    all_deps = []

    for repo in repos:
        try:
            deps = await client.get_deployments(repo["id"], days=30)
            for d in deps[:5]:
                all_deps.append({
                    "id":                 d.get("id"),
                    "project":            repo.get("name", ""),
                    "project_path":       repo.get("full_name", ""),
                    "environment":        d.get("environment", ""),
                    "status":             d.get("status", ""),
                    "ref":                d.get("ref", ""),
                    "created_at":         d.get("created_at"),
                    "updated_at":         d.get("updated_at"),
                    "web_url":            d.get("web_url", ""),
                    "deployed_by":        d.get("deployed_by", ""),
                    "deployed_by_avatar": d.get("deployed_by_avatar", ""),
                })
        except Exception:
            pass

    all_deps.sort(key=lambda x: x.get("updated_at") or "", reverse=True)
    return all_deps[:limit]
