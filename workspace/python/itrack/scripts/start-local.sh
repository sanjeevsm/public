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

# Start backend in a new terminal or background
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    osascript -e 'tell app "Terminal" to do script "cd \"'"$(pwd)"'\" && source venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload"'
elif command -v gnome-terminal &> /dev/null; then
    # Linux with gnome-terminal
    gnome-terminal -- bash -c "source venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload; exec bash"
elif command -v xterm &> /dev/null; then
    # Linux with xterm
    xterm -e "source venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload" &
else
    # Fallback: run in background
    nohup uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload > "$REPO_ROOT/backend.log" 2>&1 &
    echo "⚠️  Backend started in background. Check backend.log for logs."
fi

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

# Start frontend in a new terminal or background
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    osascript -e 'tell app "Terminal" to do script "cd \"'"$(pwd)"'\" && npm run dev"'
elif command -v gnome-terminal &> /dev/null; then
    # Linux with gnome-terminal
    gnome-terminal -- bash -c "npm run dev; exec bash"
elif command -v xterm &> /dev/null; then
    # Linux with xterm
    xterm -e "npm run dev" &
else
    # Fallback: run in background
    nohup npm run dev > "$REPO_ROOT/frontend.log" 2>&1 &
    echo "⚠️  Frontend started in background. Check frontend.log for logs."
fi

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
echo "🛑 To stop: Run ./scripts/stop-local.sh"
echo "   Or close the terminal windows"
echo ""
