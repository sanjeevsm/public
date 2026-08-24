
# iTransit+ — Stateless Public Transport Viewer

A short summary of the primary technologies used: Frontend: React (Vite) · Backend: FastAPI · DB: None (mock providers)

Lightweight stateless frontend + FastAPI backend that queries public-transport provider APIs for nearby stops and live departures. The backend prefers live provider adapters (TfL, TransportAPI, Translink, Traveline, Transport Scotland, Transport for Wales) and falls back to generated mock data when provider keys are not configured.

## Docker (Recommended)

The quickest way to run iTransit+ — no Python, Node.js, or virtualenv setup required.

**Prerequisites:** [Docker Desktop](https://docs.docker.com/get-docker/) (includes Docker Compose)

### Localhost only

```bash
cd itransit

# Optional: add provider API keys
cp .env.example .env   # then edit .env

docker compose up -d
```

### LAN access (other machines on the same network)

`VITE_API_URL` is baked into the frontend bundle at build time — it must be the URL the **browser** uses to reach the backend.

```bash
cd itransit
cp .env.example .env
# Edit .env and set:
#   VITE_API_URL=http://<your-lan-ip>:8003

docker compose build   # rebuilds frontend with the correct API URL
docker compose up -d
```

| URL | Description |
|---|---|
| `http://localhost:3001` | Map UI |
| `http://localhost:8003` | Backend API |

```bash
docker compose down        # stop and remove containers
docker compose logs -f     # follow logs
```

> **Provider API keys** are optional — mock data is returned when keys are absent. Set keys in `.env` for live departures.
>
> **IP changed?** Re-run `docker compose build frontend && docker compose up -d frontend` after updating `VITE_API_URL` in `.env`.

---

## Quick Start (Process-Based)

1. Create a local `.env` from the example and add any provider keys you have (do NOT commit secrets):

```powershell
cd public/workspace/python/itransit
copy .env.example .env
# edit .env and add keys (TFL_APP_KEY etc.)
```

2. Start both services (PowerShell):

```powershell
cd public/workspace/python/itransit/scripts
.\start-all.ps1
```

Or POSIX:

```bash
cd public/workspace/python/itransit/scripts
./start-all.sh
```

3. Stop services:

```powershell
cd public/workspace/python/itransit/scripts
.\stop-all.ps1
```

### Reinstallation (Clean Reset)

The Quick Start above is a **first-time install**: the start scripts create the `.venv/` automatically. Note that the backend does **not** run `pip install` for you (install `backend/requirements.txt` manually the first time), and only the Bash `start-frontend.sh` runs `npm install` automatically — under PowerShell run `npm install` yourself.

For a clean reinstall (corrupted venv, dependency changes, or a pristine slate):

1. Stop both services:

   ```bash
   ./scripts/stop-all.sh          # Windows: .\scripts\stop-all.ps1
   ```

2. Delete the environments and runtime artifacts:

   ```bash
   # macOS / Linux
   rm -rf .venv frontend/node_modules logs .pids
   find backend -type d -name __pycache__ -prune -exec rm -rf {} +
   ```

   ```powershell
   # Windows (PowerShell)
   Remove-Item -Recurse -Force .venv, frontend\node_modules, logs, .pids -ErrorAction SilentlyContinue
   Get-ChildItem backend -Recurse -Directory -Filter __pycache__ | Remove-Item -Recurse -Force
   ```

   Keep `.env` to preserve your provider API keys, or delete it and re-copy from `.env.example` for a full reset. This project has no database, so there is nothing else to clear.

3. Recreate the backend environment, reinstall, and start:

   ```bash
   python -m venv .venv
   . .venv/bin/activate          # Windows: .venv\Scripts\Activate.ps1
   pip install -r backend/requirements.txt
   ./scripts/start-all.sh         # Windows: .\scripts\start-all.ps1 (run "npm install" in frontend/ first)
   ```

## Runtime layout

- Backend: `backend/` — FastAPI app listening on port `8003` by default.
-- Frontend: `frontend/` — Vite + React app (dev port `3001`).
- Scripts: `scripts/` — centralized cross-platform helpers: `start-all.*`, `stop-all.*`, `start-backend.*`, `start-frontend.*`.
- Env: `.env.example` contains placeholders; copy to `.env` locally.

## API endpoints

- GET `/api/countries` — list of supported countries. Example response: `["England","Scotland","Wales","Northern Ireland"]`.
- GET `/api/stops/nearby?lat={lat}&lon={lon}&radius={m}&country={country}` — returns nearby stops from provider(s) or mock data. Example query:

  ```bash
  curl 'http://127.0.0.1:8003/api/stops/nearby?lat=51.5074&lon=-0.1278&country=England'
  ```

- GET `/api/stops/{stop_id}/departures?country={country}` — returns departures for a `stop_id`. Example:

  ```bash
  curl 'http://127.0.0.1:8003/api/stops/490014585N/departures?country=England'
  ```

- WebSocket `/ws` — simple pub/sub channel. Client messages:
  - `{"action":"subscribe","stop_id":"<stop_id>"}` — subscribe to updates for a stop.
  - `{"action":"unsubscribe","stop_id":"<stop_id>"}` — unsubscribe.

  Server sends `snapshot` (initial departures) and periodic `update` messages with `{"type":"update","data":{...}}`.

## Environment variables (in `.env`)

-- `VITE_API_URL` — frontend uses this to locate the backend (default `http://localhost:8003`).
- `ENABLE_SCRAPING` — if `true`, allows scraping fallback (disabled by default).
- `TFL_APP_KEY` — TfL API key (optional: many TfL endpoints work without a key but keys increase rate limits).
- `TRANSPORTAPI_APP_ID` / `TRANSPORTAPI_APP_KEY` — TransportAPI credentials (UK-wide aggregator).
- `TRANSLINK_KEY` — Translink developer key (Northern Ireland).
- `TRAVELINE_URL` / `TRAVELINE_KEY` — Traveline regional API base URL and key.
- `TRANSPORTSCOTLAND_URL` / `TRANSPORTSCOTLAND_KEY` — Transport Scotland custom API endpoint and key.
- `TFW_URL` / `TFW_KEY` — Transport for Wales custom API endpoint and key.
- `NATIONALRAIL_USERNAME` / `NATIONALRAIL_PASSWORD` / `NATIONALRAIL_TOKEN` — optional National Rail/OpenLDBWS credentials.

Keys left blank will cause the backend to fall back to `mock_*` providers so the app remains runnable without secrets.

## Example client usage

- Simple curl to list countries:

```bash
curl 'http://127.0.0.1:8003/api/countries'
```

- Fetch nearby stops and show names (jq required):

```bash
curl 'http://127.0.0.1:8003/api/stops/nearby?lat=51.5074&lon=-0.1278&country=England' | jq -r '.[].name'
```

- Subscribe via WebSocket (using `websocat`):

```bash
# install websocat and run
websocat ws://127.0.0.1:8003/ws
# then send: {"action":"subscribe","stop_id":"490014585N"}
```

- Quick JS fetch example (browser console):

```js
fetch('http://127.0.0.1:8003/api/stops/nearby?lat=51.5074&lon=-0.1278&country=England')
  .then(r => r.json()).then(stops => console.log(stops[0]))
```

## Troubleshooting

-- If the frontend fails to start on port `3001`, check the dev server output for the bound port (open `http://localhost:3001/`).
- If provider calls return empty arrays and you expect live data, confirm keys are set in `.env` and restart the backend so environment variables are reloaded.
- To inspect whether the backend attached a TfL key to outgoing requests, check the backend console logs — the TfL adapter logs request params (keys are masked).

## Contributing

 Backend: `backend/` — FastAPI app listening on port `8003` by default.
 Frontend: `frontend/` — Vite + React app (dev port `3001`).

---
# iTransit+

  curl 'http://127.0.0.1:8003/api/stops/nearby?lat=51.5074&lon=-0.1278&country=England'

Quick start (backend):
- create a Python virtualenv and install:
  - `python -m venv .venv`
    curl 'http://127.0.0.1:8003/api/stops/490014585N/departures?country=England'
- run backend: `python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8003 --app-dir backend`

Frontend (dev):

- `VITE_API_URL` — frontend uses this to locate the backend (default `http://localhost:8003`).
- `npm install`
 If the frontend fails to start on port `3001`, check the dev server output for the bound port (open `http://localhost:3001/`).

Notes:
- This scaffold uses mock data; later phases can swap in real transport APIs.
 run backend: `python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8003 --app-dir backend`

Folders:
- `backend/` — FastAPI mock proxy and WebSocket server (no DB)
 `npm run dev` (serves on http://localhost:3001)

Windows PowerShell:
```powershell
cd public\workspace\python\itransit\backend
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8003
```

Frontend (dev):
```powershell
cd public\workspace\python\itransit\frontend
npm install
npm run dev
```

Notes: This scaffold returns mock data so you can run the full app locally without API keys. The backend exposes a WebSocket at `/ws` for real-time arrival updates.
