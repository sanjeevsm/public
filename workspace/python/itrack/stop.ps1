# iTrack+ Stop Script for Windows PowerShell

Write-Host "🛑 Stopping iTrack+ Application..." -ForegroundColor Yellow

# Check if Docker is installed
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Docker is not installed." -ForegroundColor Red
    exit 1
}

if (-not (Get-Command docker-compose -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Docker Compose is not installed." -ForegroundColor Red
    exit 1
}

# Check if containers are running
$runningContainers = docker-compose ps --filter "status=running" -q

if (-not $runningContainers) {
    Write-Host "ℹ️  iTrack+ is not currently running." -ForegroundColor Cyan
    exit 0
}

Write-Host "📦 Stopping containers..." -ForegroundColor Yellow
docker-compose stop

Write-Host "🗑️  Removing containers..." -ForegroundColor Yellow
docker-compose down

Write-Host ""
Write-Host "✅ iTrack+ has been stopped successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "💡 To start again, run: .\start.ps1 or docker-compose up -d" -ForegroundColor Cyan
Write-Host "🗑️  To remove all data (including database), run: docker-compose down -v" -ForegroundColor Cyan
Write-Host ""
