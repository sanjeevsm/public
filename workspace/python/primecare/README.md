# PrimeCare+

A full-stack medical clinic management system for managing doctors, patients, appointments, schedules, and analytics. Built with Flask and PostgreSQL.

## Architecture

| Component | Technology | Default Port |
|-----------|-----------|:---:|
| REST API | Flask + psycopg2 | 5000 |
| Web App | Flask SSR + Chart.js | 5001 |
| Database | PostgreSQL 14+ | 5432 |

The web app is a server-side rendered Flask application that calls the REST API. The REST API connects directly to PostgreSQL with parameterized queries (no ORM).

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| REST API | Python 3.10+, Flask | HTTP endpoints, routing, request/response handling |
| Database driver | psycopg2 | PostgreSQL connectivity; parameterized raw SQL (no ORM) |
| Web frontend | Flask (SSR), Jinja2 | Server-side rendered HTML templates |
| Charts | Chart.js 4 | Reports dashboard — line, bar, and doughnut charts |
| Data export | openpyxl, csv | Multi-sheet Excel, CSV, and JSON export |
| Database | PostgreSQL 14+ | Relational data store |
| Scripts | Bash (.sh), PowerShell (.ps1) | Cross-platform setup / start / stop |
| Testing | Python unittest | Integration test suite covering all API endpoints |

## Features

- **Doctor Management** — Profiles, specialities, weekly recurring schedules, leave tracking
- **Patient Records** — Demographics, visit history, appointment timeline
- **Smart Booking** — Conflict detection, double-booking prevention, leave and schedule validation
- **Case History** — Symptoms, diagnosis, prescriptions, follow-up tracking
- **Reports & Analytics** — KPI dashboard, revenue trends, doctor and speciality performance with Chart.js
- **Data Export** — CSV, JSON, and multi-sheet Excel for appointments, doctors, and revenue

## Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| Python | 3.10+ | [python.org](https://python.org) |
| PostgreSQL | 14+ | [postgresql.org](https://postgresql.org) |

## Quick Start

```bash
# 1. Configure
cp .env.example .env
# edit .env — set DB_PASSWORD at minimum

# 2. Create database
psql -U postgres -f clinic_setup.sql

# 3. Setup (once)
./scripts/setup.sh          # macOS / Linux
.\scripts\setup.ps1         # Windows (PowerShell)

# 4. Start
./scripts/start.sh          # macOS / Linux
.\scripts\start.ps1         # Windows (PowerShell)
```

See [QUICK_START.md](QUICK_START.md) for a condensed step-by-step guide.

## Configuration

All settings are loaded from `.env` at startup:

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_HOST` | `localhost` | PostgreSQL host |
| `DB_PORT` | `5432` | PostgreSQL port |
| `DB_NAME` | `clinic` | Database name |
| `DB_USER` | `postgres` | Database user |
| `DB_PASSWORD` | *(empty)* | Database password — **required** |
| `API_PORT` | `5000` | REST API listening port |
| `API_URL` | `http://localhost:5000` | URL the web app uses to reach the API |
| `WEB_PORT` | `5001` | Web application listening port |

## Scripts

All scripts live in `scripts/` and work on macOS, Linux, and Windows (Git Bash / PowerShell).

| Script | Platform | Purpose |
|--------|----------|---------|
| `scripts/setup.sh` | macOS / Linux | Create venvs, install deps, copy `.env` |
| `scripts/setup.ps1` | Windows | Same as above |
| `scripts/start.sh` | macOS / Linux | Start API + web app; auto-runs setup if needed |
| `scripts/start.ps1` | Windows | Same as above |
| `scripts/stop.sh` | macOS / Linux | Stop servers by PID |
| `scripts/stop.ps1` | Windows | Same as above |

### First run

```bash
chmod +x scripts/*.sh    # macOS / Linux only — make scripts executable
./scripts/setup.sh
./scripts/start.sh
```

### Subsequent runs

```bash
./scripts/start.sh       # start.sh auto-reinstalls deps if requirements files changed
```

## Stopping

```bash
./scripts/stop.sh        # macOS / Linux
.\scripts\stop.ps1       # Windows
```

## Logs

All logs are written to `data/` at startup:

| File | Contents |
|------|---------|
| `data/api.log` | API stdout |
| `data/api-error.log` | API stderr / tracebacks |
| `data/web.log` | Web app stdout |
| `data/web-error.log` | Web app stderr / tracebacks |

## API Reference

### Base URL

```
http://localhost:5000
```

### Endpoints

| Resource | Methods | Path |
|----------|---------|------|
| Specialities | GET, POST, GET/:id, PUT/:id, DELETE/:id | `/specialities` |
| Doctors | CRUD + `/by-speciality/:id` + `/by-slot` | `/doctors` |
| Schedules | CRUD + `/by-doctor/:id` + `/by-speciality/:id` | `/schedules` |
| Patients | CRUD + `/by-doctor/:id` | `/patients` |
| Appointments | CRUD + `/by-doctor/:id` + `/book` | `/appointments` |
| Case History | CRUD | `/case-history` |
| Leaves | GET, POST, DELETE/:id + `/by-doctor/:id` | `/leaves` |
| Reports | Read + export | `/reports/*` |

### Booking an Appointment

```http
POST /appointments/book
Content-Type: application/json

{
  "doctor_id": 1,
  "patient_id": 1,
  "date": "2025-02-10",
  "start_time": "09:00",
  "end_time": "09:30"
}
```

**Validation rules:**
- Patient must exist
- Doctor must be active
- Slot must fall within the doctor's weekly schedule
- Doctor must not be on leave that date
- No other appointment can occupy the same `(doctor_id, date, start_time)`

**Error codes:** `409 Conflict` for double-booking, `422 Unprocessable Entity` for other business-logic failures.

### Reports

| Endpoint | Query Parameters |
|----------|-----------------|
| `GET /reports/summary` | — |
| `GET /reports/appointments` | `start_date`, `end_date`, `doctor_id`, `patient_id`, `status`, `speciality_id` |
| `GET /reports/doctors` | `start_date`, `end_date` |
| `GET /reports/specialities` | `start_date`, `end_date` |
| `GET /reports/patients` | — |
| `GET /reports/revenue` | `start_date`, `end_date`, `group_by=day\|week\|month` |
| `GET /reports/export/<type>` | `format=csv\|json\|excel` — `type`: `appointments`, `doctors`, `revenue` |

### Example: Revenue by month

```bash
curl "http://localhost:5000/reports/revenue?group_by=month&start_date=2024-01-01&end_date=2024-12-31"
```

### Example: Export appointments as Excel

```bash
curl -o appointments.xlsx "http://localhost:5000/reports/export/appointments?format=excel"
```

## Running Tests

The integration test suite requires a running API:

```bash
# macOS / Linux
API_URL=http://localhost:5000 api/venv/bin/python -m unittest api/tests.py -v

# Windows
$env:API_URL = "http://localhost:5000"
api\venv\Scripts\python.exe -m unittest api/tests.py -v
```

Tests cover CRUD for all resources plus appointment booking validation (duplicate, invalid slot, missing patient).

## Database Schema

The `clinic` database has 7 tables:

```
specialities       doctors           doctor_schedules
patients           appointments      case_history
doctor_leaves
```

Schema and sample data (8 specialities, 10 doctors, 10 patients, 21 appointments) are in `clinic_setup.sql`.

To recreate:

```bash
psql -U postgres -c "DROP DATABASE IF EXISTS clinic;"
psql -U postgres -f clinic_setup.sql
```

## Project Structure

```
primecare/
├── .env                    # Local config (gitignored)
├── .env.example            # Config template
├── clinic_setup.sql        # PostgreSQL schema + sample data
├── scripts/
│   ├── setup.sh / setup.ps1    # One-time setup
│   ├── start.sh / start.ps1    # Start servers
│   └── stop.sh  / stop.ps1     # Stop servers
├── api/
│   ├── app.py              # Flask REST API (all endpoints)
│   ├── requirements.txt
│   ├── tests.py            # Integration test suite
│   └── venv/               # Python venv (gitignored)
├── web-app/
│   ├── client.py           # Flask SSR web application
│   ├── requirements.txt
│   ├── *.html              # Jinja2 templates
│   └── venv/               # Python venv (gitignored)
└── data/                   # Runtime logs (gitignored)
```

## Troubleshooting

**API fails to start**
Check `data/api-error.log`. Most common cause is incorrect `DB_PASSWORD` in `.env` or PostgreSQL not running.

```bash
# Verify database connectivity
psql -h localhost -U postgres -d clinic -c "SELECT COUNT(*) FROM doctors"
```

**Web app shows connection errors**
Verify the API is reachable:
```bash
curl http://localhost:5000/specialities
```

**Port already in use**
```bash
./scripts/stop.sh    # clear stale processes
./scripts/start.sh   # restart
```

**Permission denied on scripts (macOS / Linux)**
```bash
chmod +x scripts/*.sh
```
