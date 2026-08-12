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
# Linux / macOS
cp .env.example .env
# Windows (PowerShell)
copy .env.example .env
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

## API reference (short)

Base URL: `http://localhost:${API_PORT:-8004}`

- **Specialities**
	- `GET /specialities` — list all specialities
	- `POST /specialities` — create (JSON: `{ "name": "Cardiology", "description": "..." }`)

- **Doctors**
	- `GET /doctors` — list doctors
	- `GET /doctors/<id>` — doctor details (includes schedules)
	- `POST /doctors` — create doctor (JSON: `{ "name": "Dr A", "speciality_id": 1, ... }`)
	- `PUT /doctors/<id>` — update
	- `DELETE /doctors/<id>` — delete (API blocks deletion when pending/future appointments exist)

- **Patients**
	- `GET /patients`, `GET /patients/<id>`, `POST /patients`, `PUT /patients/<id>`, `DELETE /patients/<id>` (delete blocked if pending appointments)

- **Schedules**
	- `GET /doctors/<id>/schedules` — list schedule rows for a doctor
	- `POST /doctors/<id>/schedules` — add schedule rows (JSON array or form rows)
	- `PUT /schedules/<sid>`, `DELETE /schedules/<sid>` — edit / remove a schedule row

- **Appointments**
	- `GET /appointments` — list appointments (query params for doctor/patient/date)
	- `POST /appointments` — create (JSON: `{ "doctor_id":1, "patient_id":1, "date":"YYYY-MM-DD", "time":"HH:MM", "duration":10 }`)
		- Default appointment duration in the UI is 10 minutes; server validates schedule membership and prevents overlap.
	- `DELETE /appointments/<id>` — cancel appointment

- **Availability**
	- `GET /doctors/<id>/available_slots?date=YYYY-MM-DD&slot=10` — returns available slot start-times for the date and slot length (minutes)

Examples (using default ports):

```bash
# List doctors
curl http://localhost:8004/doctors

# Book a 10-minute appointment
curl -X POST -H "Content-Type: application/json" \
	-d '{"doctor_id":1,"patient_id":1,"date":"2026-08-13","time":"09:00","duration":10}' \
	http://localhost:8004/appointments

# Get available slots for doctor 1 on 2026-08-13
curl "http://localhost:8004/doctors/1/available_slots?date=2026-08-13&slot=10"
```

Start the services first using the `scripts/` helpers (`scripts/setup.*`, `scripts/start.*`) as described above.
 
