# CI/CD Dashboard
A short summary of the primary technologies used: Frontend: Vanilla JS (SPA) · Backend: FastAPI · Monitoring: Prometheus, Grafana

## Quick Start

See the **Installation** section below for platform-specific setup and start commands (Windows / macOS / Linux).

A real-time CI/CD metrics dashboard built with **Python FastAPI** and a single-page application frontend. Supports **GitLab**, **GitHub**, **Bitbucket**, and **Gitea** from a single installation. Provider credentials are stored in the browser — no secrets on the server.

---

## Docker (Recommended)

The quickest way to run cicd — no Python or virtualenv setup required.

**Prerequisites:** [Docker Desktop](https://docs.docker.com/get-docker/) (includes Docker Compose)

```bash
cd cicd

# Optional: customise port or log level
cp .env.example .env   # then edit .env

docker compose up -d
```

| URL | Description |
|---|---|
| `http://localhost:8000` | Dashboard SPA |
| `http://localhost:8000/api/docs` | Swagger UI |
| `http://localhost:8000/health` | Health check |
| `http://localhost:8000/metrics` | Prometheus metrics |

**LAN access:** replace `localhost` with this machine's IP address — the server binds to `0.0.0.0` so no additional config is needed.

```bash
docker compose down          # stop and remove containers
docker compose logs -f cicd  # follow logs
```

> Prometheus and Grafana are not included in the Docker setup. Use the process-based installation (see **Installation** below) if you need the monitoring stack.

---

## Features

### Multi-provider support
Connect to any of the four major Git platforms from a single deployment. Switch providers or configure multiple at once via the browser Settings panel.

| Provider | Pipelines | Jobs | PRs / MRs | Deployments | Branches |
|---|---|---|---|---|---|
| **GitLab** | CI/CD Pipelines | CI Jobs | Merge Requests | Environments | Yes |
| **GitHub** | Actions Runs | Actions Jobs | Pull Requests | Deployments | Yes |
| **Bitbucket** | Pipelines | Pipeline Steps | Pull Requests | Deployments | Yes |
| **Gitea** | Actions Runs | Actions Jobs | Pull Requests | — | Yes |

### Dashboard sections

| Section | Content |
|---|---|
| **Overview** | KPI cards (total pipelines, success rate, failures, running, avg duration, open PRs/MRs, repos) · Pipeline trend line chart · Status distribution donut · PR/MR activity chart · Branch overview table · Recent PRs/MRs table · Recent deployments table |
| **Pipelines** | Recent pipelines / workflow runs with status, branch, duration, commit SHA, triggered-by user |
| **Jobs** | Top failing jobs bar chart · Failures-by-stage chart · Recent jobs table |

### Data features
- **Live updates** via WebSocket — dashboard cards refresh every 30 s without a page reload
- **Date range filter** — 7, 14, 30, 60, or 90 days across all views
- **Auto-refresh** every 60 s while the page is open
- **Dark / Light theme** — persisted in `localStorage`
- **Server-side TTL cache** — reduces API calls; configurable via `CACHE_TTL`
- **Per-user cache isolation** — credential hash in cache key prevents data leakage between users

### Export formats

| Format | Endpoint | Content |
|---|---|---|
| CSV | `GET /api/export/csv` | Pipelines |
| JSON | `GET /api/export/json` | All data with metadata envelope |
| Excel | `GET /api/export/excel` | Pipelines + PRs/MRs (multi-sheet) |
| PDF | `GET /api/export/pdf` | Pipelines table |

All export endpoints accept `?days=N` to control the data window.

### Security model
Credentials (tokens, URLs) live **only in the browser** (`localStorage`). They are sent to the server as HTTP headers on each request and WebSocket query parameters — they are **never written to disk or logged** server-side. Multiple users with different credentials can share a single deployment safely.

### Monitoring (optional)
Prometheus metrics are exposed at `/metrics`. A pre-built Grafana dashboard JSON is included for infrastructure-level monitoring of the API itself (request counts, latency, active WebSocket connections, provider errors).

---

## Architecture

```
Browser (localStorage: token, provider config)
   │  HTTP headers: X-Provider-*, every request
   │  WS query params: ?provider=&token=&...
   ▼
CI/CD Dashboard API  :8000  (Python FastAPI)
   │  httpx (async, per-user TTL cache)
   ▼
Git Provider API
   (GitLab / GitHub / Bitbucket / Gitea)

Optional monitoring:
   Prometheus :9000  ◄── /metrics
   Grafana    :9001  ◄── Prometheus datasource
```

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| API framework | Python 3.11+, FastAPI | Async REST endpoints, WebSocket handler, auto OpenAPI docs |
| ASGI server | Uvicorn | Production ASGI server for FastAPI |
| HTTP client | httpx (async) | Async calls to Git provider APIs with per-user TTL caching |
| Config | pydantic-settings | Typed environment variable parsing from `.env` |
| Frontend | Vanilla JS, HTML/CSS | Single-page application (SPA); no framework dependency |
| Charts | Chart.js | Pipeline trend line, status donut, PR/MR activity charts |
| Real-time | WebSocket (FastAPI) | Live dashboard card refresh every 30 s |
| Monitoring | Prometheus, Grafana | Infrastructure metrics; pre-built Grafana dashboard included |
| Export | openpyxl, reportlab, csv | Multi-sheet Excel, PDF, CSV, and JSON export |
| Scripts | Bash (.sh), PowerShell (.ps1) | Cross-platform setup / start / stop |

---

## Prerequisites

| Requirement | Notes |
|---|---|
| **Python 3.11+** | [python.org](https://python.org) — add to PATH during install |
| **Bash** (macOS / Linux) | Pre-installed |
| **PowerShell 5.1+** (Windows) | Pre-installed on Windows 10 / 11 |
| **Prometheus** *(optional)* | Only needed for the Grafana monitoring dashboard |
| **Grafana** *(optional)* | Only needed for the Grafana monitoring dashboard |

---

## Installation

### Windows

```powershell
# 1. Clone / unzip the project
cd C:\path\to\cicd

# 2. Allow script execution for this session
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# 3. Run setup (creates virtualenv, installs dependencies, copies .env.example)
.\scripts\setup.ps1

# 4. Edit .env — set ports and (if using Grafana) paths to Prometheus/Grafana binaries
notepad .env
```

### macOS

```bash
# 1. Clone / unzip the project
cd /path/to/cicd

# 2. Make scripts executable
chmod +x scripts/start.sh scripts/stop.sh scripts/setup.sh

# 3. Run setup
./scripts/setup.sh

# 4. Edit .env — set ports and (if using Grafana) paths to binaries
nano .env
```

Install Prometheus and Grafana via Homebrew if you want the monitoring stack:

```bash
brew install prometheus grafana
```

Then set in `.env`:

```ini
PROMETHEUS_EXE=/usr/local/bin/prometheus
GRAFANA_EXE=/opt/homebrew/bin/grafana
GRAFANA_ROOT=/opt/homebrew/opt/grafana
```

### Linux

```bash
# 1. Clone / unzip the project
cd /path/to/cicd

# 2. Make scripts executable
chmod +x scripts/start.sh scripts/stop.sh scripts/setup.sh

# 3. Run setup
./scripts/setup.sh

# 4. Edit .env
nano .env
```

Install Prometheus and Grafana (Debian/Ubuntu example):

```bash
# Prometheus
wget https://github.com/prometheus/prometheus/releases/download/v3.x.x/prometheus-3.x.x.linux-amd64.tar.gz
tar xvf prometheus-*.tar.gz
sudo mv prometheus-*/prometheus /usr/local/bin/

# Grafana
sudo apt-get install -y grafana
```

### Reinstallation (Clean Reset)

The steps above are for a **first-time install**. Use the following when you need a clean slate — a corrupted virtualenv, dependency conflicts after a `requirements.txt` change, or stale Prometheus/Grafana data.

1. Stop any running services so no files are locked:

   ```bash
   ./scripts/stop.sh          # Windows: .\scripts\stop.ps1
   ```

2. Remove the generated artifacts:

   ```bash
   # macOS / Linux
   rm -rf dashboard_api/.venv data .pids exports
   find . -type d -name __pycache__ -prune -exec rm -rf {} +
   ```

   ```powershell
   # Windows (PowerShell)
   Remove-Item -Recurse -Force dashboard_api\.venv, data, .pids, exports -ErrorAction SilentlyContinue
   Get-ChildItem -Recurse -Directory -Filter __pycache__ | Remove-Item -Recurse -Force
   ```

   Keep your existing `.env` to preserve configuration. Delete it too for a pristine reset — `setup` recreates it from `.env.example`. Note that removing `data/` also clears the Prometheus time-series database and `data/grafana.db`.

3. Re-run setup, then start:

   ```bash
   ./scripts/setup.sh && ./scripts/start.sh
   ```

> **Dependency-only refresh:** to rebuild just the Python environment without wiping monitoring data, delete only `dashboard_api/.venv` and re-run `setup`.

---

## Configuration

### `.env` — server-side settings only

```ini
# API server port
APP_PORT=8000

# Log level: debug | info | warning | error
LOG_LEVEL=info

# Cache TTL in seconds (per-user, keyed by provider + token hash)
CACHE_TTL=60

# --- Optional monitoring stack ---
PROMETHEUS_PORT=9000
PROMETHEUS_RETENTION=30d
PROMETHEUS_EXE=          # path to prometheus binary

GRAFANA_PORT=9001
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=admin123
GRAFANA_EXE=             # path to grafana binary
GRAFANA_ROOT=            # path to grafana installation directory
```

> Provider credentials (tokens, URLs, project IDs) are **not** in `.env`. They are configured in the browser.

### Browser Settings — provider credentials

Click the **⚙ Settings** button in the top-right corner of the dashboard.

Select your provider tab and fill in:

| Provider | Field | Notes |
|---|---|---|
| **GitLab** | Personal Access Token | Scopes: `api`, `read_api` |
| | GitLab URL | Leave blank for gitlab.com; set for self-hosted |
| | Project IDs | Comma-separated IDs; leave blank to auto-discover |
| | Max Repos | Auto-discovery limit (default: 20) |
| **GitHub** | Personal Access Token | Scopes: `repo`, `read:org` |
| | Organisation / User | Blank = your personal repos |
| | GitHub URL | Leave blank for github.com; set for GHE |
| | Repo Full Names | `org/repo-a, org/repo-b`; blank = auto-discover |
| | Max Repos | Auto-discovery limit (default: 20) |
| **Bitbucket** | App Password | Account → App passwords; scopes: `repository`, `pipelines` |
| | Workspace | Required — your Bitbucket workspace slug |
| | Bitbucket URL | Leave blank for bitbucket.org |
| | Repo Slugs | `workspace/slug`; blank = all workspace repos |
| | Max Repos | Auto-discovery limit (default: 20) |
| **Gitea** | Access Token | From Gitea → Settings → Applications |
| | Gitea URL | Required — your self-hosted Gitea URL |
| | Organisation | Blank = your personal repos |
| | Repo Full Names | `org/repo`; blank = auto-discover |
| | Max Repos | Auto-discovery limit (default: 20) |

Click **Save & Refresh** — credentials are stored in `localStorage` and applied immediately. They are never sent to the server as configuration and never stored outside the browser.

---

## Start

### Windows

```powershell
.\scripts\start.ps1
```

This starts Prometheus, Grafana (if configured), and the FastAPI dashboard. Process IDs are saved in `.pids\` so `stop.ps1` can cleanly shut them down.

### macOS / Linux

```bash
./scripts/start.sh
```

### Dashboard only (no Prometheus / Grafana)

```powershell
# Windows
dashboard_api\.venv\Scripts\uvicorn.exe main:app --host 0.0.0.0 --port 8000 --app-dir dashboard_api

# macOS / Linux
dashboard_api/.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --app-dir dashboard_api
```

Or with environment variables:

```bash
APP_PORT=8000 LOG_LEVEL=info \
  dashboard_api/.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## Access

| URL | Description |
|---|---|
| `http://<host>:8000` | Dashboard SPA |
| `http://<host>:8000/api/docs` | Swagger UI (interactive API docs) |
| `http://<host>:8000/api/redoc` | ReDoc API reference |
| `http://<host>:8000/health` | Health check `{"status":"healthy"}` |
| `http://<host>:8000/metrics` | Prometheus metrics endpoint |
| `http://<host>:9001` | Grafana (if started) |
| `http://<host>:9000` | Prometheus (if started) |

For **network access from other machines** replace `localhost` with the server's IP address or hostname. The FastAPI server binds to `0.0.0.0` by default so it accepts connections on all interfaces.

---

## Stop

### Windows

```powershell
.\scripts\stop.ps1
```

### macOS / Linux

```bash
./scripts/stop.sh
```

---

## Folder Structure

```
cicd/
├── .env.example              # template — copy to .env
├── .gitignore
├── README.md
├── dashboard_api/
│   ├── config.py             # server settings (pydantic-settings)
│   ├── main.py               # FastAPI app, CORS, routes, health
│   ├── metrics.py            # Prometheus instrumentation
│   ├── requirements.txt
│   ├── routers/
│   │   ├── overview.py       GET /api/overview
│   │   ├── pipelines.py      GET /api/pipelines/*
│   │   ├── jobs.py           GET /api/jobs/*
│   │   ├── mergerequests.py  GET /api/mrs/*
│   │   ├── deployments.py    GET /api/deployments/*
│   │   ├── branches.py       GET /api/branches/overview
│   │   ├── export.py         GET /api/export/{csv,json,excel,pdf}
│   │   └── ws.py             WS  /ws/metrics
│   ├── services/
│   │   ├── base_client.py    abstract base class (normalized interface)
│   │   ├── cache.py          shared TTL cache (per-user key)
│   │   ├── gitlab_client.py  GitLab REST API client
│   │   ├── github_client.py  GitHub REST API + Actions client
│   │   ├── bitbucket_client.py  Bitbucket API 2.0 client
│   │   ├── gitea_client.py   Gitea API v1 client
│   │   ├── provider_factory.py  FastAPI Depends() helpers
│   │   └── exporter.py       CSV / JSON / Excel / PDF
│   └── static/
│       ├── index.html
│       ├── css/styles.css
│       └── js/app.js
├── grafana/
│   ├── dashboards/cicd-dashboard.json
│   ├── grafana.ini
│   └── provisioning/
├── prometheus/
│   └── prometheus.yml
└── scripts/
    ├── setup.ps1 / setup.sh
    ├── start.ps1 / start.sh
    └── stop.ps1  / stop.sh
```

Runtime directories (git-ignored):

```
data/               API, Prometheus, Grafana logs
exports/            downloaded export files
.pids/              process PID files for stop scripts
dashboard_api/.venv/   Python virtual environment
```

---

## Troubleshooting

**Dashboard shows no data / "Configure your provider" banner**
- Click ⚙ Settings and enter your provider token
- Verify the token scopes match the requirements for your provider

**403 / 401 errors in browser console**
- Token is expired or missing required scopes
- For GitLab self-hosted: confirm the URL is correct and the instance is reachable

**CORS errors**
- Ensure you access the dashboard via the FastAPI server (`http://host:8000`), not by opening `index.html` directly as a file

**Port already in use**

```powershell
# Windows — find and kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID <pid> /F
```

```bash
# macOS / Linux
lsof -i :8000
kill -9 <pid>
```

**Python dependency errors**

```powershell
.\scripts\setup.ps1   # Windows
./scripts/setup.sh    # macOS / Linux
```

**Logs**

| File | Content |
|---|---|
| `data/api.log` | FastAPI stdout |
| `data/api-error.log` | FastAPI stderr (startup errors, tracebacks) |
| `data/prometheus.log` | Prometheus output |
| `data/grafana.log` | Grafana output |

**WebSocket stays "Connecting…"**
- The API server may not be running — check `data/api-error.log`
- If behind a reverse proxy (nginx, Caddy), ensure WebSocket upgrade headers are forwarded
