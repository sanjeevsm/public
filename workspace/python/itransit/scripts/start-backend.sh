#!/usr/bin/env bash
# start-backend.sh — with env-driven port and pre-start check
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

# Configuration via environment (defaults)
BACKEND_PORT="${BACKEND_PORT:-8003}"

echo "Starting iTransit+ backend on port $BACKEND_PORT"

check_and_free_port() {
  local port="$1"
  local pids=""

  if command -v lsof >/dev/null 2>&1; then
    pids=$(lsof -t -iTCP:"$port" -sTCP:LISTEN 2>/dev/null || true)
  elif command -v ss >/dev/null 2>&1; then
    pids=$(ss -ltnp 2>/dev/null | grep ":$port" | sed -n 's/.*pid=\([0-9]*\).*/\1/p' | head -n1 || true)
  else
    # Fallback to netstat parsing (Linux/Windows compatibility is limited here)
    pids=$(netstat -ltnp 2>/dev/null | grep ":$port" | sed -n 's/.*\s\([0-9]*\)\/.*$/\1/p' | head -n1 || true)
  fi

  if [ -n "$pids" ]; then
    for pid in $pids; do
      cmd=$(ps -p "$pid" -o args= 2>/dev/null || true)
      echo "Found PID $pid listening on $port -> $cmd"
      echo "Port $port is in use by PID $pid -> $cmd"
    done
  else
    echo "No listener found on port $port"
  fi
}

# Ensure venv
if [ ! -d .venv ]; then
  python -m venv .venv
fi
source .venv/bin/activate

check_and_free_port "$BACKEND_PORT"

mkdir -p "$ROOT_DIR/logs" "$ROOT_DIR/.pids"

nohup python -m uvicorn app.main:app --reload --host 0.0.0.0 --port "$BACKEND_PORT" --app-dir app \
    >"$ROOT_DIR/logs/backend.log" 2>"$ROOT_DIR/logs/backend-error.log" &
echo $! > "$ROOT_DIR/.pids/backend.pid"

echo "Backend started (PID $(cat "$ROOT_DIR/.pids/backend.pid"))."
echo "  URL:  http://localhost:$BACKEND_PORT"
echo "  Logs: $ROOT_DIR/logs/backend.log"
echo "To stop: ./scripts/stop-all.sh"
