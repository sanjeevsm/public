#!/usr/bin/env pwsh
$P = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location $P\..
if(-not (Test-Path .venv)){
    python -m venv .venv
}
. .venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 9100 --app-dir app
Pop-Location
