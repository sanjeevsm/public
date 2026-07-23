from fastapi import APIRouter
from services.gitlab_client import GitLabClient

router = APIRouter(prefix="/deployments", tags=["deployments"])
_client = GitLabClient()


@router.get("/recent")
async def recent_deployments(limit: int = 20):
    projects = await _client.get_projects()
    all_deps = []

    for project in projects:
        try:
            deps = await _client.get_deployments(project["id"], order_by="updated_at", sort="desc")
            for d in deps[:5]:
                env = d.get("environment") or {}
                user = d.get("user") or {}
                all_deps.append({
                    "id": d.get("id"),
                    "project": project.get("name", ""),
                    "project_path": project.get("path_with_namespace", ""),
                    "environment": env.get("name", ""),
                    "status": d.get("status", ""),
                    "ref": d.get("ref", ""),
                    "created_at": d.get("created_at"),
                    "updated_at": d.get("updated_at"),
                    "web_url": project.get("web_url", "") + f"/-/deployments/{d.get('id')}",
                    "deployed_by": user.get("name") or user.get("username") or "",
                    "deployed_by_avatar": user.get("avatar_url") or "",
                })
        except Exception:
            pass

    all_deps.sort(key=lambda x: x.get("updated_at") or "", reverse=True)
    return all_deps[:limit]
