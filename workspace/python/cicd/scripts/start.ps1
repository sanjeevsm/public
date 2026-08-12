#Requires -Version 5.1
<#
.SYNOPSIS
    Starts the CI/CD Dashboard (Prometheus + Grafana + FastAPI) as native Windows processes.
    Run setup.ps1 first if this is a fresh install.
    Provider credentials are entered in the browser Settings panel -- not required here.
#>
$ErrorActionPreference = "Stop"
$ROOT = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $ROOT

function Write-Info { param($msg) Write-Host "[CICD] $msg" -ForegroundColor Cyan }
function Write-Ok   { param($msg) Write-Host "[OK]   $msg" -ForegroundColor Green }
function Write-Warn { param($msg) Write-Host "[WARN] $msg" -ForegroundColor Yellow }
function Write-Err  { param($msg) Write-Host "[ERROR] $msg" -ForegroundColor Red; exit 1 }

Write-Host ""
Write-Host "  CI/CD Dashboard"
Write-Host ""

# -- Load .env -----------------------------------------------------------------
if (-not (Test-Path ".env")) {
    Write-Warn ".env not found - copying from .env.example"
    Copy-Item ".env.example" ".env"
}

Get-Content ".env" | Where-Object { $_ -notmatch "^\s*#" -and $_ -match "=" } | ForEach-Object {
    $parts = $_ -split "=", 2
    [System.Environment]::SetEnvironmentVariable($parts[0].Trim(), $parts[1].Trim(), "Process")
}

$API_PORT    = if ($env:APP_PORT)               { $env:APP_PORT }               else { "8000" }
$PROM_PORT   = if ($env:PROMETHEUS_PORT)        { $env:PROMETHEUS_PORT }        else { "9000" }
$GRAF_PORT   = if ($env:GRAFANA_PORT)           { $env:GRAFANA_PORT }           else { "9001" }
$LOG_LEVEL   = if ($env:LOG_LEVEL)              { $env:LOG_LEVEL }              else { "info" }
$PROM_RETAIN = if ($env:PROMETHEUS_RETENTION)   { $env:PROMETHEUS_RETENTION }   else { "30d" }

$PROMETHEUS_EXE = if ($env:PROMETHEUS_EXE) { $env:PROMETHEUS_EXE } else { Write-Err "Set PROMETHEUS_EXE in .env to the path of prometheus.exe" }
$GRAFANA_EXE    = if ($env:GRAFANA_EXE)    { $env:GRAFANA_EXE }    else { Write-Err "Set GRAFANA_EXE in .env to the path of grafana.exe" }
$GRAFANA_ROOT   = if ($env:GRAFANA_ROOT)   { $env:GRAFANA_ROOT }   else { Write-Err "Set GRAFANA_ROOT in .env to the Grafana installation directory" }

function Get-ListenersByPort { param([int]$Port) Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique }

function Ensure-PortFree {
    param([int]$Port)
    $pids = Get-ListenersByPort -Port $Port
    if ($pids) {
        foreach ($thePid in $pids) {
            $cmdline = ""
            try { $cmdline = (Get-CimInstance Win32_Process -Filter "ProcessId=$thePid" | Select-Object -ExpandProperty CommandLine) } catch {}
            Write-Err "Port $Port is in use by PID $thePid (cmd: $cmdline). Please stop it and retry."
        }
        exit 1
    }
}

# -- Prerequisite checks -------------------------------------------------------
if (-not (Test-Path $PROMETHEUS_EXE)) {
    Write-Err "Prometheus not found at $PROMETHEUS_EXE"
}
if (-not (Test-Path $GRAFANA_EXE)) {
    Write-Err "Grafana not found at $GRAFANA_EXE"
}

# -- Auto-install Python deps if needed ----------------------------------------
if (-not (Test-Path "dashboard_api\.venv\Scripts\uvicorn.exe")) {
    Write-Info "Installing Python dependencies..."
    if (-not (Test-Path "dashboard_api\.venv")) {
        python -m venv "dashboard_api\.venv"
    }
    & "dashboard_api\.venv\Scripts\pip.exe" install --upgrade pip
    & "dashboard_api\.venv\Scripts\pip.exe" install -r "dashboard_api\requirements.txt"
    if (-not (Test-Path "dashboard_api\.venv\Scripts\uvicorn.exe")) {
        Write-Err "pip install completed but uvicorn.exe still not found. Check errors above."
    }
    Write-Ok "Python dependencies installed"
}
$uvicorn = (Resolve-Path "dashboard_api\.venv\Scripts\uvicorn.exe").Path

# -- Create runtime directories ------------------------------------------------
foreach ($dir in @(".pids", "exports", "data", "data\prometheus", "data\grafana-logs")) {
    $null = New-Item -ItemType Directory -Force -Path $dir
}

function Ensure-PortFree {
    param([int]$Port)
    $pids = Get-ListenersByPort -Port $Port
    if ($pids) {
        foreach ($thePid in $pids) {
            if (-not (Stop-If-ProjectOrForce -TargetPid $thePid -Port $Port)) { Write-Err "Aborting start due to occupied port $Port" }
        }
    }
}

# -- Start Prometheus ----------------------------------------------------------
Write-Info "Starting Prometheus on port $PROM_PORT ..."
Ensure-PortFree -Port $PROM_PORT
$promArgs = @(
    "--config.file=$ROOT\prometheus\prometheus.yml",
    "--storage.tsdb.path=$ROOT\data\prometheus",
    "--storage.tsdb.retention.time=$PROM_RETAIN",
    "--web.listen-address=0.0.0.0:$PROM_PORT"
)
$promProc = Start-Process -FilePath $PROMETHEUS_EXE `
    -ArgumentList $promArgs `
    -WorkingDirectory $ROOT `
    -NoNewWindow `
    -RedirectStandardOutput "$ROOT\data\prometheus.log" `
    -RedirectStandardError  "$ROOT\data\prometheus-error.log" `
    -PassThru
