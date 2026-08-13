# Requires -Version 5.1
$ErrorActionPreference = 'Stop'
$ROOT = Split-Path -Parent $PSScriptRoot
Set-Location $ROOT

function Write-Info { param($m) Write-Host "[ICARE] $m" -ForegroundColor Cyan }
function Write-Ok   { param($m) Write-Host "[OK]        $m" -ForegroundColor Green }
function Write-Warn { param($m) Write-Host "[WARN]      $m" -ForegroundColor Yellow }
function Write-Err  { param($m) Write-Host "[ERROR]     $m" -ForegroundColor Red; exit 1 }

# Create .env if missing
if (-not (Test-Path ".env")) {
    Write-Warn ".env not found -- copying from .env.example"
    Copy-Item ".env.example" ".env"
    Write-Ok ".env created from .env.example"
}

# Create API venv
if (-not (Test-Path "api\venv")) {
    Write-Info "Creating API virtualenv..."
    python -m venv "api\venv"
    & "api\venv\Scripts\python.exe" -m pip install --upgrade pip
    if (Test-Path "api\requirements.txt") {
        & "api\venv\Scripts\pip.exe" install --quiet -r "api\requirements.txt"
        Write-Ok "API dependencies installed"
    } else {
        Write-Warn "api\requirements.txt not found — skipping API dependency install"
    }
}

# Create web-app venv
if (-not (Test-Path "web-app\venv")) {
    Write-Info "Creating web-app virtualenv..."
    python -m venv "web-app\venv"
    & "web-app\venv\Scripts\python.exe" -m pip install --upgrade pip
    if (Test-Path "web-app\requirements.txt") {
        & "web-app\venv\Scripts\pip.exe" install --quiet -r "web-app\requirements.txt"
        Write-Ok "web-app dependencies installed"
    } else {
        Write-Warn "web-app\requirements.txt not found — skipping web-app dependency install"
    }
}

Write-Ok "Setup complete."
