#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

echo "Starting PrimeCare+ Servers..."
echo ""

export DB_PASSWORD="${DB_PASSWORD:-postgres}"

mkdir -p .pids

# -- Start API Server
echo "Starting API Server (Port 5000)..."
"$ROOT/api/venv/bin/python" "$ROOT/api/app.py" \
    >"$ROOT/api.log" 2>"$ROOT/api-error.log" &
echo $! > .pids/api.pid
echo "API Server started (PID $(cat .pids/api.pid))"

sleep 3

# -- Start Web Client
echo "Starting Web Client (Port 5001)..."
"$ROOT/web-app/venv/bin/python" "$ROOT/web-app/client.py" \
    >"$ROOT/web.log" 2>"$ROOT/web-error.log" &
echo $! > .pids/web.pid
echo "Web Client started (PID $(cat .pids/web.pid))"

echo ""
echo "Both servers started!"
echo "API Server: http://localhost:5000"
echo "Web Client: http://localhost:5001"
echo ""
echo "Access the Reports module at: http://localhost:5001/reports"
echo ""
echo "To stop: ./stop_servers.sh"
