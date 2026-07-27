#Requires -Version 5.1
<#
.SYNOPSIS
    Starts PrimeCare+ API and web app as native Windows background processes.
    Automatically runs setup if virtual environments are not found.
#>
$ErrorActionPreference = "Stop"
$ROOT = Split-Path -Parent $PSScriptRoot
Set-Location $ROOT

function Write-Info { param($msg) Write-Host "[PRIMECARE] $msg" -ForegroundColor Cyan }
function Write-Ok   { param($msg) Write-Host "[OK]        $msg" -ForegroundColor Green }
function Write-Warn { param($msg) Write-Host "[WARN]      $msg" -ForegroundColor Yellow }
function Write-Err  { param($msg) Write-Host "[ERROR]     $msg" -ForegroundColor Red; exit 1 }

Write-Host ""
Write-Host "  PrimeCare+"
Write-Host ""

# -- Load .env -------------------------------------------------------------------
if (-not (Test-Path ".env")) {
    Write-Warn ".env not found -- copying from .env.example"
    Copy-Item ".env.example" ".env"
}

Get-Content ".env" | Where-Object { $_ -notmatch "^\s*#" -and $_ -match "=" } | ForEach-Object {
    $parts = $_ -split "=", 2
    [System.Environment]::SetEnvironmentVariable($parts[0].Trim(), $parts[1].Trim(), "Process")
}

$ApiPort    = if ($env:API_PORT)     { $env:API_PORT }     else { "5000" }
$WebPort    = if ($env:WEB_PORT)     { $env:WEB_PORT }     else { "5001" }
$ApiUrl     = if ($env:API_URL)      { $env:API_URL }      else { "http://localhost:$ApiPort" }
$DbHost     = if ($env:DB_HOST)      { $env:DB_HOST }      else { "localhost" }
$DbPort     = if ($env:DB_PORT)      { $env:DB_PORT }      else { "5432" }
$DbName     = if ($env:DB_NAME)      { $env:DB_NAME }      else { "clinic" }
$DbUser     = if ($env:DB_USER)      { $env:DB_USER }      else { "postgres" }
$DbPassword = if ($env:DB_PASSWORD)  { $env:DB_PASSWORD }  else { "" }

if (-not $DbPassword) { Write-Warn "DB_PASSWORD is not set in .env -- database connection may fail" }

# -- Auto-setup if venvs are missing ---------------------------------------------
if (-not (Test-Path "api\venv") -or -not (Test-Path "web-app\venv")) {
    Write-Info "Virtual environments not found -- running setup first..."
    & "$ROOT\scripts\setup.ps1"
}

# -- Auto-install if deps are stale ----------------------------------------------
$flaskCheck = & "api\venv\Scripts\python.exe" -c "import flask, psycopg2" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Info "Installing API dependencies..."
    & "api\venv\Scripts\pip.exe" install --quiet -r "api\requirements.txt"
}
$webCheck = & "web-app\venv\Scripts\python.exe" -c "import flask, requests" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Info "Installing web-app dependencies..."
    & "web-app\venv\Scripts\pip.exe" install --quiet -r "web-app\requirements.txt"
}

foreach ($dir in @(".pids", "data")) {
    $null = New-Item -ItemType Directory -Force -Path $dir
}

# -- Clear stale PIDs ------------------------------------------------------------
foreach ($svc in @("api", "web")) {
    $pidFile = ".pids\$svc.pid"
    if (Test-Path $pidFile) {
        $oldPid = Get-Content $pidFile
        try { Stop-Process -Id $oldPid -Force -ErrorAction Stop; Write-Info "Stopped existing $svc (PID $oldPid)" } catch {}
        Remove-Item $pidFile -Force -ErrorAction SilentlyContinue
    }
}

