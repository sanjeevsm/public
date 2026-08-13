from fastapi import APIRouter, Depends
from datetime import datetime, timedelta
from collections import defaultdict
import asyncio
from services.base_client import BaseProviderClient
from services.provider_factory import get_client

router = APIRouter(prefix="/pipelines", tags=["pipelines"])


@router.get("/trend")
async def pipeline_trend(days: int = 14, client: BaseProviderClient = Depends(get_client)):
    repos = await client.get_repos()
    daily: dict = defaultdict(lambda: {"total": 0, "success": 0, "failed": 0})

    for repo in repos:
        try:
            pls = await client.get_pipelines(repo["id"], days=days)
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
async def pipeline_status(days: int = 30, client: BaseProviderClient = Depends(get_client)):
    repos = await client.get_repos()
    counts = {"success": 0, "failed": 0, "canceled": 0, "running": 0, "pending": 0, "skipped": 0}

    for repo in repos:
        try:
            pls = await client.get_pipelines(repo["id"], days=days)
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
async def recent_pipelines(limit: int = 20, client: BaseProviderClient = Depends(get_client)):
    repos = await client.get_repos()
    candidates = []

    for repo in repos:
        try:
            pls = await client.get_pipelines(repo["id"], days=30)
            for p in pls[:5]:
                candidates.append({
                    "_repo_id": repo["id"],
                    "_pipeline_id": p.get("id"),
                    "id":         p.get("id"),
                    "project":    repo.get("name", ""),
                    "project_path": repo.get("full_name", ""),
                    "ref":        p.get("ref"),
                    "status":     p.get("status"),
                    "created_at": p.get("created_at"),
                    "web_url":    p.get("web_url"),
                    "sha":        p.get("sha", ""),
                    "triggered_by":        (p.get("user") or {}).get("name", ""),
                    "triggered_by_avatar": (p.get("user") or {}).get("avatar_url", ""),
                    "duration":   p.get("duration"),
                })
        except Exception:
            pass

    candidates.sort(key=lambda x: x.get("created_at") or "", reverse=True)
    top = candidates[:limit]

    # Enrich with detail (avatar + duration) only for GitLab where detail adds user info
    async def enrich(p):
        if p.get("triggered_by"):
            return {k: v for k, v in p.items() if not k.startswith("_")}
        try:
            detail = await client.get_pipeline_detail(p["_repo_id"], str(p["_pipeline_id"]))
            user = detail.get("user") or {}
            return {
                **{k: v for k, v in p.items() if not k.startswith("_")},
                "duration":            detail.get("duration") or p.get("duration"),
                "triggered_by":        user.get("name", ""),
                "triggered_by_avatar": user.get("avatar_url", ""),
            }
        except Exception:
            return {k: v for k, v in p.items() if not k.startswith("_")}

    return list(await asyncio.gather(*[enrich(p) for p in top]))
