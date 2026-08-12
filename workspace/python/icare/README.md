# iCare+

A full-stack medical clinic management system for managing doctors, patients, appointments, schedules, and analytics. Built with Flask and PostgreSQL.

## Architecture

| Component | Technology | Default Port |
|-----------|-----------|:---:|
| REST API | Flask + psycopg2 | 8004 |
| Web App | Flask SSR + Chart.js | 3003 |
| Database | PostgreSQL 14+ | 5432 |

This project was renamed from PrimeCare+ to iCare+; it maintains the same architecture and features.

## Quick Start

```bash
# 1. Configure
cp .env.example .env
# edit .env — set DB_PASSWORD at minimum

# 2. Create database
psql -U postgres -f clinic_setup.sql

# 3. Setup (once)
./scripts/setup.sh          # macOS / Linux
.\scripts\setup.ps1       # Windows (PowerShell)

# 4. Start
./scripts/start.sh          # macOS / Linux
.\scripts\start.ps1       # Windows (PowerShell)
```

## Configuration

All settings are loaded from `.env` at startup. Defaults: `API_PORT=8004`, `WEB_PORT=3003`.

See the other docs in this folder for reporting and troubleshooting.
