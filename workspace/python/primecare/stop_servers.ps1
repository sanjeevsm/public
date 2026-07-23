#Requires -Version 5.1
$ROOT = $PSScriptRoot

function Stop-PidFile {
    param([string]$name, [string]$file)
    $pidFile = Join-Path $ROOT ".pids\$file"
    if (Test-Path $pidFile) {
        $procId = (Get-Content $pidFile -Raw).Trim()
        try {
            Stop-Process -Id $procId -Force -ErrorAction Stop
            Write-Host "[PrimeCare+] Stopped $name (PID $procId)" -ForegroundColor Cyan
        } catch {
            Write-Host "[PrimeCare+] $name (PID $procId) was not running" -ForegroundColor Yellow
        }
        Remove-Item $pidFile -Force
    } else {
        Write-Host "[PrimeCare+] No PID file for $name - skipping" -ForegroundColor Yellow
    }
}

Write-Host "[PrimeCare+] Stopping all services..." -ForegroundColor Cyan

Stop-PidFile "API Server" "api.pid"
Stop-PidFile "Web Client" "web.pid"

Write-Host "[PrimeCare+] Done." -ForegroundColor Green
