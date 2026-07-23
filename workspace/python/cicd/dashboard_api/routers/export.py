from fastapi import APIRouter
from fastapi.responses import Response
from datetime import datetime, timedelta
from services.gitlab_client import GitLabClient
from services.exporter import export_csv, export_json, export_excel, export_pdf

router = APIRouter(prefix="/export", tags=["export"])
_client = GitLabClient()


def _ts() -> str:
    return datetime.utcnow().strftime("%Y%m%d_%H%M%S")


async def _gather(days: int) -> dict:
    since = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    projects = await _client.get_projects()

    pipelines = []
    for project in projects:
        try:
            pls = await _client.get_pipelines(project["id"], updated_after=since)
            for p in pls:
                p["project_name"] = project.get("name", "")
                pipelines.append(p)
        except Exception:
            pass

    mrs = []
    for project in projects:
        try:
            raw = await _client.get_merge_requests(project["id"], created_after=since)
            for m in raw:
                m["project_name"] = project.get("name", "")
                mrs.append(m)
        except Exception:
            pass

    return {"pipelines": pipelines, "merge_requests": mrs, "projects": projects}


@router.get("/csv")
async def export_as_csv(days: int = 30):
    data = await _gather(days)
    return Response(
        content=export_csv(data),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=cicd_{_ts()}.csv"},
    )


@router.get("/json")
async def export_as_json(days: int = 30):
    data = await _gather(days)
    return Response(
        content=export_json(data),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename=cicd_{_ts()}.json"},
    )


@router.get("/excel")
async def export_as_excel(days: int = 30):
    data = await _gather(days)
    buf = export_excel(data)
    return Response(
        content=buf.read(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=cicd_{_ts()}.xlsx"},
    )


@router.get("/pdf")
async def export_as_pdf(days: int = 30):
    data = await _gather(days)
    buf = export_pdf(data)
    return Response(
        content=buf.read(),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=cicd_{_ts()}.pdf"},
    )
