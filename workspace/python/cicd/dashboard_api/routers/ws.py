"""WebSocket endpoint for live metrics push.

Browser WebSocket API does not support custom headers, so credentials are
passed as query parameters:
  ws://host/ws/metrics?provider=gitlab&token=xxx&url=https://gitlab.com
                       &username=&project_ids=&limit=20
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
import asyncio
import json
from datetime import datetime, timedelta
from services.provider_factory import get_client_from_params
from metrics import websocket_connections_active

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/metrics")
async def ws_metrics(
    websocket: WebSocket,
    provider:    str = Query(default=""),
    token:       str = Query(default=""),
    url:         str = Query(default=""),
    username:    str = Query(default=""),
    project_ids: str = Query(default=""),
    limit:       int = Query(default=20),
):
    await websocket.accept()
    websocket_connections_active.inc()
    try:
        while True:
            try:
                client = get_client_from_params(
                    provider=provider,
                    token=token,
                    url=url,
                    username=username,
                    project_ids=project_ids,
                    limit=limit,
                )
                data = await _fetch_overview(client)
                await websocket.send_text(json.dumps({"type": "metrics", "data": data}))
            except Exception as e:
                await websocket.send_text(json.dumps({"type": "error", "message": str(e)}))
            await asyncio.sleep(30)
    except WebSocketDisconnect:
        pass
    finally:
        websocket_connections_active.dec()


async def _fetch_overview(client) -> dict:
    since_days = 30
    repos = await client.get_repos()

    total = success = failed = running = 0
    durations = []

    for repo in repos:
        try:
            pls = await client.get_pipelines(repo["id"], days=since_days)
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

    open_prs = 0
    for repo in repos:
        try:
            prs = await client.get_pull_requests(repo["id"], days=since_days, state="opened")
            open_prs += len(prs)
        except Exception:
            pass

    avg_dur = round(sum(durations) / len(durations)) if durations else 0

    return {
        "total_pipelines": total,
        "success":         success,
        "failed":          failed,
        "running":         running,
        "success_rate":    round(success / total * 100, 1) if total > 0 else 0,
        "avg_duration_s":  avg_dur,
        "open_mrs":        open_prs,
        "total_projects":  len(repos),
        "timestamp":       datetime.utcnow().isoformat(),
    }
