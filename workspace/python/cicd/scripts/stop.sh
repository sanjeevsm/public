#!/usr/bin/env bash
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

stop_pid() {
    local name="$1" file="$ROOT/.pids/$2"
    if [ -f "$file" ]; then
        local pid
        pid=$(cat "$file")
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid"
            echo "[CICD] Stopped $name (PID $pid)"
        else
            echo "[CICD] $name (PID $pid) was not running"
        fi
        rm -f "$file"
    else
        echo "[CICD] No PID file for $name - skipping"
    fi
}

echo "[CICD] Stopping all services..."

stop_pid "CI/CD Dashboard" "api.pid"
stop_pid "Grafana"         "grafana.pid"
stop_pid "Prometheus"      "prometheus.pid"

echo "[CICD] Done."
