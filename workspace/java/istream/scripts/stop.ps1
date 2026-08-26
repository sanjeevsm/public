#Requires -Version 5.1
[CmdletBinding()]
param(
    [switch]$Infra,
    [switch]$All
)

$Root = Split-Path $PSScriptRoot -Parent
Set-Location $Root
$PidFile = Join-Path $Root ".istream.pid"

function Write-Info { param($m) Write-Host "[stop] $m" -ForegroundColor Green }
function Write-Warn { param($m) Write-Host "[stop] $m" -ForegroundColor Yellow }

$stopInfra = $Infra -or $All

# Stop the application JAR
if (Test-Path $PidFile) {
    $pid = Get-Content $PidFile
    $proc = Get-Process -Id $pid -ErrorAction SilentlyContinue
    if ($proc) {
        Write-Info "Stopping application (PID $pid)..."
        Stop-Process -Id $pid -Force
        Start-Sleep -Seconds 2
        Write-Info "Application stopped."
    } else {
        Write-Warn "No process found for PID $pid."
    }
    Remove-Item $PidFile -Force
} else {
    Write-Warn "No PID file found — application may not be running."
}

# Optionally stop infrastructure
if ($stopInfra) {
    if (Get-Command docker -ErrorAction SilentlyContinue) {
        Write-Info "Stopping infrastructure containers..."
        docker compose stop zookeeper kafka postgres redis
        Write-Info "Infrastructure stopped."
    }
}

Write-Info "Done. Use -Infra or -All to also stop Kafka/PostgreSQL/Redis."
