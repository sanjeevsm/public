#!/bin/bash

# Resolve repo root (script is in ./scripts)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT" || exit 1

# iTrack+ Local Setup Script for Linux/macOS (No Docker)

echo "🚀 iTrack+ Local Setup (Non-Docker)"
echo "====================================="
echo ""

# Check Python
echo "📦 Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed."
    echo "📥 Please install Python 3.11+ first:"
    echo "   Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv"
    echo "   macOS: brew install python@3.11"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo "✅ Python found: $PYTHON_VERSION"

# Check Node.js
echo "📦 Checking Node.js installation..."
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed."
    echo "📥 Please install Node.js 16+ first:"
    echo "   Ubuntu/Debian: curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash - && sudo apt install nodejs"
    echo "   macOS: brew install node"
    exit 1
fi

NODE_VERSION=$(node --version)
echo "✅ Node.js found: $NODE_VERSION"

# Check MongoDB
SKIP_MONGO=false
if [ "$1" == "--skip-mongo-check" ]; then
    SKIP_MONGO=true
fi

if [ "$SKIP_MONGO" == false ]; then
    echo "📦 Checking MongoDB installation..."
    if ! command -v mongod &> /dev/null; then
        echo "⚠️  MongoDB is not installed or not in PATH."
        echo ""
        echo "📥 MongoDB Installation Options:"
        echo "   Ubuntu/Debian: https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-ubuntu/"
        echo "   macOS: brew tap mongodb/brew && brew install mongodb-community"
        echo "   Or use MongoDB Atlas (cloud): https://www.mongodb.com/cloud/atlas"
        echo ""
        echo "   Or run with --skip-mongo-check if using MongoDB Atlas"
        exit 1
    else
        echo "✅ MongoDB found"
    fi
fi

echo ""
echo "🔧 Setting up Backend..."
echo "========================"

# Create virtual environment for backend
cd backend || exit 1

if [ -d "venv" ]; then
    echo "♻️  Virtual environment already exists, using it..."
else
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing Python dependencies..."
pip install -r requirements.txt

cd ..

echo ""
echo "🎨 Setting up Frontend..."
echo "========================"

cd frontend || exit 1

# Install npm dependencies
if [ -d "node_modules" ]; then
    echo "♻️  Node modules already exist, skipping install..."
else
    echo "📥 Installing npm dependencies..."
    npm install
fi

cd ..

echo ""
echo "⚙️  Setting up environment configuration..."
echo "==========================================="

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    
    # Update MongoDB URL for local setup (macOS compatible)
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' 's|mongodb://mongodb:27017|mongodb://localhost:27017|g' .env
    else
        sed -i 's|mongodb://mongodb:27017|mongodb://localhost:27017|g' .env
    fi
    
    echo "✅ .env file created"
    echo "⚠️  Please update .env file with your configuration"
else
    echo "✅ .env file already exists"
fi

# Create frontend .env file
if [ ! -f "frontend/.env" ]; then
    echo "📝 Creating frontend .env file..."
    echo "VITE_API_URL=http://localhost:8000" > frontend/.env
    echo "✅ Frontend .env file created"
else
    echo "✅ Frontend .env file already exists"
fi

echo ""
echo "✅ Setup Complete!"
echo "=================="
echo ""
echo "📝 Next Steps:" 
echo ""
echo "1. Make sure MongoDB is running:" 
echo "   mongod --dbpath /data/db"
echo "   (or start MongoDB service: sudo systemctl start mongod)"
echo ""
echo "2. Start the application:" 
echo "   ./scripts/start-local.sh"
echo ""
echo "3. Access the application:" 
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