# -- Set env vars for child processes (inherited by Start-Process) ---------------
[System.Environment]::SetEnvironmentVariable("DB_HOST",     $DbHost,     "Process")
[System.Environment]::SetEnvironmentVariable("DB_PORT",     $DbPort,     "Process")
[System.Environment]::SetEnvironmentVariable("DB_NAME",     $DbName,     "Process")
[System.Environment]::SetEnvironmentVariable("DB_USER",     $DbUser,     "Process")
[System.Environment]::SetEnvironmentVariable("DB_PASSWORD", $DbPassword, "Process")
[System.Environment]::SetEnvironmentVariable("API_PORT",    $ApiPort,    "Process")

# -- Start API -------------------------------------------------------------------
Write-Info "Starting PrimeCare+ API on port $ApiPort..."
$apiProc = Start-Process -FilePath "api\venv\Scripts\python.exe" `
    -ArgumentList "api\app.py" `
    -WorkingDirectory $ROOT `
    -NoNewWindow `
    -RedirectStandardOutput "$ROOT\data\api.log" `
    -RedirectStandardError  "$ROOT\data\api-error.log" `
    -PassThru
$apiProc.Id | Out-File ".pids\api.pid" -Encoding ascii
Write-Ok "API started (PID $($apiProc.Id))"

# -- Wait for API ----------------------------------------------------------------
Write-Info "Waiting for API to be ready..."
Start-Sleep 5
$ready = $false
for ($i = 1; $i -le 20; $i++) {
    try {
        $r = Invoke-WebRequest -Uri "http://localhost:$ApiPort/specialities" -UseBasicParsing -TimeoutSec 5 -ErrorAction SilentlyContinue
        if ($r.StatusCode -eq 200) { $ready = $true; break }
    } catch {}
    Start-Sleep 2
}
if ($ready) { Write-Ok "API is ready" } else { Write-Err "API did not start after 20 s -- check data\api-error.log" }

# -- Set env vars for web app ---------------------------------------------------
[System.Environment]::SetEnvironmentVariable("API_URL",  $ApiUrl,  "Process")
[System.Environment]::SetEnvironmentVariable("WEB_PORT", $WebPort, "Process")

# -- Start web app ---------------------------------------------------------------
Write-Info "Starting PrimeCare+ web app on port $WebPort..."
$webProc = Start-Process -FilePath "web-app\venv\Scripts\python.exe" `
    -ArgumentList "web-app\client.py" `
    -WorkingDirectory $ROOT `
    -NoNewWindow `
    -RedirectStandardOutput "$ROOT\data\web.log" `
    -RedirectStandardError  "$ROOT\data\web-error.log" `
    -PassThru
$webProc.Id | Out-File ".pids\web.pid" -Encoding ascii
Write-Ok "Web app started (PID $($webProc.Id))"

# -- Wait for web app ------------------------------------------------------------
Write-Info "Waiting for web app to be ready..."
$ready = $false
for ($i = 1; $i -le 15; $i++) {
    try {
        $r = Invoke-WebRequest -Uri "http://localhost:$WebPort/specialities" -UseBasicParsing -TimeoutSec 5 -ErrorAction SilentlyContinue
        if ($r.StatusCode -eq 200) { $ready = $true; break }
    } catch {}
    Start-Sleep 1
}
if ($ready) { Write-Ok "Web app is ready" } else { Write-Warn "Web app health check timed out -- check data\web-error.log" }

Write-Host ""
Write-Host "PrimeCare+ is running!" -ForegroundColor Green
Write-Host ""
Write-Host "  Web app  ->  http://localhost:$WebPort"  -ForegroundColor Green
Write-Host "  Reports  ->  http://localhost:$WebPort/reports" -ForegroundColor Green
Write-Host "  API      ->  http://localhost:$ApiPort"  -ForegroundColor Green
Write-Host ""
Write-Host "To stop: .\scripts\stop.ps1" -ForegroundColor Gray
Write-Host ""

# -- Open browser ----------------------------------------------------------------
Start-Process "http://localhost:$WebPort"
