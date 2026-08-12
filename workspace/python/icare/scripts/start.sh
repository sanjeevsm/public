#!/usr/bin/env bash
# Starts iCare+ API and web app on macOS / Linux / Windows (Git Bash / WSL).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

info() { echo "[ICARE] $*"; }
ok()   { echo "[OK]        $*"; }
warn() { echo "[WARN]      $*"; }
err()  { echo "[ERROR]     $*" >&2; exit 1; }

echo ""
echo "  iCare+"
echo ""

# -- Load .env -------------------------------------------------------------------
if [ ! -f ".env" ]; then
    warn ".env not found — copying from .env.example"
    cp .env.example .env
fi

while IFS='=' read -r key val; do
    [[ "$key" =~ ^[[:space:]]*# ]] && continue
    [[ -z "${key// }" ]] && continue
    export "${key// }"="${val}"
done < .env

API_PORT="${API_PORT:-8004}"
WEB_PORT="${WEB_PORT:-3003}"
API_URL="${API_URL:-http://localhost:$API_PORT}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-clinic}"
DB_USER="${DB_USER:-postgres}"
DB_PASSWORD="${DB_PASSWORD:-}"

[ -z "$DB_PASSWORD" ] && warn "DB_PASSWORD is not set in .env — database connection may fail"

# -- Auto-setup if venvs are missing ---------------------------------------------
if [ ! -d "api/venv" ] || [ ! -d "web-app/venv" ]; then
    info "Virtual environments not found — running setup first..."
    bash "$ROOT/scripts/setup.sh"
fi

# -- Auto-install if deps are stale ----------------------------------------------
if ! api/venv/bin/python -c "import flask, psycopg2" 2>/dev/null; then
    info "Installing API dependencies..."
    api/venv/bin/pip install --quiet -r api/requirements.txt
fi
if ! web-app/venv/bin/python -c "import flask, requests" 2>/dev/null; then
    info "Installing web-app dependencies..."
    web-app/venv/bin/pip install --quiet -r web-app/requirements.txt
fi

mkdir -p .pids data

# -- Clear stale PIDs ------------------------------------------------------------
for svc in api web; do
    pidfile=".pids/$svc.pid"
    if [ -f "$pidfile" ]; then
        old=$(cat "$pidfile")
        if kill -0 "$old" 2>/dev/null; then
            info "Stopping existing $svc (PID $old)..."
            kill "$old" 2>/dev/null || true
            sleep 1
        fi
        rm -f "$pidfile"
    fi
done

# -- Start API -------------------------------------------------------------------
check_and_free_port() {
    local port="$1"
    if command -v lsof >/dev/null 2>&1; then
        pids=$(lsof -t -iTCP:"$port" -sTCP:LISTEN 2>/dev/null || true)
    else
        pids=$(netstat -aon 2>/dev/null | grep ":$port " | sed -n 's/.* \([0-9]*\)$/\1/p' || true)
    fi
    if [ -n "$pids" ]; then
        for pid in $pids; do
            cmd=$(ps -p "$pid" -o args= 2>/dev/null || true)
            echo "Port $port is in use by PID $pid -> $cmd"
        done
        echo "Please stop the above process(es) and retry." >&2
        exit 1
    fi
}

info "Starting iCare+ API on port $API_PORT..."
check_and_free_port "$API_PORT"
DB_HOST="$DB_HOST" DB_PORT="$DB_PORT" DB_NAME="$DB_NAME" \
    DB_USER="$DB_USER" DB_PASSWORD="$DB_PASSWORD" API_PORT="$API_PORT" \
    nohup api/venv/bin/python api/app.py \
        >"$ROOT/data/api.log" 2>"$ROOT/data/api-error.log" &
echo $! > .pids/api.pid
ok "API started (PID $(cat .pids/api.pid))"

# -- Wait for API ----------------------------------------------------------------
info "Waiting for API to be ready..."
sleep 5
for i in $(seq 1 20); do
    if curl -sf --max-time 5 "http://localhost:$API_PORT/specialities" >/dev/null 2>&1; then
        ok "API is ready"
        break
    fi
    [ "$i" -eq 20 ] && err "API did not start after 45 s — check data/api-error.log"
    sleep 2
done

# -- Start web app ---------------------------------------------------------------
info "Starting iCare+ web app on port $WEB_PORT..."
check_and_free_port "$WEB_PORT"
API_URL="$API_URL" WEB_PORT="$WEB_PORT" \
  nohup web-app/venv/bin/python web-app/client.py \
    >"$ROOT/data/web.log" 2>"$ROOT/data/web-error.log" &
echo $! > .pids/web.pid
ok "Web app started (PID $(cat .pids/web.pid))"

# -- Wait for web app ------------------------------------------------------------
info "Waiting for web app to be ready..."
for i in $(seq 1 15); do
    if curl -sf --max-time 5 "http://localhost:$WEB_PORT/specialities" >/dev/null 2>&1; then
        ok "Web app is ready"
        break
    fi
    [ "$i" -eq 15 ] && warn "Web app health check timed out — check data/web-error.log"
    sleep 1
done

echo ""
echo "iCare+ is running!"
echo ""
echo "  Web app  ->  http://localhost:$WEB_PORT"
echo "  Reports  ->  http://localhost:$WEB_PORT/reports"
echo "  API      ->  http://localhost:$API_PORT"
echo ""
echo "To stop: ./scripts/stop.sh"
echo ""

# -- Open browser ----------------------------------------------------------------
case "$(uname -s)" in
    Darwin)  open "http://localhost:$WEB_PORT" ;;
    Linux)   xdg-open "http://localhost:$WEB_PORT" &>/dev/null & disown ;;
esac
