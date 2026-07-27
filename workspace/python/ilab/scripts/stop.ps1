#Requires -Version 5.1
<#
.SYNOPSIS
    Stops iLab+ processes started by start.ps1.
    Defaults to stopping both desktop and web if they are running.
.EXAMPLE
    .\scripts\stop.ps1              # stop everything
    .\scripts\stop.ps1 -Mode web    # stop web server only
    .\scripts\stop.ps1 -Mode desktop # stop desktop app only
#>
param(
    [ValidateSet("all", "desktop", "web")]
    [string]$Mode = "all"
)
$ROOT = Split-Path -Parent $PSScriptRoot

function Stop-PidFile {
    param([string]$Label, [string]$File)
    $pidFile = Join-Path $ROOT ".pids\$File"
    if (Test-Path $pidFile) {
        $procId = (Get-Content $pidFile -Raw).Trim()
        try {
            Stop-Process -Id $procId -Force -ErrorAction Stop
            Write-Host "[iLab+] Stopped $Label (PID $procId)" -ForegroundColor Cyan
        } catch {
            Write-Host "[iLab+] $Label (PID $procId) was not running" -ForegroundColor Yellow
        }
        Remove-Item $pidFile -Force
    } else {
        Write-Host "[iLab+] No PID file for $Label -- skipping" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "[iLab+] Stopping iLab+ [$Mode]..." -ForegroundColor Cyan

if ($Mode -eq "all" -or $Mode -eq "desktop") {
    Stop-PidFile "desktop app" "app.pid"
}
if ($Mode -eq "all" -or $Mode -eq "web") {
    Stop-PidFile "web server"  "web.pid"
}

Write-Host ""
Write-Host "[iLab+] Done." -ForegroundColor Green
Write-Host ""
