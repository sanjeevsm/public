#Requires -Version 5.1
<#
.SYNOPSIS
    One-time setup for PrimeCare+ (Windows).
    Creates Python virtual environments and installs all dependencies.
    Run once before the first start, or to reset after a clean clone.
#>
$ErrorActionPreference = "Stop"
$ROOT = Split-Path -Parent $PSScriptRoot
Set-Location $ROOT

function Write-Info { param($msg) Write-Host "[PRIMECARE] $msg" -ForegroundColor Cyan }
function Write-Ok   { param($msg) Write-Host "[OK]        $msg" -ForegroundColor Green }
function Write-Warn { param($msg) Write-Host "[WARN]      $msg" -ForegroundColor Yellow }
function Write-Err  { param($msg) Write-Host "[ERROR]     $msg" -ForegroundColor Red; exit 1 }

Write-Host ""
Write-Host "  PrimeCare+ Setup"
Write-Host ""

# -- Check Python ----------------------------------------------------------------
$Python = $null
foreach ($cmd in @("python", "python3")) {
    try {
        $ver = & $cmd --version 2>&1
        if ($ver -match "Python 3\.(\d+)" -and [int]$Matches[1] -ge 10) {
            $Python = $cmd; break
        }
    } catch {}
}
if (-not $Python) { Write-Err "Python 3.10+ not found. Install from https://python.org" }
Write-Info "Using $($Python): $(& $Python --version 2>&1)"

# -- Create runtime directories --------------------------------------------------
foreach ($dir in @("data", ".pids")) {
    $null = New-Item -ItemType Directory -Force -Path $dir
}
Write-Ok "Runtime directories created (data\, .pids\)"

# -- Copy .env if missing --------------------------------------------------------
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Warn "Created .env from .env.example -- edit DB_PASSWORD before starting"
} else {
    Write-Ok ".env already exists"
}

# -- API venv --------------------------------------------------------------------
Write-Info "Setting up API virtual environment..."
if (-not (Test-Path "api\venv")) {
    & $Python -m venv "api\venv"
}
& "api\venv\Scripts\pip.exe" install --upgrade pip --quiet
& "api\venv\Scripts\pip.exe" install -r "api\requirements.txt"
Write-Ok "API dependencies installed"

# -- Web-app venv ----------------------------------------------------------------
Write-Info "Setting up web-app virtual environment..."
if (-not (Test-Path "web-app\venv")) {
    & $Python -m venv "web-app\venv"
}
& "web-app\venv\Scripts\pip.exe" install --upgrade pip --quiet
& "web-app\venv\Scripts\pip.exe" install -r "web-app\requirements.txt"
Write-Ok "Web-app dependencies installed"

Write-Host ""
Write-Host "Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Edit .env  -- set DB_PASSWORD (and DB_HOST/DB_NAME if needed)"
Write-Host "  2. Create DB  -- psql -U postgres -f clinic_setup.sql"
Write-Host "  3. Start      -- .\scripts\start.ps1"
Write-Host ""
