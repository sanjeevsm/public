#!/usr/bin/env bash
# Stops iLab+ processes started by start.sh.
# Usage: stop.sh [--desktop | --web]   (default: stops both)
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

info() { printf '\033[0;36m[iLab+] %s\033[0m\n' "$*"; }
ok()   { printf '\033[0;32m[iLab+] %s\033[0m\n' "$*"; }
warn() { printf '\033[0;33m[iLab+] %s\033[0m\n' "$*"; }

# -- Parse arguments -----------------------------------------------------------
STOP_DESKTOP=true
STOP_WEB=true
while [[ $# -gt 0 ]]; do
    case $1 in
        --desktop|-d) STOP_WEB=false ;;
        --web|-w)     STOP_DESKTOP=false ;;
        *) echo "[ERROR] Unknown argument: $1  Usage: stop.sh [--desktop|--web]" >&2; exit 1 ;;
    esac
    shift
done

# -- Helper --------------------------------------------------------------------
stop_pid_file() {
    local label="$1"
    local pid_file="$2"
    if [ -f "$pid_file" ]; then
        local pid
        pid=$(cat "$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid"
            ok "Stopped $label (PID $pid)"
        else
            warn "$label (PID $pid) was not running"
        fi
        rm -f "$pid_file"
    else
        warn "No PID file for $label — skipping"
    fi
}

echo ""
echo "  iLab+  Stopping..."
echo ""

[ "$STOP_DESKTOP" = "true" ] && stop_pid_file "desktop app" "$ROOT/.pids/app.pid"
[ "$STOP_WEB"     = "true" ] && stop_pid_file "web server"  "$ROOT/.pids/web.pid"

echo ""
ok "Done."
echo ""
