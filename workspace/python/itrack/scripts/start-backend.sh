#!/usr/bin/env bash
# start-backend.sh — env-driven port + pre-start check for itrack
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT/backend" || exit 1

BACKEND_PORT="${BACKEND_PORT:-8002}"

if [ -f venv/bin/activate ]; then
  source venv/bin/activate
fi

echo "Starting iTrack+ backend on http://localhost:$BACKEND_PORT"

check_and_free_port() {
  local port="$1"
  local pids=""
  if command -v lsof >/dev/null 2>&1; then
    pids=$(lsof -t -iTCP:"$port" -sTCP:LISTEN 2>/dev/null || true)
  elif command -v ss >/dev/null 2>&1; then
    pids=$(ss -ltnp 2>/dev/null | grep ":$port" | sed -n 's/.*pid=\([0-9]*\).*/\1/p' || true)
  fi
  if [ -n "$pids" ]; then
    for pid in $pids; do
      cmd=$(ps -p "$pid" -o args= 2>/dev/null || true)
      echo "Port $port is in use by PID $pid -> $cmd"
    done
    echo "Please stop the above process(es) and retry." >&2
    exit 1
  else
    echo "No listener on port $port"
  fi
}

check_and_free_port "$BACKEND_PORT"

mkdir -p "$REPO_ROOT/logs" "$REPO_ROOT/.pids"

nohup uvicorn app.main:app --host 0.0.0.0 --port "$BACKEND_PORT" --reload \
    >"$REPO_ROOT/logs/backend.log" 2>"$REPO_ROOT/logs/backend-error.log" &
echo $! > "$REPO_ROOT/.pids/backend.pid"

echo "Backend started (PID $(cat "$REPO_ROOT/.pids/backend.pid"))."
echo "  URL:  http://localhost:$BACKEND_PORT"
echo "  Docs: http://localhost:$BACKEND_PORT/docs"
echo "  Logs: $REPO_ROOT/logs/backend.log"
echo "To stop: ./scripts/stop-local.sh"
