from fastapi import APIRouter, Depends
from datetime import datetime, timedelta
from services.base_client import BaseProviderClient
from services.provider_factory import get_client
from metrics import gitlab_pipelines_total, gitlab_projects_total

router = APIRouter(tags=["overview"])


@router.get("/overview")
async def get_overview(days: int = 30, client: BaseProviderClient = Depends(get_client)):
    repos = await client.get_repos()

    total = success = failed = running = pending = canceled = 0
    durations = []

    for repo in repos:
        try:
            pls = await client.get_pipelines(repo["id"], days=days)
            for p in pls:
                total += 1
                s = p.get("status", "")
                if s == "success":
                    success += 1
                elif s == "failed":
                    failed += 1
                elif s == "running":
                    running += 1
                elif s == "pending":
                    pending += 1
                elif s in ("canceled", "cancelled"):
                    canceled += 1
                dur = p.get("duration")
                if dur:
                    durations.append(dur)
        except Exception:
            pass

    open_prs = 0
    for repo in repos:
        try:
            prs = await client.get_pull_requests(repo["id"], days=days, state="opened")
            open_prs += len(prs)
        except Exception:
            pass

    avg_dur = round(sum(durations) / len(durations)) if durations else 0

    gitlab_pipelines_total.labels(status="success").set(success)
    gitlab_pipelines_total.labels(status="failed").set(failed)
    gitlab_pipelines_total.labels(status="running").set(running)
    gitlab_pipelines_total.labels(status="pending").set(pending)
    gitlab_pipelines_total.labels(status="canceled").set(canceled)
    gitlab_projects_total.set(len(repos))

    return {
        "total_pipelines": total,
        "success": success,
        "failed": failed,
        "running": running,
        "pending": pending,
        "canceled": canceled,
        "success_rate": round(success / total * 100, 1) if total > 0 else 0,
        "avg_duration_s": avg_dur,
        "open_mrs": open_prs,
        "total_projects": len(repos),
        "pr_label": client.pr_label,
        "pipeline_label": client.pipeline_label,
    }
