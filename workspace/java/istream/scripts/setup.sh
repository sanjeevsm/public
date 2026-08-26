#!/usr/bin/env bash
set -e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'

info()  { echo -e "${GREEN}[setup]${NC} $*"; }
warn()  { echo -e "${YELLOW}[setup]${NC} $*"; }
error() { echo -e "${RED}[setup]${NC} $*"; exit 1; }

info "iStream+ — setup"
echo ""

# ── Java 21+ ──────────────────────────────────────────────────────────────────
if ! command -v java &>/dev/null; then
  error "Java not found. Install Java 21+ from https://adoptium.net and re-run."
fi

JAVA_VERSION=$(java -version 2>&1 | head -1 | sed 's/.*version "\([0-9]*\).*/\1/')
if [ "$JAVA_VERSION" -lt 21 ]; then
  error "Java 21+ required (found $JAVA_VERSION). Install from https://adoptium.net"
fi
info "Java $JAVA_VERSION found."

# ── Maven (prefer mvnw wrapper, fall back to installed mvn) ───────────────────
if [ -f ./mvnw ]; then
  chmod +x ./mvnw
  MVN="./mvnw"
elif command -v mvn &>/dev/null; then
  MVN="mvn"
else
  error "Maven not found. The Maven wrapper (mvnw) is missing and mvn is not in PATH."
fi

MVN_VERSION=$($MVN --version 2>&1 | head -1 | awk '{print $3}')
info "Maven $MVN_VERSION found ($MVN)."

# ── .env ──────────────────────────────────────────────────────────────────────
if [ ! -f .env ]; then
  cp .env.example .env
  info ".env created from .env.example — review and update values before starting."
else
  info ".env already exists — skipping."
fi

# ── Build ─────────────────────────────────────────────────────────────────────
info "Building project (skipping tests)..."
$MVN clean package -DskipTests -q
info "Build complete."

echo ""
info "Setup complete. Next steps:"
echo "  1. Edit .env and set JWT_SECRET and DB_PASSWORD"
echo "  2. Run: ./scripts/start.sh           (hybrid: Docker infra + local JAR)"
echo "     Run: ./scripts/start.sh --docker  (full Docker stack)"
