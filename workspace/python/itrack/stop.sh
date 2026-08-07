#!/bin/bash

# iTrack+ Stop Script for Linux/Mac

echo "🛑 Stopping iTrack+ Application..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed."
    exit 1
fi

# Check if containers are running
if ! docker-compose ps | grep -q "Up"; then
    echo "ℹ️  iTrack+ is not currently running."
    exit 0
fi

echo "📦 Stopping containers..."
docker-compose stop

echo "🗑️  Removing containers..."
docker-compose down

echo ""
echo "✅ iTrack+ has been stopped successfully!"
echo ""
echo "💡 To start again, run: ./start.sh or docker-compose up -d"
echo "🗑️  To remove all data (including database), run: docker-compose down -v"
echo ""
