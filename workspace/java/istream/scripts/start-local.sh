#!/usr/bin/env bash
set -e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; CYAN='\033[0;36m'; NC='\033[0m'
PID_FILE="$ROOT/.istream.pid"

info()  { echo -e "${GREEN}[start-local]${NC} $*"; }
warn()  { echo -e "${YELLOW}[start-local]${NC} $*"; }
error() { echo -e "${RED}[start-local]${NC} $*"; exit 1; }
link()  { echo -e "${CYAN}  $*${NC}"; }

# Resolve JDK via JAVA_HOME
JAVA_EXE="java"
if [ -n "$JAVA_HOME" ] && [ -x "$JAVA_HOME/bin/java" ]; then
  JAVA_EXE="$JAVA_HOME/bin/java"
  info "Using Java from JAVA_HOME: $JAVA_HOME"
fi

# Guard: already running
if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
  warn "Already running (PID $(cat "$PID_FILE")). Run ./scripts/stop-local.sh first."
  exit 0
fi

# Find JAR
JAR=$(ls "$ROOT"/istream-app/target/istream-app-*.jar 2>/dev/null | head -1)
[ -z "$JAR" ] && error "JAR not found. Run: ./mvnw clean package -DskipTests"

# Load .env
[ -f "$ROOT/.env" ] && { set -a; source "$ROOT/.env"; set +a; }

export DB_URL="jdbc:postgresql://localhost:5432/istream"
export DB_USER="${DB_USER:-istream}"
export DB_PASSWORD="${DB_PASSWORD:-istream}"
export SERVER_PORT="${SERVER_PORT:-8080}"
export JWT_SECRET="${JWT_SECRET:-dev-secret-change-in-production-minimum-32-chars}"

mkdir -p "$ROOT/logs"

info "Starting iStream+ (local mode)..."
nohup "$JAVA_EXE" \
  -XX:MaxRAMPercentage=75.0 \
  -Djava.security.egd=file:/dev/./urandom \
  -jar "$JAR" \
  --spring.profiles.active=local \
  > "$ROOT/logs/istream.log" 2>&1 &

APP_PID=$!
echo "$APP_PID" > "$PID_FILE"
info "PID $APP_PID saved. Logs: logs/istream.log"

# Wait for readiness
info "Waiting for application to be ready..."
for i in $(seq 1 30); do
  if curl -sf "http://localhost:${SERVER_PORT}/actuator/health" &>/dev/null; then
    echo ""
    info "Application is ready."
    link "App      http://localhost:${SERVER_PORT}"
    link "Swagger  http://localhost:${SERVER_PORT}/swagger-ui.html"
    link "Health   http://localhost:${SERVER_PORT}/actuator/health"
    echo ""
    info "Stop with: ./scripts/stop-local.sh"
    exit 0
  fi
  sleep 2
done

warn "Did not respond within 60s. Check logs/istream.log for errors."
