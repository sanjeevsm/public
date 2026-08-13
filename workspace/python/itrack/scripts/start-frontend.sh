#!/usr/bin/env bash
# start-frontend.sh — env-driven port + pre-start check for itrack
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT/frontend" || exit 1

FRONTEND_PORT="${FRONTEND_PORT:-3000}"

echo "Starting iTrack+ frontend on http://localhost:$FRONTEND_PORT"

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
		echo "No listener on port $port"
	fi
}

check_and_free_port "$FRONTEND_PORT"

npm run dev -- --port "$FRONTEND_PORT"
