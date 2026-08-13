#!/usr/bin/env bash
# Stops iCare+ servers by reading PIDs written by start.sh.
set -uo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

ok()   { echo "[OK]        $*"; }
warn() { echo "[WARN]      $*"; }

stop_pid() {
    local name="$1"
    local pidfile=".pids/$name.pid"
    if [ -f "$pidfile" ]; then
        local pid
        pid=$(cat "$pidfile")
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid" 2>/dev/null || true
            sleep 1
            kill -0 "$pid" 2>/dev/null && kill -9 "$pid" 2>/dev/null || true
            ok "$name stopped (PID $pid)"
        else
            warn "$name is not running (stale PID $pid)"
        fi
        rm -f "$pidfile"
    else
        warn "$name is not running (no PID file)"
    fi
}

echo ""
stop_pid web
stop_pid api

# Flask debug mode spawns a reloader child that survives parent termination.
# Sweep for any orphaned icare processes by matching the venv paths.
sweep_orphans() {
    local pattern="$1"
    local found=false
    while IFS= read -r line; do
        local opid
        opid=$(echo "$line" | awk '{print $1}')
        if [ -n "$opid" ] && kill -0 "$opid" 2>/dev/null; then
            kill -9 "$opid" 2>/dev/null || true
            echo "[WARN]      Cleaned up orphan process (PID $opid)"
            found=true
        fi
    done < <(pgrep -af "$pattern" 2>/dev/null || true)
    $found || true
}

sweep_orphans "icare/api/venv"
sweep_orphans "icare/web-app/venv"

echo ""
echo "Done."
echo ""
