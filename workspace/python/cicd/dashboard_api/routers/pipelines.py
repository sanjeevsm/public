from fastapi import APIRouter
from datetime import datetime, timedelta
from collections import defaultdict
import asyncio
from services.gitlab_client import GitLabClient

router = APIRouter(prefix="/pipelines", tags=["pipelines"])
_client = GitLabClient()


@router.get("/trend")
async def pipeline_trend(days: int = 14):
    since = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    projects = await _client.get_projects()
    daily: dict = defaultdict(lambda: {"total": 0, "success": 0, "failed": 0})

    for project in projects:
        try:
            pls = await _client.get_pipelines(project["id"], updated_after=since)
            for p in pls:
                date = (p.get("created_at") or "")[:10]
                if not date:
                    continue
                daily[date]["total"] += 1
                s = p.get("status", "")
                if s == "success":
                    daily[date]["success"] += 1
                elif s == "failed":
                    daily[date]["failed"] += 1
        except Exception:
            pass

    result = []
    for i in range(days):
        date = (datetime.utcnow() - timedelta(days=days - 1 - i)).strftime("%Y-%m-%d")
        d = daily.get(date, {"total": 0, "success": 0, "failed": 0})
        result.append({"date": date, **d})
    return result


@router.get("/status")
async def pipeline_status(days: int = 30):
    since = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    projects = await _client.get_projects()
    counts = {"success": 0, "failed": 0, "canceled": 0, "running": 0, "pending": 0, "skipped": 0}

    for project in projects:
        try:
            pls = await _client.get_pipelines(project["id"], updated_after=since)
            for p in pls:
                s = p.get("status", "")
                if s in ("canceled", "cancelled"):
                    counts["canceled"] += 1
                elif s in counts:
                    counts[s] += 1
        except Exception:
            pass

    return counts


@router.get("/recent")
async def recent_pipelines(limit: int = 20):
    projects = await _client.get_projects()
    candidates = []

    for project in projects:
        try:
            pls = await _client.get_pipelines(project["id"])
            for p in pls[:5]:
                candidates.append({
                    "_project_id": project["id"],
                    "id": p.get("id"),
                    "project": project.get("name", ""),
                    "project_path": project.get("path_with_namespace", ""),
                    "ref": p.get("ref"),
                    "status": p.get("status"),
                    "created_at": p.get("created_at"),
                    "web_url": p.get("web_url"),
                    "sha": (p.get("sha") or "")[:8],
                })
        except Exception:
            pass

    candidates.sort(key=lambda x: x.get("created_at") or "", reverse=True)
    top = candidates[:limit]

    async def enrich(p):
        try:
            detail = await _client.get_pipeline(p["_project_id"], p["id"])
            user = detail.get("user") or {}
            return {
                **{k: v for k, v in p.items() if k != "_project_id"},
                "duration": detail.get("duration"),
                "triggered_by": user.get("name") or user.get("username") or "",
                "triggered_by_avatar": user.get("avatar_url") or "",
            }
        except Exception:
            return {
                **{k: v for k, v in p.items() if k != "_project_id"},
                "duration": None,
                "triggered_by": "",
                "triggered_by_avatar": "",
            }

    return list(await asyncio.gather(*[enrich(p) for p in top]))
