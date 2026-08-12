
# iTransit+ — Stateless Public Transport Viewer

Lightweight stateless frontend + FastAPI backend that queries public-transport provider APIs for nearby stops and live departures. The backend prefers live provider adapters (TfL, TransportAPI, Translink, Traveline, Transport Scotland, Transport for Wales) and falls back to generated mock data when provider keys are not configured.

## Quick start (local)

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

## Runtime layout

- Backend: `backend/` — FastAPI app listening on port `9100` by default.
- Frontend: `frontend/` — Vite + React app (dev port `3002`).
- Scripts: `scripts/` — centralized cross-platform helpers: `start-all.*`, `stop-all.*`, `start-backend.*`, `start-frontend.*`.
- Env: `.env.example` contains placeholders; copy to `.env` locally.

## API endpoints

- GET `/api/countries` — list of supported countries. Example response: `["England","Scotland","Wales","Northern Ireland"]`.
- GET `/api/stops/nearby?lat={lat}&lon={lon}&radius={m}&country={country}` — returns nearby stops from provider(s) or mock data. Example query:

  ```bash
  curl 'http://127.0.0.1:9100/api/stops/nearby?lat=51.5074&lon=-0.1278&country=England'
  ```

- GET `/api/stops/{stop_id}/departures?country={country}` — returns departures for a `stop_id`. Example:

  ```bash
  curl 'http://127.0.0.1:9100/api/stops/490014585N/departures?country=England'
  ```

- WebSocket `/ws` — simple pub/sub channel. Client messages:
  - `{"action":"subscribe","stop_id":"<stop_id>"}` — subscribe to updates for a stop.
  - `{"action":"unsubscribe","stop_id":"<stop_id>"}` — unsubscribe.

  Server sends `snapshot` (initial departures) and periodic `update` messages with `{"type":"update","data":{...}}`.

## Environment variables (in `.env`)

- `VITE_API_URL` — frontend uses this to locate the backend (default `http://localhost:9100`).
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
curl 'http://127.0.0.1:9100/api/countries'
```

- Fetch nearby stops and show names (jq required):

```bash
curl 'http://127.0.0.1:9100/api/stops/nearby?lat=51.5074&lon=-0.1278&country=England' | jq -r '.[].name'
```

- Subscribe via WebSocket (using `websocat`):

```bash
# install websocat and run
websocat ws://127.0.0.1:9100/ws
# then send: {"action":"subscribe","stop_id":"490014585N"}
```

- Quick JS fetch example (browser console):

```js
fetch('http://127.0.0.1:9100/api/stops/nearby?lat=51.5074&lon=-0.1278&country=England')
  .then(r => r.json()).then(stops => console.log(stops[0]))
```

## Troubleshooting

- If the frontend fails to start on port `3000`, it will default to `3002` — open `http://localhost:3002/`.
- If provider calls return empty arrays and you expect live data, confirm keys are set in `.env` and restart the backend so environment variables are reloaded.
- To inspect whether the backend attached a TfL key to outgoing requests, check the backend console logs — the TfL adapter logs request params (keys are masked).

## Contributing

- Add provider adapters or improve parsing under `backend/app/transport_providers.py`.
- Keep secrets out of git; only store keys in local `.env`.

---

This README gives the basic runtime and developer usage. For architecture notes, provider-specific parsing details and further tests, see the `backend/` and `frontend/` folders.
# iTransit+

Lightweight, stateless transit arrivals viewer. Server provides mock data and WebSocket updates. Favourites are stored in the browser localStorage only — no server-side persistence.

Quick start (backend):

- create a Python virtualenv and install:
  - `python -m venv .venv`
  - `.venv\Scripts\pip.exe install -r backend/requirements.txt`
- run backend: `python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 9100 --app-dir backend`

Frontend (dev):

- `cd frontend`
- `npm install`
- `npm run dev` (serves on http://localhost:3000)

Notes:
- This scaffold uses mock data; later phases can swap in real transport APIs.
- Favourites live in `localStorage` under key `itransit:favourites`.
# iTransit+

Lightweight, cross-platform transit arrivals app (stateless server). Favourites are stored client-side (localStorage); backend does not persist data.

Folders:
- `backend/` — FastAPI mock proxy and WebSocket server (no DB)
- `frontend/` — React + Vite SPA that stores favourites in `localStorage`

Quick start (backend):

Windows PowerShell:
```powershell
cd public\workspace\python\itransit\backend
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 9100
```

Frontend (dev):
```powershell
cd public\workspace\python\itransit\frontend
npm install
npm run dev
```

Notes: This scaffold returns mock data so you can run the full app locally without API keys. The backend exposes a WebSocket at `/ws` for real-time arrival updates.
