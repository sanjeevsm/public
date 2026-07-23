#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

info() { echo "[PrimeCare+] $*"; }
ok()   { echo "[OK]         $*"; }

echo ""
echo "  PrimeCare+ Setup"
echo ""

command -v python3 &>/dev/null || { echo "[ERROR] python3 not found. Install Python 3.8+ and retry."; exit 1; }
ok "Python found: $(python3 --version)"

# -- API venv
if [ ! -d "api/venv" ]; then
    info "Creating API virtual environment at api/venv ..."
    python3 -m venv api/venv
    ok "API virtual environment created"
else
    ok "API virtual environment already exists"
fi
info "Installing API dependencies..."
api/venv/bin/pip install --upgrade pip --quiet
api/venv/bin/pip install -r api/requirements.txt
ok "API dependencies installed"

# -- Web-app venv
if [ ! -d "web-app/venv" ]; then
    info "Creating web-app virtual environment at web-app/venv ..."
    python3 -m venv web-app/venv
    ok "Web-app virtual environment created"
else
    ok "Web-app virtual environment already exists"
fi
info "Installing web-app dependencies..."
web-app/venv/bin/pip install --upgrade pip --quiet
web-app/venv/bin/pip install -r web-app/requirements.txt
ok "Web-app dependencies installed"

echo ""
echo "Setup complete!"
echo "Next steps:"
echo "  1. Ensure PostgreSQL is running and DB_PASSWORD is set"
echo "  2. Run: ./start_servers.sh"
echo ""
