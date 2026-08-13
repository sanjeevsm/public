#Requires -Version 5.1
<#
.SYNOPSIS
    One-time setup: creates Python venv, installs dependencies, creates directories.
#>
$ErrorActionPreference = "Stop"
$ROOT = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $ROOT

function Write-Info { param($msg) Write-Host "[Setup] $msg" -ForegroundColor Cyan }
function Write-Ok   { param($msg) Write-Host "[OK]    $msg" -ForegroundColor Green }
function Write-Warn { param($msg) Write-Host "[WARN]  $msg" -ForegroundColor Yellow }

Write-Host ""
Write-Host "  CI/CD Dashboard - Setup"
Write-Host ""

# -- Directories ---------------------------------------------------------------
Write-Info "Creating directories..."
foreach ($dir in @("data", "data\prometheus", "data\grafana-logs", "exports", ".pids")) {
    $null = New-Item -ItemType Directory -Force -Path $dir
}
Write-Ok "Directories ready"

# -- Python check --------------------------------------------------------------
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Warn "Python not found in PATH. Install from https://python.org and re-run setup."
    exit 1
}
Write-Ok "Python found: $(python --version)"

# -- Virtual environment -------------------------------------------------------
if (-not (Test-Path "dashboard_api\.venv")) {
    Write-Info "Creating venv at dashboard_api\.venv ..."
    python -m venv "dashboard_api\.venv"
    Write-Ok "Virtual environment created"
} else {
    Write-Ok "Virtual environment already exists"
}

Write-Info "Installing Python dependencies..."
& "dashboard_api\.venv\Scripts\pip.exe" install --upgrade pip
& "dashboard_api\.venv\Scripts\pip.exe" install -r "dashboard_api\requirements.txt"
Write-Ok "Python dependencies installed"

# -- .env ----------------------------------------------------------------------
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Ok ".env created from .env.example - edit it and set GITLAB_TOKEN"
} else {
    Write-Ok ".env already exists"
}

Write-Host ""
Write-Host "Setup complete!" -ForegroundColor Green
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Edit .env and set GITLAB_TOKEN"
Write-Host "  2. Run: .\scripts\start.ps1"
Write-Host ""
