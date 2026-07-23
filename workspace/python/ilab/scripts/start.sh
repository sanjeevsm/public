#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

info() { echo "[iLab+] $*"; }
ok()   { echo "[OK]    $*"; }
warn() { echo "[WARN]  $*"; }
err()  { echo "[ERROR] $*" >&2; exit 1; }

echo ""
echo "  iLab+  AI Interview Simulator"
echo ""

# -- Check for a running instance
mkdir -p .pids
PID_FILE="$ROOT/.pids/app.pid"

if [ -f "$PID_FILE" ]; then
    existing=$(cat "$PID_FILE")
    if kill -0 "$existing" 2>/dev/null; then
        warn "iLab+ is already running (PID $existing)"
        warn "Run ./scripts/stop.sh first, or delete .pids/app.pid to force a fresh start."
        exit 0
    else
        warn "Stale PID file found ($existing) - cleaning up"
        rm -f "$PID_FILE"
    fi
fi

# -- Python prerequisite
info "Checking Python installation..."
if ! command -v python3 &>/dev/null; then
    err "python3 not found on PATH. Install Python 3.10+ and retry."
fi
ok "Found $(python3 --version)"

# -- Virtual environment
VENV_DIR="$ROOT/.venv"
VENV_PYTHON="$VENV_DIR/bin/python"
VENV_PIP="$VENV_DIR/bin/pip"

if [ ! -f "$VENV_PYTHON" ]; then
    info "Creating virtual environment at .venv ..."
    python3 -m venv "$VENV_DIR"
    [ -f "$VENV_PYTHON" ] || err "Failed to create virtual environment. Check Python installation."
    ok "Virtual environment created"
fi

# -- Install / verify dependencies
MARKER_FILE="$VENV_DIR/.deps_installed"
REQ_FILE="$ROOT/requirements.txt"

[ -f "$REQ_FILE" ] || err "requirements.txt not found at $REQ_FILE"

REINSTALL=false
if [ ! -f "$MARKER_FILE" ]; then
    REINSTALL=true
elif [ "$REQ_FILE" -nt "$MARKER_FILE" ]; then
    info "requirements.txt changed - reinstalling dependencies..."
    REINSTALL=true
fi

if [ "$REINSTALL" = "true" ]; then
    info "Installing Python dependencies (this may take a minute on first run)..."
    "$VENV_PIP" install --upgrade pip --quiet
    "$VENV_PIP" install -r "$REQ_FILE"
    touch "$MARKER_FILE"
    ok "Dependencies installed"
else
    ok "Dependencies up to date"
fi

# -- Check tkinter availability (Linux only)
if [ "$(uname -s)" = "Linux" ]; then
    if ! "$VENV_PYTHON" -c "import tkinter" 2>/dev/null; then
        warn "tkinter not available."
        warn "  Ubuntu/Debian: sudo apt-get install python3-tk"
        warn "  Fedora/RHEL:   sudo dnf install python3-tkinter"
        err "Install python3-tk and retry."
    fi
fi

# -- Launch iLab+
info "Launching iLab+ ..."
"$VENV_PYTHON" main.py &
APP_PID=$!
echo $APP_PID > "$PID_FILE"
ok "iLab+ launched (PID $APP_PID)"

# -- Quick alive check
sleep 3
if ! kill -0 "$APP_PID" 2>/dev/null; then
    rm -f "$PID_FILE"
    echo ""
    echo "[ERROR] iLab+ exited immediately."
    echo "        Run manually to see the error:"
    echo "        .venv/bin/python main.py"
    exit 1
fi

echo ""
echo "  iLab+ is running!"
echo "  PID  -> $APP_PID"
echo ""
echo "To stop: ./scripts/stop.sh"
echo ""
