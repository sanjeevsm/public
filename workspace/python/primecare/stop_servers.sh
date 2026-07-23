#!/usr/bin/env bash
ROOT="$(cd "$(dirname "$0")" && pwd)"

stop_pid() {
    local name="$1" file="$ROOT/.pids/$2"
    if [ -f "$file" ]; then
        local pid
        pid=$(cat "$file")
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid"
            echo "[PrimeCare+] Stopped $name (PID $pid)"
        else
            echo "[PrimeCare+] $name (PID $pid) was not running"
        fi
        rm -f "$file"
    else
        echo "[PrimeCare+] No PID file for $name - skipping"
    fi
}

echo "[PrimeCare+] Stopping all services..."

stop_pid "API Server" "api.pid"
stop_pid "Web Client" "web.pid"

echo "[PrimeCare+] Done."
