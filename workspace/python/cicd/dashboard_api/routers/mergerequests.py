from fastapi import APIRouter
from datetime import datetime, timedelta
from collections import defaultdict
from services.gitlab_client import GitLabClient

router = APIRouter(prefix="/mrs", tags=["merge_requests"])
_client = GitLabClient()


@router.get("/trend")
async def mr_trend(days: int = 30):
    since = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    since_dt = datetime.strptime(since[:10], "%Y-%m-%d")
    projects = await _client.get_projects()
    daily: dict = defaultdict(lambda: {"opened": 0, "merged": 0, "closed": 0})

    # Track all MRs we've seen to avoid double counting
    seen_mrs = set()

    for project in projects:
        try:
            # Get all MRs updated since the time window - this matches what Recent MRs shows
            mrs = await _client.get_merge_requests(project["id"], updated_after=since)
            for m in mrs:
                mr_key = f"{project['id']}_{m.get('iid')}"
                if mr_key in seen_mrs:
                    continue
                seen_mrs.add(mr_key)

                # Count when MR was created (if within window)
                created_date = (m.get("created_at") or "")[:10]
                if created_date:
                    created_dt = datetime.strptime(created_date, "%Y-%m-%d")
                    if created_dt >= since_dt:
                        daily[created_date]["opened"] += 1

                # Count when MR was merged (if within window)
                if m.get("state") == "merged" and m.get("merged_at"):
                    merged_date = (m.get("merged_at") or "")[:10]
                    if merged_date:
                        merged_dt = datetime.strptime(merged_date, "%Y-%m-%d")
                        if merged_dt >= since_dt:
                            daily[merged_date]["merged"] += 1

                # Count when MR was closed (if within window and not merged)
                if m.get("state") == "closed" and m.get("closed_at"):
                    closed_date = (m.get("closed_at") or "")[:10]
                    if closed_date:
                        closed_dt = datetime.strptime(closed_date, "%Y-%m-%d")
                        if closed_dt >= since_dt:
                            daily[closed_date]["closed"] += 1
        except Exception:
            pass

    result = []
    for i in range(days):
        date = (datetime.utcnow() - timedelta(days=days - 1 - i)).strftime("%Y-%m-%d")
        d = daily.get(date, {"opened": 0, "merged": 0, "closed": 0})
        result.append({"date": date, **d})
    return result


@router.get("/recent")
async def recent_mrs(limit: int = 20):
    projects = await _client.get_projects()
    all_mrs = []

    for project in projects:
        try:
            mrs = await _client.get_merge_requests(project["id"], per_page=10, order_by="updated_at", sort="desc")
            for m in mrs[:10]:
                all_mrs.append({
                    "id": m.get("iid"),
                    "project": project.get("name", ""),
                    "project_path": project.get("path_with_namespace", ""),
                    "title": m.get("title", ""),
                    "author": (m.get("author") or {}).get("name", ""),
                    "state": m.get("state", ""),
                    "created_at": m.get("created_at"),
                    "updated_at": m.get("updated_at"),
                    "web_url": m.get("web_url"),
                    "source_branch": m.get("source_branch", ""),
                    "target_branch": m.get("target_branch", ""),
                })
        except Exception:
            pass

    all_mrs.sort(key=lambda x: x.get("updated_at") or "", reverse=True)
    return all_mrs[:limit]
