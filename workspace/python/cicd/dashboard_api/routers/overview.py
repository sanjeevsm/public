from fastapi import APIRouter
from datetime import datetime, timedelta
from services.gitlab_client import GitLabClient
from metrics import gitlab_pipelines_total, gitlab_projects_total

router = APIRouter(tags=["overview"])
_client = GitLabClient()


@router.get("/overview")
async def get_overview(days: int = 30):
    since = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    projects = await _client.get_projects()

    total = success = failed = running = pending = canceled = 0
    durations = []

    for project in projects:
        try:
            pls = await _client.get_pipelines(project["id"], updated_after=since)
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

    open_mrs = 0
    for project in projects:
        try:
            mrs = await _client.get_merge_requests(project["id"], state="opened")
            open_mrs += len(mrs)
        except Exception:
            pass

    avg_dur = round(sum(durations) / len(durations)) if durations else 0

    gitlab_pipelines_total.labels(status="success").set(success)
    gitlab_pipelines_total.labels(status="failed").set(failed)
    gitlab_pipelines_total.labels(status="running").set(running)
    gitlab_pipelines_total.labels(status="pending").set(pending)
    gitlab_pipelines_total.labels(status="canceled").set(canceled)
    gitlab_projects_total.set(len(projects))

    return {
        "total_pipelines": total,
        "success": success,
        "failed": failed,
        "running": running,
        "pending": pending,
        "canceled": canceled,
        "success_rate": round(success / total * 100, 1) if total > 0 else 0,
        "avg_duration_s": avg_dur,
        "open_mrs": open_mrs,
        "total_projects": len(projects),
    }
