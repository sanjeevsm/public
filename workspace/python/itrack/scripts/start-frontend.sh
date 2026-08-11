#!/usr/bin/env bash

# Start frontend (POSIX) — placed in scripts/
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT/frontend" || exit 1

echo "Frontend server starting on http://localhost:3000"
npm run dev
