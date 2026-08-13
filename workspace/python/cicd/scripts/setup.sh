#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

info() { echo "[Setup] $*"; }
ok()   { echo "[OK]    $*"; }
warn() { echo "[WARN]  $*"; }

echo ""
echo "  CI/CD Dashboard - Setup"
echo ""

# -- Directories
info "Creating directories..."
mkdir -p data/prometheus data/grafana-logs exports .pids
ok "Directories ready"

# -- Python check
if ! command -v python3 &>/dev/null; then
    echo "[ERROR] python3 not found. Install from https://python.org and retry."
    exit 1
fi
ok "Python found: $(python3 --version)"

# -- Virtual environment
if [ ! -d "dashboard_api/.venv" ]; then
    info "Creating venv at dashboard_api/.venv ..."
    python3 -m venv dashboard_api/.venv
    ok "Virtual environment created"
else
    ok "Virtual environment already exists"
fi

info "Installing Python dependencies..."
dashboard_api/.venv/bin/pip install --upgrade pip --quiet
dashboard_api/.venv/bin/pip install -r dashboard_api/requirements.txt
ok "Python dependencies installed"

# -- .env
if [ ! -f ".env" ]; then
    cp .env.example .env
    ok ".env created from .env.example - edit it and set GITLAB_TOKEN"
else
    ok ".env already exists"
fi

echo ""
echo "Setup complete!"
echo "Next steps:"
echo "  1. Edit .env and set GITLAB_TOKEN"
echo "  2. Run: ./scripts/start.sh"
echo ""
