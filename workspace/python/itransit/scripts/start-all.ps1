$P = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location $P
Start-Process powershell -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File .\start-backend.ps1"
Start-Process powershell -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File .\start-frontend.ps1"
Pop-Location
