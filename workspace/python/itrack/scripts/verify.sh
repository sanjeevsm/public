#!/bin/bash

# Resolve repo root (script is in ./scripts)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT" || exit 1

# iTrack+ Installation Verification Script

echo "========================================="
echo "iTrack+ Installation Verification"
echo "========================================="
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Docker
echo -n "Checking Docker... "
if command -v docker &> /dev/null; then
    echo -e "${GREEN}✓ Installed${NC}"
    docker --version
else
    echo -e "${RED}✗ Not installed${NC}"
    echo "Please install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi
echo ""

# Check Docker Compose (v2 plugin)
echo -n "Checking Docker Compose... "
if docker compose version &> /dev/null; then
    echo -e "${GREEN}✓ Available${NC}"
    docker compose version
else
    echo -e "${RED}✗ Not available${NC}"
    echo "Docker Compose should be included with Docker Desktop"
    exit 1
fi
echo ""

# Check if .env exists
echo -n "Checking .env file... "
if [ -f ".env" ]; then
    echo -e "${GREEN}✓ Found${NC}"
else
    echo -e "${YELLOW}⚠ Not found${NC}"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo -e "${GREEN}✓ Created${NC}"
fi
echo ""

# Check if ports are available
echo "Checking port availability..."

check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        echo -e "  Port $1: ${RED}✗ In use${NC}"
        return 1
    else
        echo -e "  Port $1: ${GREEN}✓ Available${NC}"
        return 0
    fi
}

PORTS_OK=true
check_port 3000 || PORTS_OK=false
check_port 8002 || PORTS_OK=false
check_port 27017 || PORTS_OK=false
echo ""

if [ "$PORTS_OK" = false ]; then
    echo -e "${YELLOW}⚠ Warning: Some ports are in use${NC}"
    echo "You may need to stop other services or change ports in docker-compose.yml"
    echo ""
fi

# Check project structure
echo "Checking project structure..."

check_dir() {
    if [ -d "$1" ]; then
        echo -e "  $1: ${GREEN}✓${NC}"
    else
        echo -e "  $1: ${RED}✗ Missing${NC}"
    fi
}

check_file() {
    if [ -f "$1" ]; then
        echo -e "  $1: ${GREEN}✓${NC}"
    else
        echo -e "  $1: ${RED}✗ Missing${NC}"
    fi
}

check_dir "backend"
check_dir "frontend"
check_file "docker-compose.yml"
check_file ".env"
echo ""

# Summary
echo "========================================="
echo "Verification Summary"
echo "========================================="
echo ""

if [ "$PORTS_OK" = true ]; then
    echo -e "${GREEN}✓ All checks passed!${NC}"
    echo ""
    echo "You're ready to start iTrack+!"
    echo ""
    echo "Run: ./scripts/start.sh"
    echo "Or: docker compose up --build -d"
    echo ""
    echo "Then visit: http://localhost:3000"
else
    echo -e "${YELLOW}⚠ Some warnings found${NC}"
    echo ""
    echo "Please address the warnings above before starting."
    echo ""
fi

echo "========================================="
