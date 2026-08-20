#!/usr/bin/env bash
# start-frontend.sh — env-driven port and pre-start check
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR/frontend"

FRONTEND_PORT="${FRONTEND_PORT:-3001}"

echo "Starting iTransit+ frontend on port $FRONTEND_PORT"

check_and_free_port() {
	local port="$1"
	local pids=""
	if command -v lsof >/dev/null 2>&1; then
		pids=$(lsof -t -iTCP:"$port" -sTCP:LISTEN 2>/dev/null || true)
	elif command -v ss >/dev/null 2>&1; then
		pids=$(ss -ltnp 2>/dev/null | grep ":$port" | sed -n 's/.*pid=\([0-9]*\).*/\1/p' | head -n1 || true)
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

npm install
check_and_free_port "$FRONTEND_PORT"

mkdir -p "$ROOT_DIR/logs" "$ROOT_DIR/.pids"

nohup npm run dev -- --port "$FRONTEND_PORT" \
    >"$ROOT_DIR/logs/frontend.log" 2>"$ROOT_DIR/logs/frontend-error.log" &
echo $! > "$ROOT_DIR/.pids/frontend.pid"

echo "Frontend started (PID $(cat "$ROOT_DIR/.pids/frontend.pid"))."
echo "  URL:  http://localhost:$FRONTEND_PORT"
echo "  Logs: $ROOT_DIR/logs/frontend.log"
echo "To stop: ./scripts/stop-all.sh"
