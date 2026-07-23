#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

info() { echo "[CICD] $*"; }
ok()   { echo "[OK]   $*"; }
warn() { echo "[WARN] $*"; }
err()  { echo "[ERROR] $*" >&2; exit 1; }

echo ""
echo "  CI/CD Dashboard"
echo ""

# -- Load .env
if [ ! -f ".env" ]; then
    warn ".env not found - copying from .env.example"
    cp .env.example .env
fi

while IFS='=' read -r key val; do
    [[ "$key" =~ ^[[:space:]]*# ]] && continue
    [[ -z "${key// }" ]] && continue
    export "${key// }"="${val}"
done < .env

API_PORT="${APP_PORT:-8090}"
PROM_PORT="${PROMETHEUS_PORT:-9091}"
GRAF_PORT="${GRAFANA_PORT:-3001}"
LOG_LEVEL="${LOG_LEVEL:-info}"
PROM_RETAIN="${PROMETHEUS_RETENTION:-30d}"

[ -z "${PROMETHEUS_EXE:-}" ] && err "Set PROMETHEUS_EXE in .env to the path of the prometheus binary"
[ -z "${GRAFANA_EXE:-}" ]    && err "Set GRAFANA_EXE in .env to the path of the grafana binary"
[ -z "${GRAFANA_ROOT:-}" ]   && err "Set GRAFANA_ROOT in .env to the Grafana installation directory"

# -- Prerequisite checks
[ -x "$PROMETHEUS_EXE" ] || err "Prometheus not found or not executable at $PROMETHEUS_EXE"
[ -x "$GRAFANA_EXE" ]    || err "Grafana not found or not executable at $GRAFANA_EXE"

if [ -z "${GITLAB_TOKEN:-}" ] || [ "$GITLAB_TOKEN" = "your_personal_access_token_here" ]; then
    warn "GITLAB_TOKEN is not set in .env - the dashboard will show empty data"
    warn "Edit .env and set a valid Personal Access Token"
fi

# -- Auto-install Python deps if needed
if [ ! -f "dashboard_api/.venv/bin/uvicorn" ]; then
    info "Installing Python dependencies..."
    if [ ! -d "dashboard_api/.venv" ]; then
        python3 -m venv dashboard_api/.venv
    fi
    dashboard_api/.venv/bin/pip install --upgrade pip --quiet
    dashboard_api/.venv/bin/pip install -r dashboard_api/requirements.txt
    [ -f "dashboard_api/.venv/bin/uvicorn" ] || err "pip install completed but uvicorn not found. Check errors above."
    ok "Python dependencies installed"
fi
UVICORN="$ROOT/dashboard_api/.venv/bin/uvicorn"

# -- Create runtime directories
mkdir -p .pids exports data/prometheus data/grafana-logs

# -- Start Prometheus
info "Starting Prometheus on port $PROM_PORT ..."
"$PROMETHEUS_EXE" \
    --config.file="$ROOT/prometheus/prometheus.yml" \
    --storage.tsdb.path="$ROOT/data/prometheus" \
    --storage.tsdb.retention.time="$PROM_RETAIN" \
    --web.listen-address="0.0.0.0:$PROM_PORT" \
    >"$ROOT/data/prometheus.log" 2>"$ROOT/data/prometheus-error.log" &
echo $! > .pids/prometheus.pid
ok "Prometheus started (PID $(cat .pids/prometheus.pid))"

# -- Start Grafana
info "Starting Grafana on port $GRAF_PORT ..."
GRAFANA_ADMIN_USER="${GRAFANA_ADMIN_USER:-admin}"
GRAFANA_ADMIN_PASSWORD="${GRAFANA_ADMIN_PASSWORD:-admin123}"

GF_SERVER_HTTP_PORT="$GRAF_PORT" \
GF_SECURITY_ADMIN_USER="$GRAFANA_ADMIN_USER" \
GF_SECURITY_ADMIN_PASSWORD="$GRAFANA_ADMIN_PASSWORD" \
GF_PATHS_PROVISIONING="$ROOT/grafana/provisioning" \
GF_PATHS_CONFIG="$ROOT/grafana/grafana.ini" \
GF_DASHBOARDS_DEFAULT_HOME_DASHBOARD_PATH="$ROOT/grafana/dashboards/cicd-dashboard.json" \
GF_DATABASE_PATH="$ROOT/data/grafana.db" \
GF_PATHS_LOGS="$ROOT/data/grafana-logs" \
"$GRAFANA_EXE" server --homepath="$GRAFANA_ROOT" \
    >"$ROOT/data/grafana.log" 2>"$ROOT/data/grafana-error.log" &
echo $! > .pids/grafana.pid
ok "Grafana started (PID $(cat .pids/grafana.pid))"

# -- Start FastAPI
info "Starting CI/CD Dashboard API on port $API_PORT ..."
EXPORT_DIR="$ROOT/exports" \
APP_PORT="$API_PORT" \
LOG_LEVEL="$LOG_LEVEL" \
"$UVICORN" main:app --host 0.0.0.0 --port "$API_PORT" \
    >"$ROOT/data/api.log" 2>"$ROOT/data/api-error.log" &
echo $! > .pids/api.pid
ok "CI/CD Dashboard API started (PID $(cat .pids/api.pid))"

# -- Health checks
info "Waiting for services to be healthy..."
sleep 3

wait_health() {
    local url="$1" name="$2" attempts="${3:-20}"
    local i
    for i in $(seq 1 "$attempts"); do
        if curl -sf --max-time 2 "$url" >/dev/null 2>&1; then
            ok "$name is ready"
            return 0
        fi
        sleep 2
    done
    warn "$name did not respond at $url - check logs in data/"
}

wait_health "http://localhost:$PROM_PORT/-/ready"    "Prometheus"
wait_health "http://localhost:$GRAF_PORT/api/health" "Grafana"
wait_health "http://localhost:$API_PORT/health"      "CI/CD Dashboard"

echo ""
echo "CI/CD Dashboard is running!"
echo "  Dashboard  -> http://localhost:$API_PORT"
echo "  Grafana    -> http://localhost:$GRAF_PORT"
echo "  Prometheus -> http://localhost:$PROM_PORT"
echo "  API Docs   -> http://localhost:$API_PORT/api/docs"
echo "  Metrics    -> http://localhost:$API_PORT/metrics"
echo ""
echo "To stop: ./scripts/stop.sh"
echo ""

# -- Open browser
info "Opening dashboards in browser..."
case "$(uname -s)" in
    Darwin)
        open "http://localhost:$API_PORT"
        sleep 1
        open "http://localhost:$GRAF_PORT"
        sleep 1
        open "http://localhost:$PROM_PORT"
        ;;
    Linux)
        xdg-open "http://localhost:$API_PORT" &>/dev/null & disown
        sleep 1
        xdg-open "http://localhost:$GRAF_PORT" &>/dev/null & disown
        sleep 1
        xdg-open "http://localhost:$PROM_PORT" &>/dev/null & disown
        ;;
esac
