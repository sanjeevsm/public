from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
import json
from datetime import datetime, timedelta
from services.gitlab_client import GitLabClient
from metrics import websocket_connections_active

router = APIRouter(tags=["websocket"])
_client = GitLabClient()


async def _fetch_overview() -> dict:
    since = (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ")
    projects = await _client.get_projects()

    total = success = failed = running = 0
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

    return {
        "total_pipelines": total,
        "success": success,
        "failed": failed,
        "running": running,
        "success_rate": round(success / total * 100, 1) if total > 0 else 0,
        "avg_duration_s": avg_dur,
        "open_mrs": open_mrs,
        "total_projects": len(projects),
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.websocket("/ws/metrics")
async def ws_metrics(websocket: WebSocket):
    await websocket.accept()
    websocket_connections_active.inc()
    try:
        while True:
            try:
                data = await _fetch_overview()
                await websocket.send_text(json.dumps({"type": "metrics", "data": data}))
            except Exception as e:
                await websocket.send_text(json.dumps({"type": "error", "message": str(e)}))
            await asyncio.sleep(30)
    except WebSocketDisconnect:
        pass
    finally:
        websocket_connections_active.dec()
