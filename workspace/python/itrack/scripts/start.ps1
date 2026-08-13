# iTrack+ Quick Start Script for Windows PowerShell (moved to scripts/)

Write-Host "🚀 Starting iTrack+ Setup..." -ForegroundColor Green

# Resolve script and repo paths
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Join-Path $scriptDir '..'
Set-Location $repoRoot

# Check if Docker is installed
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Docker is not installed. Please install Docker Desktop first." -ForegroundColor Red
    exit 1
}

if (-not (Get-Command docker-compose -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Docker Compose is not installed. Please install Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Create .env file if it doesn't exist
if (-not (Test-Path .env)) {
    Write-Host "📝 Creating .env file from .env.example..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "✅ .env file created" -ForegroundColor Green
} else {
    Write-Host "✅ .env file already exists" -ForegroundColor Green
}

# Build and start containers
Write-Host "🏗️  Building Docker containers..." -ForegroundColor Yellow
docker-compose build

Write-Host "🚀 Starting iTrack+ application..." -ForegroundColor Yellow
docker-compose up -d

# Wait for services to be ready
Write-Host "⏳ Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check if services are running
$running = docker-compose ps | Select-String "Up"

if ($running) {
    Write-Host "";
    Write-Host "✅ iTrack+ is now running!" -ForegroundColor Green
    Write-Host "";
    Write-Host "📱 Frontend: http://localhost:3000" -ForegroundColor Cyan
    Write-Host "🔧 Backend API: http://localhost:8002" -ForegroundColor Cyan
    Write-Host "📚 API Docs: http://localhost:8002/docs" -ForegroundColor Cyan
    Write-Host "";
    Write-Host "To stop the application, run: .\scripts\stop.ps1" -ForegroundColor Yellow
    Write-Host "To view logs, run: docker-compose logs -f" -ForegroundColor Yellow
} else {
    Write-Host "";
    Write-Host "❌ Failed to start services. Check logs with: docker-compose logs" -ForegroundColor Red
    exit 1
}
