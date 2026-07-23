#!/usr/bin/env bash
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

PID_FILE="$ROOT/.pids/app.pid"

echo "[iLab+] Stopping iLab+ ..."

if [ -f "$PID_FILE" ]; then
    pid=$(cat "$PID_FILE")
    if kill -0 "$pid" 2>/dev/null; then
        kill "$pid"
        echo "[iLab+] Stopped iLab+ App (PID $pid)"
    else
        echo "[iLab+] iLab+ App (PID $pid) was not running"
    fi
    rm -f "$PID_FILE"
else
    echo "[iLab+] No PID file for iLab+ App - skipping"
fi

echo "[iLab+] Done."
