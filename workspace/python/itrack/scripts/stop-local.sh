#!/bin/bash

# Resolve repo root (script is in ./scripts)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT" || exit 1

# iTrack+ Local Stop Script for Linux/macOS (No Docker)

echo "🛑 Stopping iTrack+ (Local Mode)"
echo "================================="
echo ""

# Function to kill process by port
stop_process_by_port() {
    local port=$1
    local service=$2
    
    echo "🔧 Stopping $service (Port $port)..."
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        local pid=$(lsof -ti:$port)
        if [ ! -z "$pid" ]; then
            kill -9 $pid 2>/dev/null
            echo "✅ $service stopped"
            return 0
        fi
    else
        # Linux
        local pid=$(fuser $port/tcp 2>/dev/null)
        if [ ! -z "$pid" ]; then
            kill -9 $pid 2>/dev/null
            echo "✅ $service stopped"
            return 0
        fi
    fi
    
    echo "ℹ️  $service not running on port $port"
    return 1
}

# Stop Backend (Port 8000)
stop_process_by_port 8000 "Backend Server"

# Stop Frontend (Port 3000)
stop_process_by_port 3000 "Frontend Server"

# Stop any remaining Node.js processes from the project
echo "🔍 Checking for remaining Node.js processes..."
if pgrep -f "vite.*itrack" > /dev/null; then
    pkill -f "vite.*itrack"
    echo "✅ Stopped remaining Vite processes"
fi

# Stop any remaining Python processes from the project
echo "🔍 Checking for remaining Python processes..."
if pgrep -f "uvicorn.*itrack" > /dev/null; then
    pkill -f "uvicorn.*itrack"
    echo "✅ Stopped remaining Uvicorn processes"
fi

echo ""
echo "✅ iTrack+ stopped successfully!"
echo ""
echo "💡 MongoDB is still running (if you started it)"
echo "   To stop MongoDB:"
echo "   - Service: sudo systemctl stop mongod"
echo "   - Homebrew: brew services stop mongodb-community"
echo "   - Manual: Just close the mongod terminal"
echo ""
echo "💡 To start again: ./scripts/start-local.sh"
echo ""
