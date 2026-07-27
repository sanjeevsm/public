from fastapi import APIRouter, Depends
from collections import defaultdict
from services.base_client import BaseProviderClient
from services.provider_factory import get_client

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/top-failing")
async def top_failing_jobs(limit: int = 10, client: BaseProviderClient = Depends(get_client)):
    repos = await client.get_repos()
    stats: dict = defaultdict(lambda: {"name": "", "project": "", "failures": 0})

    for repo in repos:
        try:
            failed = await client.get_failed_jobs(repo["id"])
            for j in failed:
                name = j.get("name", "unknown")
                key = f"{repo.get('name', '')}::{name}"
                stats[key]["name"] = name
                stats[key]["project"] = repo.get("name", "")
                stats[key]["failures"] += 1
        except Exception:
            pass

    ranked = sorted(stats.values(), key=lambda x: x["failures"], reverse=True)
    return ranked[:limit]


@router.get("/stages")
async def job_stages(client: BaseProviderClient = Depends(get_client)):
    repos = await client.get_repos()
    stage_stats: dict = defaultdict(lambda: {"total": 0, "success": 0, "failed": 0})

    for repo in repos[:5]:
        try:
            jobs = await client.get_all_jobs(repo["id"])
            for j in jobs:
                stage = j.get("stage", "unknown")
                stage_stats[stage]["total"] += 1
                s = j.get("status", "")
                if s == "success":
                    stage_stats[stage]["success"] += 1
                elif s == "failed":
                    stage_stats[stage]["failed"] += 1
        except Exception:
            pass

    return [{"stage": k, **v} for k, v in sorted(stage_stats.items())]


@router.get("/recent")
async def recent_jobs(limit: int = 20, client: BaseProviderClient = Depends(get_client)):
    repos = await client.get_repos()
    all_jobs = []

    for repo in repos[:5]:
        try:
            jobs = await client.get_all_jobs(repo["id"])
            for j in jobs[:10]:
                all_jobs.append({
                    "id":         j.get("id"),
                    "name":       j.get("name"),
                    "project":    repo.get("name", ""),
                    "stage":      j.get("stage"),
                    "status":     j.get("status"),
                    "duration":   j.get("duration"),
                    "created_at": j.get("created_at"),
                    "web_url":    j.get("web_url"),
                    "ref":        j.get("ref"),
                })
        except Exception:
            pass

    all_jobs.sort(key=lambda x: x.get("created_at") or "", reverse=True)
    return all_jobs[:limit]
