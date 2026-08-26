#!/usr/bin/env bash
set -e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; CYAN='\033[0;36m'; NC='\033[0m'
PID_FILE="$ROOT/.streamsource.pid"

info()  { echo -e "${GREEN}[start]${NC} $*"; }
warn()  { echo -e "${YELLOW}[start]${NC} $*"; }
error() { echo -e "${RED}[start]${NC} $*"; exit 1; }
link()  { echo -e "${CYAN}$*${NC}"; }

DOCKER_MODE=false
for arg in "$@"; do
  case $arg in
    --docker|-docker) DOCKER_MODE=true ;;
  esac
done

# ── Full Docker mode ───────────────────────────────────────────────────────────
if [ "$DOCKER_MODE" = true ]; then
  info "Starting full Docker stack (build + run)..."
  docker compose up --build -d
  echo ""
  info "Stack is up. Access:"
  link "  App         http://localhost:8080"
  link "  Swagger UI  http://localhost:8080/swagger-ui.html"
  link "  Prometheus  http://localhost:9090"
  link "  Grafana     http://localhost:3002  (admin / admin)"
  exit 0
fi

# ── Hybrid mode: Docker infra + local JAR ────────────────────────────────────
if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
  warn "Application already running (PID $(cat "$PID_FILE")). Use ./scripts/stop.sh first."
  exit 0
fi

# Check JAR exists
JAR=$(ls "$ROOT"/streamsource-app/target/streamsource-app-*.jar 2>/dev/null | head -1)
if [ -z "$JAR" ]; then
  error "JAR not found. Run ./scripts/setup.sh first."
fi

# Check Docker for infra
if ! command -v docker &>/dev/null; then
  warn "Docker not found — infrastructure must be running manually."
  warn "See README.md 'Fully Local' section for manual Kafka/PostgreSQL/Redis setup."
else
  info "Starting infrastructure (Kafka, PostgreSQL, Redis) via Docker..."
  docker compose up -d zookeeper kafka postgres redis
  info "Waiting for services to be ready..."
  sleep 20
fi

# Load .env
if [ -f .env ]; then
  set -a; source .env; set +a
  info "Loaded environment from .env"
fi

# Export connection vars pointing to Docker-exposed host ports
export KAFKA_BROKERS="${KAFKA_BROKERS:-localhost:9092}"
export DB_URL="${DB_URL:-jdbc:postgresql://localhost:5433/streamsource}"
export DB_USER="${DB_USER:-streamsource}"
export DB_PASSWORD="${DB_PASSWORD:-streamsource}"
export REDIS_HOST="${REDIS_HOST:-localhost}"
export REDIS_PORT="${REDIS_PORT:-6379}"
export JWT_SECRET="${JWT_SECRET:-dev-secret-change-in-production-minimum-32-chars}"
export SERVER_PORT="${SERVER_PORT:-8080}"

info "Starting streamsource (PID will be saved to .streamsource.pid)..."
nohup java \
  -XX:+UseContainerSupport \
  -XX:MaxRAMPercentage=75.0 \
  -Djava.security.egd=file:/dev/./urandom \
  -jar "$JAR" \
  > streamsource.log 2>&1 &

APP_PID=$!
echo "$APP_PID" > "$PID_FILE"
info "Application started (PID $APP_PID). Logs: streamsource.log"

# Wait for app to be ready
info "Waiting for application to be ready..."
for i in $(seq 1 30); do
  if curl -sf http://localhost:"${SERVER_PORT:-8080}"/actuator/health &>/dev/null; then
    echo ""
    info "Application is ready."
    link "  App         http://localhost:${SERVER_PORT:-8080}"
    link "  Swagger UI  http://localhost:${SERVER_PORT:-8080}/swagger-ui.html"
    link "  Health      http://localhost:${SERVER_PORT:-8080}/actuator/health"
    echo ""
    info "Stop with: ./scripts/stop.sh"
    exit 0
  fi
  sleep 2
done

warn "Application did not respond within 60s. Check streamsource.log for errors."
