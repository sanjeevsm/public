# GitLab CI/CD Dashboard

A real-time GitLab CI/CD metrics dashboard built with Python FastAPI and a single-page application frontend. Connects directly to the GitLab REST API - no Prometheus or Grafana required.

## Architecture

```
GitLab API (your-gitlab-instance.example.com)
        |
        v  httpx (async, TTL-cached)
CI/CD Dashboard API  :8090  (Python FastAPI)
        |
        v  WebSocket + REST
Browser SPA  (Chart.js, dark/light theme)
```

## Sections

| Section | Content |
|---|---|
| **Overview** | KPI cards + pipeline trend chart + status donut + branch overview + recent MRs + recent deployments |
| **Pipelines** | Recent pipelines table with status, branch, duration |
| **Jobs** | Top failing jobs chart + stage breakdown + recent jobs |

## Prerequisites

| Requirement | Notes |
|---|---|
| **Python 3.11+** | [Download](https://python.org). Add to PATH during install. |
| **PowerShell 5.1+** | Pre-installed on Windows 10/11 |
| **GitLab Personal Access Token** | Scopes: `api`, `read_repository` |

---

## Quick Start

### Step 1 - Create a GitLab Personal Access Token

Go to: `https://<your-gitlab-host>/-/user_settings/personal_access_tokens`

Create a token with scopes: `api`, `read_api`, `read_repository`

### Step 2 - Setup (first time only)

```powershell
cd <path-to-project>
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\scripts\setup.ps1
```

Then edit `.env` and set your token:

```powershell
notepad .env
```

```ini
GITLAB_URL=https://your-gitlab-instance.example.com
GITLAB_TOKEN=your_token_here
GITLAB_PROJECT_IDS=          # leave empty for all your projects
GITLAB_PROJECT_LIMIT=20
APP_PORT=8090
```

### Step 3 - Start

```powershell
.\scripts\start.ps1
```

The dashboard and API docs open automatically in your browser.

### Step 4 - Stop

```powershell
.\scripts\stop.ps1
```

---

## URLs

| URL | Description |
|---|---|
| http://localhost:8090 | Dashboard |
| http://localhost:8090/api/docs | Swagger UI |
| http://localhost:8090/health | Health check |

---

## Configuration (.env)

| Variable | Default | Description |
|---|---|---|
| `GITLAB_URL` | *(required)* | GitLab instance URL |
| `GITLAB_TOKEN` | *(required)* | Personal Access Token |
| `GITLAB_PROJECT_IDS` | *(empty)* | Comma-separated project IDs; empty = all member projects |
| `GITLAB_PROJECT_LIMIT` | `20` | Max projects when using auto-discovery |
| `APP_PORT` | `8090` | Dashboard port |
| `LOG_LEVEL` | `info` | Log verbosity |
| `CACHE_TTL` | `60` | API response cache duration in seconds |

---

## Troubleshooting

**Dashboard shows empty data**
- Confirm `GITLAB_TOKEN` is set in `.env`
- Verify the token has `api` scope
- Check logs: `data\api.log` and `data\api-error.log`

**Port already in use**
```powershell
netstat -ano | findstr :8090
taskkill /PID <pid> /F
```

**Python dependency errors**
```powershell
.\scripts\setup.ps1
```

---

## Folder Structure

```
python/cicd/
├── .env.example
├── .gitignore
├── README.md
├── dashboard_api/
│   ├── config.py
│   ├── main.py
│   ├── requirements.txt
│   ├── routers/
│   │   ├── overview.py        GET /api/overview
│   │   ├── pipelines.py       GET /api/pipelines/*
│   │   ├── jobs.py            GET /api/jobs/*
│   │   ├── mergerequests.py   GET /api/mrs/*
│   │   ├── deployments.py     GET /api/deployments/*
│   │   ├── branches.py        GET /api/branches/*
│   │   ├── export.py          GET /api/export/*
│   │   └── ws.py              WS  /ws/metrics
│   ├── services/
│   │   ├── gitlab_client.py   async GitLab API client with TTL cache
│   │   └── exporter.py        CSV / JSON / Excel / PDF export
│   └── static/
│       ├── index.html
│       ├── css/styles.css
│       └── js/app.js
└── scripts/
    ├── setup.ps1
    ├── start.ps1
    └── stop.ps1
```

Runtime directories (git-ignored):

```
data\            - API and error logs
exports\         - downloaded report files
.pids\           - process PID file for stop.ps1
dashboard_api\.venv\  - Python virtual environment
```

## Export Formats

All export endpoints support `?days=30` to control the data window.

| Format | Endpoint | Sheets / Content |
|---|---|---|
| CSV | `/api/export/csv` | Pipelines |
| JSON | `/api/export/json` | All data with metadata envelope |
| Excel | `/api/export/excel` | Pipelines, Merge Requests |
| PDF | `/api/export/pdf` | Pipelines table |
