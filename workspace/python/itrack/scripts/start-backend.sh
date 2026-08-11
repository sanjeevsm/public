#!/usr/bin/env bash

# Start backend (POSIX) — placed in scripts/
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT/backend" || exit 1

if [ -f venv/bin/activate ]; then
  # shellcheck source=/dev/null
  source venv/bin/activate
fi

echo "Backend server starting on http://localhost:8000"
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
