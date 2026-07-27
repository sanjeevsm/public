#!/usr/bin/env bash
# One-time setup for PrimeCare+ — creates venvs and installs dependencies.
# Run this once before the first start, or to reset after a clean clone.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

info() { echo "[PRIMECARE] $*"; }
ok()   { echo "[OK]        $*"; }
warn() { echo "[WARN]      $*"; }
err()  { echo "[ERROR]     $*" >&2; exit 1; }

echo ""
echo "  PrimeCare+ Setup"
echo ""

# -- Check Python ----------------------------------------------------------------
PYTHON=""
for cmd in python3 python; do
    if command -v "$cmd" &>/dev/null && "$cmd" -c "import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)" 2>/dev/null; then
        PYTHON="$cmd"
        break
    fi
done
[ -z "$PYTHON" ] && err "Python 3.10+ not found. Install from https://python.org"
info "Using Python: $($PYTHON --version)"

# -- Create runtime directories --------------------------------------------------
mkdir -p data .pids
ok "Runtime directories created (data/, .pids/)"

# -- Copy .env if missing --------------------------------------------------------
if [ ! -f ".env" ]; then
    cp .env.example .env
    warn "Created .env from .env.example — edit DB_PASSWORD before starting"
else
    ok ".env already exists"
fi

# -- API venv --------------------------------------------------------------------
info "Setting up API virtual environment..."
if [ ! -d "api/venv" ]; then
    $PYTHON -m venv api/venv
fi
api/venv/bin/pip install --upgrade pip --quiet
api/venv/bin/pip install -r api/requirements.txt
ok "API dependencies installed"

# -- Web-app venv ----------------------------------------------------------------
info "Setting up web-app virtual environment..."
if [ ! -d "web-app/venv" ]; then
    $PYTHON -m venv web-app/venv
fi
web-app/venv/bin/pip install --upgrade pip --quiet
web-app/venv/bin/pip install -r web-app/requirements.txt
ok "Web-app dependencies installed"

echo ""
echo "Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Edit .env  — set DB_PASSWORD (and DB_HOST/DB_NAME if needed)"
echo "  2. Create DB  — psql -U postgres -f clinic_setup.sql"
echo "  3. Start      — ./scripts/start.sh"
echo ""
