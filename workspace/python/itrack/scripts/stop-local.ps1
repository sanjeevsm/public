# iTrack+ Local Stop Script for Windows (No Docker) - moved to scripts/

Write-Host "Stopping iTrack+ (Local Mode)" -ForegroundColor Yellow
Write-Host "=================================" -ForegroundColor Yellow
Write-Host ""

# Resolve script and repo paths
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Join-Path $scriptDir '..'
Set-Location $repoRoot

# Function to kill process by port
function Stop-ProcessByPort {
    param([int]$Port)
    
    $process = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique
    
    if ($process) {
        foreach ($thePid in $process) {
            $processInfo = Get-Process -Id $thePid -ErrorAction SilentlyContinue
            if ($processInfo) {
                Write-Host "  Stopping $($processInfo.ProcessName) (PID: $thePid)" -ForegroundColor Yellow
                Stop-Process -Id $thePid -Force -ErrorAction SilentlyContinue
            }
        }
        return $true
    }
    return $false
}

# Stop Backend (Port 8002)
Write-Host "Stopping Backend Server (Port 8002)..." -ForegroundColor Cyan
if (Stop-ProcessByPort -Port 8002) {
    Write-Host "Backend stopped" -ForegroundColor Green
} else {
    Write-Host "Backend not running on port 8002" -ForegroundColor Gray
}

# Stop Frontend (Port 3000)
Write-Host "Stopping Frontend Server (Port 3000)..." -ForegroundColor Cyan
if (Stop-ProcessByPort -Port 3000) {
    Write-Host "Frontend stopped" -ForegroundColor Green
} else {
    Write-Host "Frontend not running on port 3000" -ForegroundColor Gray
}

# Stop any Node.js processes that might be running from the project
Write-Host "Checking for remaining Node.js processes..." -ForegroundColor Cyan
$nodeProcesses = Get-Process node -ErrorAction SilentlyContinue | Where-Object {
    $_.Path -like "*itrack*"
}

if ($nodeProcesses) {
    foreach ($proc in $nodeProcesses) {
        Write-Host "  Stopping Node.js (PID: $($proc.Id))" -ForegroundColor Yellow
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
    }
}

# Stop Python/Uvicorn processes
Write-Host "Checking for remaining Python processes..." -ForegroundColor Cyan
$pythonProcesses = Get-Process python -ErrorAction SilentlyContinue | Where-Object {
    $_.Path -like "*itrack*"
}

if ($pythonProcesses) {
    foreach ($proc in $pythonProcesses) {
        Write-Host "  Stopping Python (PID: $($proc.Id))" -ForegroundColor Yellow
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
    }
}

Write-Host ""
Write-Host "iTrack+ stopped successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Note: MongoDB is still running (if you started it)" -ForegroundColor Cyan
Write-Host "   To stop MongoDB service: net stop MongoDB" -ForegroundColor Gray
Write-Host "   Or just close the mongod window if running manually" -ForegroundColor Gray
Write-Host ""
Write-Host "To start again: .\scripts\start-local.ps1" -ForegroundColor Cyan
Write-Host ""
