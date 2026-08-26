#!/usr/bin/env bash

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PID_FILE="$ROOT/.istream.pid"

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
info() { echo -e "${GREEN}[stop-local]${NC} $*"; }
warn() { echo -e "${YELLOW}[stop-local]${NC} $*"; }

if [ -f "$PID_FILE" ]; then
  PID=$(cat "$PID_FILE")
  if kill -0 "$PID" 2>/dev/null; then
    info "Stopping application (PID $PID)..."
    kill "$PID"
    sleep 3
    kill -0 "$PID" 2>/dev/null && kill -9 "$PID" && info "Force-killed."
    info "Application stopped."
  else
    warn "No process found for PID $PID."
  fi
  rm -f "$PID_FILE"
else
  warn "No PID file found -- application may not be running."
fi
