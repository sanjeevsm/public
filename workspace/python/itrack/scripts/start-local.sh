#!/bin/bash

# Resolve repo root (script is in ./scripts)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT" || exit 1

# iTrack+ Local Start Script for Linux/macOS (No Docker)

echo "🚀 Starting iTrack+ (Local Mode)"
echo "================================="
echo ""

# Check if MongoDB is running
echo "🔍 Checking MongoDB..."
if mongosh --eval "db.runCommand({ ping: 1 })" --quiet &> /dev/null; then
    echo "✅ MongoDB is running"
else
    echo "❌ MongoDB is not running!"
    echo ""
    echo "Please start MongoDB first:"
    echo "  Option 1: mongod --dbpath /data/db"
    echo "  Option 2: sudo systemctl start mongod (if installed as service)"
    echo "  Option 3: brew services start mongodb-community (macOS)"
    echo "  Option 4: Use MongoDB Atlas (update .env with connection string)"
    echo ""
    exit 1
fi

echo ""
echo "🔧 Starting Backend Server..."
echo "============================="

# Start backend in background
cd backend || exit 1
source venv/bin/activate

echo "🔥 Backend server starting on http://localhost:8002"
echo "📚 API Documentation: http://localhost:8002/docs"
echo ""

mkdir -p "$REPO_ROOT/logs" "$REPO_ROOT/.pids"
nohup uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload \
    >"$REPO_ROOT/logs/backend.log" 2>"$REPO_ROOT/logs/backend-error.log" &
echo $! > "$REPO_ROOT/.pids/backend.pid"
echo "Backend started (PID $(cat "$REPO_ROOT/.pids/backend.pid")). Logs: $REPO_ROOT/logs/backend.log"

cd "$REPO_ROOT" || exit 1

echo "✅ Backend started"
echo "   URL: http://localhost:8002"

sleep 3

echo ""
echo "🎨 Starting Frontend Server..."
echo "=============================="

cd frontend || exit 1

echo "🎨 Frontend server starting on http://localhost:3000"
echo ""

nohup npm run dev >"$REPO_ROOT/logs/frontend.log" 2>"$REPO_ROOT/logs/frontend-error.log" &
echo $! > "$REPO_ROOT/.pids/frontend.pid"
echo "Frontend started (PID $(cat "$REPO_ROOT/.pids/frontend.pid")). Logs: $REPO_ROOT/logs/frontend.log"

cd "$REPO_ROOT" || exit 1

echo "✅ Frontend started"
echo "   URL: http://localhost:3000"

echo ""
echo "✅ iTrack+ is starting up!"
echo "========================="
echo ""
echo "📱 Access the application:"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8002"
echo "   API Docs: http://localhost:8002/docs"
echo ""
echo "⏱️  Please wait 10-15 seconds for all services to start..."
echo ""
echo "To stop: ./scripts/stop-local.sh"
echo ""
