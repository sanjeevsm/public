#Requires -Version 5.1
$Root = Split-Path $PSScriptRoot -Parent
$PidFile = Join-Path $Root ".istream.pid"

function Write-Info { param($m) Write-Host "[stop-local] $m" -ForegroundColor Green }
function Write-Warn { param($m) Write-Host "[stop-local] $m" -ForegroundColor Yellow }

if (Test-Path $PidFile) {
    $appPid = Get-Content $PidFile
    $proc = Get-Process -Id $appPid -ErrorAction SilentlyContinue
    if ($proc) {
        Write-Info "Stopping application (PID $appPid)..."
        Stop-Process -Id $appPid -Force
        Start-Sleep -Seconds 2
        Write-Info "Application stopped."
    } else {
        Write-Warn "No process found for PID $appPid."
    }
    Remove-Item $PidFile -Force
} else {
    Write-Warn "No PID file found -- application may not be running."
}
