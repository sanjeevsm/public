from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncio
import random
import math
from typing import Dict, Set
from . import transport_providers

app = FastAPI(title="iTransit+ (stateless mock)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory pubsub: stop_id -> set of websockets
subscriptions: Dict[str, Set[WebSocket]] = {}
subscriptions_lock = asyncio.Lock()


def mock_nearby_stops(lat: float, lon: float, radius: int, country: str):
    # generate 8 mock stops around the location
    stops = []
    for i in range(8):
        angle = i * (2 * math.pi / 8)
        d = (i + 1) * 0.002  # small offset
        s_lat = lat + d * math.cos(angle)
        s_lon = lon + d * math.sin(angle)
        stops.append({
            "stop_id": f"{country[:2].upper()}-S-{int((lat+lon)*1000)%10000}-{i}",
            "name": f"Stop {i+1}",
            "lat": round(s_lat, 6),
            "lon": round(s_lon, 6),
            "modes": ["bus"] if i % 2 == 0 else ["tram", "train"],
            "distance_m": int(d * 111000),
        })
    return stops


def mock_departures(stop_id: str):
    # generate 5 departures with random minutes
    deps = []
    for i in range(5):
        mins = random.randint(0, 25)
        deps.append({
            "line": f"{random.choice(['A','B','X','10','24'])}",
            "destination": f"Destination {random.randint(1,50)}",
            "expected_minutes": mins,
        })
    # sort by expected_minutes
    deps.sort(key=lambda d: d["expected_minutes"])
    return deps


@app.get("/api/countries")
async def countries():
    return ["England", "Scotland", "Wales", "Northern Ireland"]



@app.get("/api/stops/nearby")
async def stops_nearby(lat: float, lon: float, radius: int = 1000, country: str = "England"):
    try:
        lat = float(lat)
        lon = float(lon)
    except Exception:
        return JSONResponse({"error": "invalid lat/lon"}, status_code=400)
    # try live providers first; fall back to mock
    try:
        res = await transport_providers.get_nearby(lat, lon, radius, country)
        if res:
            return res
    except Exception:
        pass
    return mock_nearby_stops(lat, lon, radius, country)


@app.get("/api/stops/{stop_id}/departures")
async def departures(stop_id: str, country: str = "England"):
    # try live provider for the country first
    try:
        res = await transport_providers.get_departures(stop_id, country)
        if res:
            return res
    except Exception:
        pass
    return mock_departures(stop_id)


async def broadcast_update(stop_id: str):
    deps = mock_departures(stop_id)
    payload = {"stop_id": stop_id, "departures": deps}
    async with subscriptions_lock:
        sockets = list(subscriptions.get(stop_id, set()))
    for ws in sockets:
        try:
            await ws.send_json({"type": "update", "data": payload})
        except Exception:
            pass


async def poller_loop():
    # simple poller that every 10s broadcasts to subscribed stops
    while True:
        await asyncio.sleep(10)
        async with subscriptions_lock:
            stop_ids = list(subscriptions.keys())
        for sid in stop_ids:
            await broadcast_update(sid)


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(poller_loop())


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    client_subs: Set[str] = set()
    try:
        while True:
            msg = await ws.receive_json()
            action = msg.get("action")
            if action == "subscribe":
                stop_id = msg.get("stop_id")
                if not stop_id:
                    continue
                async with subscriptions_lock:
                    subscriptions.setdefault(stop_id, set()).add(ws)
                client_subs.add(stop_id)
                # send immediate snapshot
                await ws.send_json({"type": "snapshot", "data": {"stop_id": stop_id, "departures": mock_departures(stop_id)}})
            elif action == "unsubscribe":
                stop_id = msg.get("stop_id")
                if not stop_id:
                    continue
                async with subscriptions_lock:
                    if stop_id in subscriptions:
                        subscriptions[stop_id].discard(ws)
                        if not subscriptions[stop_id]:
                            subscriptions.pop(stop_id, None)
                client_subs.discard(stop_id)
            else:
                # ignore unknown
                pass
    except WebSocketDisconnect:
        # cleanup
        async with subscriptions_lock:
            for sid in list(client_subs):
                if sid in subscriptions:
                    subscriptions[sid].discard(ws)
                    if not subscriptions[sid]:
                        subscriptions.pop(sid, None)
