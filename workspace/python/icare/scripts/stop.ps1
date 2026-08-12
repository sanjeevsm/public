#Requires -Version 5.1
<#
.SYNOPSIS
    Stops iCare+ servers started by start.ps1.
#>
$ROOT = Split-Path -Parent $PSScriptRoot

function Stop-PidFile {
    param([string]$Name, [string]$File)
    $pidFile = Join-Path $ROOT ".pids\$File"
    if (Test-Path $pidFile) {
        $procId = (Get-Content $pidFile -Raw).Trim()
        try {
            Stop-Process -Id $procId -Force -ErrorAction Stop
            Write-Host "[ICARE] Stopped $Name (PID $procId)" -ForegroundColor Cyan
        } catch {
            Write-Host "[ICARE] $Name (PID $procId) was not running" -ForegroundColor Yellow
        }
        Remove-Item $pidFile -Force
    } else {
        Write-Host "[ICARE] No PID file for $Name -- skipping" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "[ICARE] Stopping iCare+..." -ForegroundColor Cyan

Stop-PidFile "web app" "web.pid"
Stop-PidFile "API"     "api.pid"

# Flask debug mode spawns a reloader child process that survives parent termination.
# Sweep for any orphaned icare processes by matching the venv executable paths.
$orphans = @(Get-WmiObject Win32_Process | Where-Object {
    $_.CommandLine -match [regex]::Escape("icare\api\venv") -or
    $_.CommandLine -match [regex]::Escape("icare\web-app\venv")
})
foreach ($proc in $orphans) {
    try {
        Stop-Process -Id $proc.ProcessId -Force -ErrorAction Stop
        Write-Host "[ICARE] Cleaned up orphan process (PID $($proc.ProcessId))" -ForegroundColor Yellow
    } catch {}
}

Write-Host "[ICARE] Done." -ForegroundColor Green
Write-Host ""
