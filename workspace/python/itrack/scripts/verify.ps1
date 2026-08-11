# iTrack+ Installation Verification Script for Windows (moved to scripts/)

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "iTrack+ Installation Verification" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

$allChecksPass = $true

# Check Docker
Write-Host "Checking Docker... " -NoNewline
if (Get-Command docker -ErrorAction SilentlyContinue) {
    Write-Host "✓ Installed" -ForegroundColor Green
    docker --version
} else {
    Write-Host "✗ Not installed" -ForegroundColor Red
    Write-Host "Please install Docker Desktop: https://docs.docker.com/desktop/install/windows-install/" -ForegroundColor Yellow
    $allChecksPass = $false
}
Write-Host ""

# Check Docker Compose
Write-Host "Checking Docker Compose... " -NoNewline
if (Get-Command docker-compose -ErrorAction SilentlyContinue) {
    Write-Host "✓ Installed" -ForegroundColor Green
    docker-compose --version
} else {
    Write-Host "✗ Not installed" -ForegroundColor Red
    Write-Host "Docker Compose should be included with Docker Desktop" -ForegroundColor Yellow
    $allChecksPass = $false
}
Write-Host ""

# Check if .env exists
Write-Host "Checking .env file... " -NoNewline
if (Test-Path ".env") {
    Write-Host "✓ Found" -ForegroundColor Green
} else {
    Write-Host "⚠ Not found" -ForegroundColor Yellow
    Write-Host "Creating .env from .env.example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "✓ Created" -ForegroundColor Green
}
Write-Host ""

# Check if ports are available
Write-Host "Checking port availability..." -ForegroundColor Cyan

function Test-Port {
    param($Port)
    
    $connection = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
    if ($connection) {
        Write-Host "  Port $Port: ✗ In use" -ForegroundColor Red
        return $false
    } else {
        Write-Host "  Port $Port: ✓ Available" -ForegroundColor Green
        return $true
    }
}

$portsOk = $true
$portsOk = (Test-Port 3000) -and $portsOk
$portsOk = (Test-Port 8000) -and $portsOk
$portsOk = (Test-Port 27017) -and $portsOk
Write-Host ""

if (-not $portsOk) {
    Write-Host "⚠ Warning: Some ports are in use" -ForegroundColor Yellow
    Write-Host "You may need to stop other services or change ports in docker-compose.yml" -ForegroundColor Yellow
    Write-Host ""
    $allChecksPass = $false
}

# Check project structure
Write-Host "Checking project structure..." -ForegroundColor Cyan

function Check-Directory {
    param($Path)
    
    if (Test-Path -Path $Path -PathType Container) {
        Write-Host "  $Path: ✓" -ForegroundColor Green
    } else {
        Write-Host "  $Path: ✗ Missing" -ForegroundColor Red
    }
}

function Check-File {
    param($Path)
    
    if (Test-Path -Path $Path -PathType Leaf) {
        Write-Host "  $Path: ✓" -ForegroundColor Green
    } else {
        Write-Host "  $Path: ✗ Missing" -ForegroundColor Red
    }
}

Check-Directory "backend"
Check-Directory "frontend"
Check-File "docker-compose.yml"
Check-File ".env"
Write-Host ""

# Summary
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Verification Summary" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

if ($allChecksPass -and $portsOk) {
    Write-Host "✓ All checks passed!" -ForegroundColor Green
    Write-Host ""
    Write-Host "You're ready to start iTrack+!" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Run: .\scripts\start.ps1" -ForegroundColor Yellow
    Write-Host "Or: docker-compose up --build -d" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Then visit: http://localhost:3000" -ForegroundColor Cyan
} else {
    Write-Host "⚠ Some warnings found" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Please address the warnings above before starting." -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "=========================================" -ForegroundColor Cyan
