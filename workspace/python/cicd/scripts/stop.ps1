#Requires -Version 5.1
<#
.SYNOPSIS
    Stops all CI/CD Dashboard services started by start.ps1.
#>
$ROOT = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)

function Stop-PidFile {
    param([string]$name, [string]$file)
    $pidFile = "$ROOT\.pids\$file"
    if (Test-Path $pidFile) {
        $procId = (Get-Content $pidFile -Raw).Trim()
        try {
            Stop-Process -Id $procId -Force -ErrorAction Stop
            Write-Host "[CICD] Stopped $name (PID $procId)" -ForegroundColor Cyan
        } catch {
            Write-Host "[CICD] $name (PID $procId) was not running" -ForegroundColor Yellow
        }
        Remove-Item $pidFile -Force
    } else {
        Write-Host "[CICD] No PID file for $name - skipping" -ForegroundColor Yellow
    }
}

Write-Host "[CICD] Stopping all services..." -ForegroundColor Cyan

Stop-PidFile "CI/CD Dashboard" "api.pid"
Stop-PidFile "Grafana"         "grafana.pid"
Stop-PidFile "Prometheus"      "prometheus.pid"

Write-Host "[CICD] Done." -ForegroundColor Green
