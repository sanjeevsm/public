#Requires -Version 5.1
<#
.SYNOPSIS
    Stops the iLab+ AI Interview Simulator started by start.ps1.
#>
$ROOT = Split-Path -Parent $PSScriptRoot

function Stop-PidFile {
    param([string]$name, [string]$file)
    $pidFile = "$ROOT\.pids\$file"
    if (Test-Path $pidFile) {
        $procId = (Get-Content $pidFile -Raw).Trim()
        try {
            Stop-Process -Id $procId -Force -ErrorAction Stop
            Write-Host "[iLab+] Stopped $name (PID $procId)" -ForegroundColor Cyan
        } catch {
            Write-Host "[iLab+] $name (PID $procId) was not running" -ForegroundColor Yellow
        }
        Remove-Item $pidFile -Force
    } else {
        Write-Host "[iLab+] No PID file for $name - skipping" -ForegroundColor Yellow
    }
}

Write-Host "[iLab+] Stopping iLab+ ..." -ForegroundColor Cyan

Stop-PidFile "iLab+ App" "app.pid"

Write-Host "[iLab+] Done." -ForegroundColor Green
