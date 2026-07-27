# PrimeCare+ — Quick Start

## Prerequisites

- Python 3.10+
- PostgreSQL 14+ (running locally)

---

## macOS / Linux

```bash
# 1. Configure
cp .env.example .env
# Open .env and set DB_PASSWORD (and DB_HOST/DB_NAME if not using defaults)

# 2. Create the database (run once)
psql -U postgres -f clinic_setup.sql

# 3. Make scripts executable (run once)
chmod +x scripts/*.sh

# 4. Setup — install dependencies (run once, or after pulling updates)
./scripts/setup.sh

# 5. Start
./scripts/start.sh
```

Opens http://localhost:5001 automatically.

### Stop

```bash
./scripts/stop.sh
```

---

## Windows (PowerShell)

```powershell
# 1. Configure
Copy-Item .env.example .env
# Open .env and set DB_PASSWORD

# 2. Create the database (run once)
psql -U postgres -f clinic_setup.sql

# 3. Setup — install dependencies (run once, or after pulling updates)
.\scripts\setup.ps1

# 4. Start
.\scripts\start.ps1
```

Opens http://localhost:5001 automatically.

### Stop

```powershell
.\scripts\stop.ps1
```

---

## URLs

| URL | Description |
|-----|-------------|
| http://localhost:5001 | Web application |
| http://localhost:5001/reports | Analytics & reports |
| http://localhost:5000 | REST API |

---

## .env reference

```ini
DB_HOST=localhost
DB_PORT=5432
DB_NAME=clinic
DB_USER=postgres
DB_PASSWORD=           # <-- set this
API_PORT=5000
API_URL=http://localhost:5000
WEB_PORT=5001
```

---

## Logs

```
data/api.log          API output
data/api-error.log    API errors / tracebacks
data/web.log          Web app output
data/web-error.log    Web app errors / tracebacks
```

---

## Notes

- `start.sh` / `start.ps1` automatically call setup if venvs are missing — you can skip the setup step on first run.
- The web app talks to the API via `API_URL`. If you change `API_PORT`, also update `API_URL` in `.env`.
- Sample data includes 10 doctors, 10 patients, and 21 appointments so the UI is populated immediately after setup.
