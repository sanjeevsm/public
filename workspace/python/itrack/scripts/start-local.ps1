# iTrack+ Local Start Script for Windows (No Docker) — moved to scripts/

Write-Host "Starting iTrack+ (Local Mode)" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# Resolve script and repo paths
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Join-Path $scriptDir '..'
Set-Location $repoRoot

Write-Host "Working directory: $repoRoot" -ForegroundColor Gray
Write-Host ""

# Check if MongoDB service is running
Write-Host "Checking MongoDB service..." -ForegroundColor Yellow
$mongoService = Get-Service | Where-Object {$_.Name -like "*mongo*"} | Select-Object -First 1

if ($mongoService -and $mongoService.Status -eq "Running") {
    Write-Host "MongoDB service is running: $($mongoService.Name)" -ForegroundColor Green
} else {
    Write-Host "MongoDB service is not running!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please start MongoDB first:" -ForegroundColor Yellow
    Write-Host "  Option 1: net start MongoDB (if installed as service)" -ForegroundColor White
    Write-Host "  Option 2: mongod --dbpath C:\data\db" -ForegroundColor White
    Write-Host "  Option 3: Use MongoDB Atlas (update .env with connection string)" -ForegroundColor White
    Write-Host ""

    $response = Read-Host "Do you want to continue anyway? (y/n)"
    if ($response -ne "y") {
        exit 1
    }
}

Write-Host ""
Write-Host "Starting Backend Server..." -ForegroundColor Cyan
Write-Host "=============================" -ForegroundColor Cyan

# Start backend in a new window
$backendScript = @"
Set-Location "$repoRoot\backend"
.\venv\Scripts\Activate.ps1
Write-Host 'Backend server starting on http://localhost:8000' -ForegroundColor Green
Write-Host 'API Documentation: http://localhost:8000/docs' -ForegroundColor Cyan
Write-Host ''
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
"@

$backendScriptPath = Join-Path $repoRoot "scripts\start-backend.ps1"
Set-Content $backendScriptPath $backendScript

Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-File", $backendScriptPath

Write-Host "Backend started in new window" -ForegroundColor Green
Write-Host "   URL: http://localhost:8000" -ForegroundColor Cyan

Start-Sleep -Seconds 3

Write-Host ""
Write-Host "Starting Frontend Server..." -ForegroundColor Cyan
Write-Host "==============================" -ForegroundColor Cyan

# Start frontend in a new window
$frontendScript = @"
Set-Location "$repoRoot\frontend"
Write-Host 'Frontend server starting on http://localhost:3000' -ForegroundColor Green
Write-Host ''
npm run dev
"@

$frontendScriptPath = Join-Path $repoRoot "scripts\start-frontend.ps1"
Set-Content $frontendScriptPath $frontendScript

Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-File", $frontendScriptPath

Write-Host "Frontend started in new window" -ForegroundColor Green
Write-Host "   URL: http://localhost:3000" -ForegroundColor Cyan

Write-Host ""
Write-Host "iTrack+ is starting up!" -ForegroundColor Green
Write-Host "=========================" -ForegroundColor Green
Write-Host ""
Write-Host "Access the application:" -ForegroundColor Cyan
Write-Host "   Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "   Backend:  http://localhost:8000" -ForegroundColor White
Write-Host "   API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "Please wait 10-15 seconds for all services to start..." -ForegroundColor Yellow
Write-Host ""
Write-Host "To stop: Close the backend and frontend PowerShell windows" -ForegroundColor Yellow
Write-Host "   Or run: .\scripts\stop-local.ps1" -ForegroundColor Yellow
Write-Host ""
