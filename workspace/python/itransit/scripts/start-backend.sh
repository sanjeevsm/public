#!/usr/bin/env bash
P=$(dirname "$0")
cd "$P/.."
if [ ! -d .venv ]; then
  python -m venv .venv
fi
source .venv/bin/activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 9100 --app-dir app
