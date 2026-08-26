#!/usr/bin/env bash

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
PID_FILE="$ROOT/.streamsource.pid"

info()  { echo -e "${GREEN}[stop]${NC} $*"; }
warn()  { echo -e "${YELLOW}[stop]${NC} $*"; }

STOP_INFRA=false
for arg in "$@"; do
  case $arg in
    --infra) STOP_INFRA=true ;;
    --all)   STOP_INFRA=true ;;
  esac
done

# Stop the application JAR
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
  warn "No PID file found — application may not be running."
fi

# Optionally stop infrastructure
if [ "$STOP_INFRA" = true ]; then
  if command -v docker &>/dev/null; then
    info "Stopping infrastructure containers..."
    docker compose stop zookeeper kafka postgres redis
    info "Infrastructure stopped."
  fi
fi

info "Done. Use --infra or --all to also stop Kafka/PostgreSQL/Redis."
