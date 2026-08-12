#!/usr/bin/env bash
# Starts iLab+ in desktop GUI mode (default) or web server mode (--web).
# Usage: start.sh [--web | --desktop] [--port PORT]
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

info() { printf '\033[0;36m[iLab+] %s\033[0m\n' "$*"; }
ok()   { printf '\033[0;32m[OK]    %s\033[0m\n' "$*"; }
warn() { printf '\033[0;33m[WARN]  %s\033[0m\n' "$*"; }
err()  { printf '\033[0;31m[ERROR] %s\033[0m\n' "$*" >&2; exit 1; }

# -- Parse arguments -----------------------------------------------------------
MODE="desktop"
CLI_PORT=""
while [[ $# -gt 0 ]]; do
    case $1 in
        --web|-w)       MODE="web" ;;
        --desktop|-d)   MODE="desktop" ;;
        --port|-p)      CLI_PORT="$2"; shift ;;
        *) err "Unknown argument: $1  Usage: start.sh [--web|--desktop] [--port PORT]" ;;
    esac
    shift
done

echo ""
echo "  iLab+  AI Interview Simulator  [mode: $MODE]"
echo ""

# -- PID file ------------------------------------------------------------------
mkdir -p .pids
if [ "$MODE" = "web" ]; then
    PID_FILE="$ROOT/.pids/web.pid"
    LOG_FILE="$ROOT/.pids/web.log"
else
    PID_FILE="$ROOT/.pids/app.pid"
fi

if [ -f "$PID_FILE" ]; then
    existing=$(cat "$PID_FILE")
    if kill -0 "$existing" 2>/dev/null; then
        warn "iLab+ ($MODE) is already running (PID $existing)"
        warn "Run ./scripts/stop.sh --$MODE first, or delete .pids/$(basename "$PID_FILE") to force a restart."
        exit 0
    else
        warn "Stale PID file found ($existing) — cleaning up"
        rm -f "$PID_FILE"
    fi
fi

# -- Python prerequisite -------------------------------------------------------
info "Checking Python installation..."
if ! command -v python3 &>/dev/null; then
    err "python3 not found on PATH. Install Python 3.10+ and retry."
fi
ok "Found $(python3 --version)"

# -- Virtual environment -------------------------------------------------------
VENV_DIR="$ROOT/.venv"
VENV_PYTHON="$VENV_DIR/bin/python"
VENV_PIP="$VENV_DIR/bin/pip"

if [ ! -f "$VENV_PYTHON" ]; then
    info "Creating virtual environment at .venv ..."
    python3 -m venv "$VENV_DIR"
    [ -f "$VENV_PYTHON" ] || err "Failed to create virtual environment."
    ok "Virtual environment created"
fi

# -- Dependencies --------------------------------------------------------------
if [ "$MODE" = "web" ]; then
    REQ_FILE="$ROOT/requirements-web.txt"
    MARKER_FILE="$VENV_DIR/.web_deps_installed"
else
    REQ_FILE="$ROOT/requirements.txt"
    MARKER_FILE="$VENV_DIR/.desktop_deps_installed"
fi

[ -f "$REQ_FILE" ] || err "$(basename "$REQ_FILE") not found at $REQ_FILE"

REINSTALL=false
if [ ! -f "$MARKER_FILE" ]; then
    REINSTALL=true
elif [ "$REQ_FILE" -nt "$MARKER_FILE" ]; then
    info "$(basename "$REQ_FILE") changed — reinstalling dependencies..."
    REINSTALL=true
fi

if [ "$REINSTALL" = "true" ]; then
    info "Installing Python dependencies (may take a minute on first run)..."
    "$VENV_PIP" install --upgrade pip --quiet
    "$VENV_PIP" install -r "$REQ_FILE"
    touch "$MARKER_FILE"
    ok "Dependencies installed"
else
    ok "Dependencies up to date"
fi

# -- Desktop mode --------------------------------------------------------------
if [ "$MODE" = "desktop" ]; then

    # Tkinter check (Linux only — macOS ships it, Windows uses pythonw.exe path below)
    if [ "$(uname -s)" = "Linux" ]; then
        if ! "$VENV_PYTHON" -c "import tkinter" 2>/dev/null; then
            warn "tkinter not available."
            warn "  Ubuntu/Debian: sudo apt-get install python3-tk"
            warn "  Fedora/RHEL:   sudo dnf install python3-tkinter"
            err "Install python3-tk and retry."
        fi
    fi

    info "Launching iLab+ desktop app ..."
    "$VENV_PYTHON" main.py &
    APP_PID=$!
    echo "$APP_PID" > "$PID_FILE"
    ok "Desktop app launched (PID $APP_PID)"

    sleep 3
    if ! kill -0 "$APP_PID" 2>/dev/null; then
        rm -f "$PID_FILE"
        echo ""
        err "iLab+ exited immediately. Run manually to see the error: .venv/bin/python main.py"
    fi

    echo ""
    echo "  iLab+ desktop is running!"
    echo "  PID -> $APP_PID"
    echo ""
    echo "  To stop: ./scripts/stop.sh"
    echo ""