$promProc.Id | Out-File ".pids\prometheus.pid" -Encoding ascii
Write-Ok "Prometheus started (PID $($promProc.Id))"

# Ensure Grafana port is free
Ensure-PortFree -Port $GRAF_PORT
# -- Start Grafana -------------------------------------------------------------
Write-Info "Starting Grafana on port $GRAF_PORT ..."
$grafanaAdminUser = if ($env:GRAFANA_ADMIN_USER)     { $env:GRAFANA_ADMIN_USER }     else { "admin" }
$grafanaAdminPass = if ($env:GRAFANA_ADMIN_PASSWORD) { $env:GRAFANA_ADMIN_PASSWORD } else { "admin123" }

[System.Environment]::SetEnvironmentVariable("GF_SERVER_HTTP_PORT",                       $GRAF_PORT,                                          "Process")
[System.Environment]::SetEnvironmentVariable("GF_SECURITY_ADMIN_USER",                    $grafanaAdminUser,                                   "Process")
[System.Environment]::SetEnvironmentVariable("GF_SECURITY_ADMIN_PASSWORD",                $grafanaAdminPass,                                   "Process")
[System.Environment]::SetEnvironmentVariable("GF_PATHS_PROVISIONING",                     "$ROOT\grafana\provisioning",                        "Process")
[System.Environment]::SetEnvironmentVariable("GF_PATHS_CONFIG",                           "$ROOT\grafana\grafana.ini",                         "Process")
[System.Environment]::SetEnvironmentVariable("GF_DASHBOARDS_DEFAULT_HOME_DASHBOARD_PATH", "$ROOT\grafana\dashboards\cicd-dashboard.json",      "Process")
[System.Environment]::SetEnvironmentVariable("GF_DATABASE_PATH",                          "$ROOT\data\grafana.db",                             "Process")
[System.Environment]::SetEnvironmentVariable("GF_PATHS_LOGS",                             "$ROOT\data\grafana-logs",                           "Process")

$grafanaProc = Start-Process -FilePath $GRAFANA_EXE `
    -ArgumentList "server", "--homepath=$GRAFANA_ROOT" `
    -WorkingDirectory $GRAFANA_ROOT `
    -NoNewWindow `
    -RedirectStandardOutput "$ROOT\data\grafana.log" `
    -RedirectStandardError  "$ROOT\data\grafana-error.log" `
    -PassThru
$grafanaProc.Id | Out-File ".pids\grafana.pid" -Encoding ascii
Write-Ok "Grafana started (PID $($grafanaProc.Id))"

Ensure-PortFree -Port $API_PORT
# -- Start FastAPI -------------------------------------------------------------
Write-Info "Starting CI/CD Dashboard API on port $API_PORT ..."

[System.Environment]::SetEnvironmentVariable("APP_PORT",   $API_PORT,  "Process")
[System.Environment]::SetEnvironmentVariable("LOG_LEVEL",  $LOG_LEVEL, "Process")
[System.Environment]::SetEnvironmentVariable("EXPORT_DIR", "$ROOT\exports", "Process")

$apiProc = Start-Process -FilePath $uvicorn `
    -ArgumentList "main:app", "--host", "0.0.0.0", "--port", $API_PORT `
    -WorkingDirectory "$ROOT\dashboard_api" `
    -NoNewWindow `
    -RedirectStandardOutput "$ROOT\data\api.log" `
    -RedirectStandardError  "$ROOT\data\api-error.log" `
    -PassThru
$apiProc.Id | Out-File ".pids\api.pid" -Encoding ascii
Write-Ok "CI/CD Dashboard API started (PID $($apiProc.Id))"

# -- Health checks -------------------------------------------------------------
Write-Info "Waiting for services to be healthy..."
Start-Sleep 3

function Wait-Health {
    param($url, $name, [int]$maxAttempts = 20)
    for ($i = 0; $i -lt $maxAttempts; $i++) {
        try {
            $null = Invoke-WebRequest $url -UseBasicParsing -TimeoutSec 2
            Write-Ok "$name is ready"
            return
        } catch {
            Start-Sleep 2
        }
    }
    Write-Warn "$name did not respond at $url - check logs in data\"
}

Wait-Health "http://localhost:$PROM_PORT/-/ready"    "Prometheus"
Wait-Health "http://localhost:$GRAF_PORT/api/health" "Grafana"
Wait-Health "http://localhost:$API_PORT/health"      "CI/CD Dashboard"

Write-Host ""
Write-Host "CI/CD Dashboard is running!" -ForegroundColor Green
Write-Host "  Dashboard  -> http://localhost:$API_PORT"           -ForegroundColor Green
Write-Host "  Grafana    -> http://localhost:$GRAF_PORT"          -ForegroundColor Green
Write-Host "  Prometheus -> http://localhost:$PROM_PORT"          -ForegroundColor Green
Write-Host "  API Docs   -> http://localhost:$API_PORT/api/docs"  -ForegroundColor Green
Write-Host "  Metrics    -> http://localhost:$API_PORT/metrics"   -ForegroundColor Green
Write-Host ""
Write-Host "To stop: .\scripts\stop.ps1" -ForegroundColor Gray
Write-Host ""

# -- Open browser tabs ---------------------------------------------------------
Write-Info "Opening dashboards in browser..."
Start-Process "http://localhost:$API_PORT"
Start-Sleep 1
Start-Process "http://localhost:$GRAF_PORT"
Start-Sleep 1
Start-Process "http://localhost:$PROM_PORT"
