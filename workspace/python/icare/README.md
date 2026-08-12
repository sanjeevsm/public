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

## What's new (Aug 2026)

- Theme presets and global CSS variables: the web UI now supports multiple theme presets (light/dark/brand variants) that apply to the entire interface including tables and cards.
- Schedule CRUD: doctor creation and a dedicated Schedules screen support creating, editing and deleting doctor schedules. The web form posts schedule rows after doctor creation when provided.
- Appointment booking improvements: the booking UI defaults to a 10-minute slot and provides a dropdown time selector. The server validates that booked times fall within a doctor's schedule and prevents overlapping appointments.
- Availability API: new endpoint `GET /doctors/<id>/available_slots` returns available time slots for a doctor for a given date and slot length.
- Delete protections: deleting a doctor or patient is blocked by the API when they have pending/future appointments; the API returns HTTP 400 with a helpful message in that case.
- Server-side validation: appointment conflicts and schedule membership checks are enforced on the API side to keep data consistent when using the web UI or direct API calls.

If you're running locally, use the `dev` branch in the `public` repo for these changes. See the project README and `web-app/` templates for example usage and screenshots.