# -- Web mode ------------------------------------------------------------------
else

    # Load .env if present (does not override variables already in the environment)
    ENV_FILE="$ROOT/.env"
    if [ -f "$ENV_FILE" ]; then
        set -a
        # shellcheck source=/dev/null
        source "$ENV_FILE"
        set +a
        ok "Loaded .env"
    else
        warn ".env not found — copy .env.example to .env to configure ILAB_SECRET and PORT"
    fi

    # Resolve port: CLI flag > .env/PORT > default 8001
    if [ -n "$CLI_PORT" ]; then
        PORT="$CLI_PORT"
    elif [ -n "${PORT:-}" ]; then
        : # already set by .env
    else
        PORT=8001
    fi
    export PORT

    # Resolve bind host: .env HOST > default 0.0.0.0 (all interfaces = LAN accessible)
    HOST="${HOST:-0.0.0.0}"
    export HOST

        check_and_free_port() {
            local port="$1"
            if command -v lsof >/dev/null 2>&1; then
                pids=$(lsof -t -iTCP:"$port" -sTCP:LISTEN 2>/dev/null || true)
            else
                pids=$(netstat -aon 2>/dev/null | grep ":$port " | sed -n 's/.* \([0-9]*\)$/\1/p' || true)
            fi
            if [ -n "$pids" ]; then
                for pid in $pids; do
                    cmd=$(ps -p "$pid" -o args= 2>/dev/null || true)
                    echo "Port $port is in use by PID $pid -> $cmd"
                done
                echo "Please stop the above process(es) and retry." >&2
                exit 1
            fi
        }

    # Warn if session secret is unset (flask_app.py auto-generates one, but
    # every restart will invalidate in-flight sessions)
    if [ -z "${ILAB_SECRET:-}" ]; then
        warn "ILAB_SECRET is not set — a random secret is generated each restart."
        warn "User sessions are lost on restart. Set ILAB_SECRET in .env to persist them."
    fi

    GUNICORN="$VENV_DIR/bin/gunicorn"

    if [ -x "$GUNICORN" ]; then
        info "Starting iLab+ web server with Gunicorn on $HOST:$PORT ..."
        check_and_free_port "$PORT"
        # Single worker required — TTLStore is process-local.
        # See wsgi.py for notes on upgrading to multi-worker with Redis.
        nohup "$GUNICORN" \
            --workers 1 \
            --bind "$HOST:$PORT" \
            --timeout 120 \
            --access-logfile - \
            --error-logfile - \
            wsgi:application >> "$LOG_FILE" 2>&1 &
        WEB_PID=$!
    else
        warn "gunicorn not found — falling back to Flask built-in server (NOT for production)."
        warn "Install gunicorn: .venv/bin/pip install gunicorn"
        info "Starting Flask built-in server on $HOST:$PORT ..."
        check_and_free_port "$PORT"
        HOST="$HOST" FLASK_DEBUG=0 nohup "$VENV_PYTHON" flask_app.py >> "$LOG_FILE" 2>&1 &
        WEB_PID=$!
    fi

    echo "$WEB_PID" > "$PID_FILE"
    ok "Web server launched (PID $WEB_PID)"

    sleep 2
    if ! kill -0 "$WEB_PID" 2>/dev/null; then
        rm -f "$PID_FILE"
        echo ""
        echo "  Last log output:"
        tail -20 "$LOG_FILE" 2>/dev/null || true
        err "Web server exited immediately. Check $LOG_FILE for details."
    fi

    # Resolve a non-loopback LAN IP to show a usable network URL
    LAN_IP=""
    if command -v ip &>/dev/null; then
        LAN_IP=$(ip route get 1.1.1.1 2>/dev/null | awk '/src/{print $7; exit}')
    elif command -v ipconfig &>/dev/null; then
        LAN_IP=$(ipconfig 2>/dev/null | awk '/IPv4.*[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+/{print $NF}' | grep -v '^127\.' | head -1)
    fi

    echo ""
    echo "  iLab+ web is running!"
    echo "  PID         -> $WEB_PID"
    echo "  Local URL   -> http://127.0.0.1:$PORT"
    if [ -n "$LAN_IP" ]; then
        printf "  \033[0;36mNetwork URL -> http://%s:%s  (share this with others on your LAN)\033[0m\n" "$LAN_IP" "$PORT"
    fi
    echo "  Logs        -> $LOG_FILE"
    echo ""
    echo "  Each user opens the URL in their browser and enters"
    echo "  their own API key in Settings — keys never leave their browser."
    echo ""
    echo "  To stop: ./scripts/stop.sh --web"
    echo ""
fi
