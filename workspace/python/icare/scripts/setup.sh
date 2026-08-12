#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

info() { echo "[ICARE] $*"; }
ok()   { echo "[OK]        $*"; }
warn() { echo "[WARN]      $*"; }
err()  { echo "[ERROR]     $*" >&2; exit 1; }

# Create .env if missing
if [ ! -f ".env" ]; then
    warn ".env not found — copying from .env.example"
    cp .env.example .env
    ok ".env created from .env.example"
fi

# Create virtualenvs and install requirements
if [ ! -d "api/venv" ]; then
    info "Creating API virtualenv..."
    python -m venv api/venv
    api/venv/bin/python -m pip install --upgrade pip
    if [ -f "api/requirements.txt" ]; then
        api/venv/bin/pip install --quiet -r api/requirements.txt
        ok "API dependencies installed"
    else
        warn "api/requirements.txt not found — skip installing API dependencies"
    fi
fi

if [ ! -d "web-app/venv" ]; then
    info "Creating web-app virtualenv..."
    python -m venv web-app/venv
    web-app/venv/bin/python -m pip install --upgrade pip
    if [ -f "web-app/requirements.txt" ]; then
        web-app/venv/bin/pip install --quiet -r web-app/requirements.txt
        ok "web-app dependencies installed"
    else
        warn "web-app/requirements.txt not found — skip installing web-app dependencies"
    fi
fi

ok "Setup complete."
