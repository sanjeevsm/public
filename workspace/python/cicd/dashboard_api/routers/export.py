from fastapi import APIRouter, Depends
from fastapi.responses import Response
from datetime import datetime, timedelta
from services.base_client import BaseProviderClient
from services.provider_factory import get_client
from services.exporter import export_csv, export_json, export_excel, export_pdf

router = APIRouter(prefix="/export", tags=["export"])


def _ts() -> str:
    return datetime.utcnow().strftime("%Y%m%d_%H%M%S")


async def _gather(client: BaseProviderClient, days: int) -> dict:
    repos = await client.get_repos()

    pipelines = []
    for repo in repos:
        try:
            pls = await client.get_pipelines(repo["id"], days=days)
            for p in pls:
                pipelines.append({
                    "project_name": repo.get("name", ""),
                    "id":           p.get("id", ""),
                    "status":       p.get("status", ""),
                    "ref":          p.get("ref", ""),
                    "duration":     p.get("duration"),
                    "created_at":   p.get("created_at", ""),
                    "web_url":      p.get("web_url", ""),
                })
        except Exception:
            pass

    mrs = []
    for repo in repos:
        try:
            prs = await client.get_pull_requests(repo["id"], days=days)
            for m in prs:
                mrs.append({
                    "project_name": repo.get("name", ""),
                    "id":           m.get("id", ""),
                    "title":        m.get("title", ""),
                    "author_name":  m.get("author", ""),
                    "state":        m.get("state", ""),
                    "created_at":   m.get("created_at", ""),
                })
        except Exception:
            pass

    return {"pipelines": pipelines, "merge_requests": mrs, "projects": repos}


@router.get("/csv")
async def export_as_csv(days: int = 30, client: BaseProviderClient = Depends(get_client)):
    data = await _gather(client, days)
    return Response(
        content=export_csv(data),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=cicd_{_ts()}.csv"},
    )


@router.get("/json")
async def export_as_json(days: int = 30, client: BaseProviderClient = Depends(get_client)):
    data = await _gather(client, days)
    return Response(
        content=export_json(data),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename=cicd_{_ts()}.json"},
    )


@router.get("/excel")
async def export_as_excel(days: int = 30, client: BaseProviderClient = Depends(get_client)):
    data = await _gather(client, days)
    buf = export_excel(data)
    return Response(
        content=buf.read(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=cicd_{_ts()}.xlsx"},
    )


@router.get("/pdf")
async def export_as_pdf(days: int = 30, client: BaseProviderClient = Depends(get_client)):
    data = await _gather(client, days)
    buf = export_pdf(data)
    return Response(
        content=buf.read(),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=cicd_{_ts()}.pdf"},
    )
