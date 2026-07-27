from fastapi import APIRouter, Depends
from datetime import datetime, timedelta
from collections import defaultdict
from services.base_client import BaseProviderClient
from services.provider_factory import get_client

router = APIRouter(prefix="/mrs", tags=["merge_requests"])


@router.get("/trend")
async def mr_trend(days: int = 30, client: BaseProviderClient = Depends(get_client)):
    since_dt = datetime.utcnow() - timedelta(days=days)
    repos = await client.get_repos()
    daily: dict = defaultdict(lambda: {"opened": 0, "merged": 0, "closed": 0})
    seen = set()

    for repo in repos:
        try:
            prs = await client.get_pull_requests(repo["id"], days=days)
            for m in prs:
                key = f"{repo['id']}_{m.get('id')}"
                if key in seen:
                    continue
                seen.add(key)

                created_date = (m.get("created_at") or "")[:10]
                if created_date:
                    try:
                        if datetime.strptime(created_date, "%Y-%m-%d") >= since_dt.replace(hour=0, minute=0, second=0):
                            daily[created_date]["opened"] += 1
                    except Exception:
                        pass

                if m.get("state") == "merged" and m.get("merged_at"):
                    merged_date = (m.get("merged_at") or "")[:10]
                    if merged_date:
                        try:
                            if datetime.strptime(merged_date, "%Y-%m-%d") >= since_dt.replace(hour=0, minute=0, second=0):
                                daily[merged_date]["merged"] += 1
                        except Exception:
                            pass

                if m.get("state") == "closed" and m.get("closed_at"):
                    closed_date = (m.get("closed_at") or "")[:10]
                    if closed_date:
                        try:
                            if datetime.strptime(closed_date, "%Y-%m-%d") >= since_dt.replace(hour=0, minute=0, second=0):
                                daily[closed_date]["closed"] += 1
                        except Exception:
                            pass
        except Exception:
            pass

    result = []
    for i in range(days):
        date = (datetime.utcnow() - timedelta(days=days - 1 - i)).strftime("%Y-%m-%d")
        d = daily.get(date, {"opened": 0, "merged": 0, "closed": 0})
        result.append({"date": date, **d})
    return result


@router.get("/recent")
async def recent_mrs(limit: int = 20, client: BaseProviderClient = Depends(get_client)):
    repos = await client.get_repos()
    all_mrs = []

    for repo in repos:
        try:
            prs = await client.get_pull_requests(repo["id"], days=30)
            for m in prs[:10]:
                all_mrs.append({
                    "id":            m.get("id"),
                    "project":       repo.get("name", ""),
                    "project_path":  repo.get("full_name", ""),
                    "title":         m.get("title", ""),
                    "author":        m.get("author", ""),
                    "state":         m.get("state", ""),
                    "created_at":    m.get("created_at"),
                    "updated_at":    m.get("updated_at"),
                    "web_url":       m.get("web_url"),
                    "source_branch": m.get("source_branch", ""),
                    "target_branch": m.get("target_branch", ""),
                })
        except Exception:
            pass

    all_mrs.sort(key=lambda x: x.get("updated_at") or "", reverse=True)
    return all_mrs[:limit]
