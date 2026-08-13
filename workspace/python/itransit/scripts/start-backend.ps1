#!/usr/bin/env pwsh
$P = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location $P\..

# Config
$BACKEND_PORT = if ($env:BACKEND_PORT) { [int]$env:BACKEND_PORT } else { 8003 }
Write-Host "Starting iTransit+ backend on port $BACKEND_PORT"

function Get-ListenersByPort {
    param([int]$Port)
    return Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique
}

# Ensure venv
if(-not (Test-Path .venv)){
    python -m venv .venv
}
. .venv\Scripts\Activate.ps1

$pids = Get-ListenersByPort -Port $BACKEND_PORT
if ($pids) {
    foreach ($thePid in $pids) {
        $cmdline = ""
        try { $cmdline = (Get-CimInstance Win32_Process -Filter "ProcessId=$thePid" | Select-Object -ExpandProperty CommandLine) } catch {}
        Write-Host "Port $BACKEND_PORT is in use by PID $thePid (cmd: $cmdline)" -ForegroundColor Red
    }
    Write-Host "Please stop the above process(es) and retry." -ForegroundColor Red
    Pop-Location
    exit 1
} else {
    Write-Host "No listener on port $BACKEND_PORT" -ForegroundColor Gray
}

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port $BACKEND_PORT --app-dir app
Pop-Location
