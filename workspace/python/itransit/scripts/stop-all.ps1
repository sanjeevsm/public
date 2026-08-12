#!/usr/bin/env pwsh
<#
Stop all iTransit+ services (Windows / PowerShell).

Stops:
- backend (port 8003)
- frontend (ports 3000, 3001)
- Node.js / Python processes scoped to this project where detectable

Safe: will only attempt to stop discovered PIDs and prints a summary.
#>

$P = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location $P

function Stop-ProcessByPort {
    param([int]$Port)

    $pids = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique
    if ($pids) {
        $stopped = @()
        foreach ($thepid in $pids) {
            $proc = Get-Process -Id $thepid -ErrorAction SilentlyContinue
            if ($proc) {
                Write-Host "Stopping $($proc.ProcessName) (PID: $thepid) on port $Port" -ForegroundColor Yellow
                Stop-Process -Id $thepid -Force -ErrorAction SilentlyContinue
            } else {
                Write-Host "Killing PID $thepid on port $Port" -ForegroundColor Yellow
                Stop-Process -Id $thepid -Force -ErrorAction SilentlyContinue
            }
            $stopped += $thepid
        }
        return $stopped
    }
    return $null
}

Write-Host "Stopping iTransit+ services" -ForegroundColor Cyan
Write-Host "===========================" -ForegroundColor Cyan

$ports = @(8003, 3001, 3000)
$stoppedAll = @()
foreach ($p in $ports) {
    $res = Stop-ProcessByPort -Port $p
    if ($res) {
        Write-Host ("Stopped processes listening on port {0}: {1}" -f $p, ($res -join ', ')) -ForegroundColor Green
        $stoppedAll += $res
    } else {
        Write-Host "No listener on port $p" -ForegroundColor Gray
    }
}

# Attempt to stop Node/Python processes that include the project path or 'itransit' in their path
$projectPath = (Get-Item -Path '..').FullName
Write-Host "Project path: $projectPath" -ForegroundColor Gray

Write-Host "Checking for Node.js processes scoped to the project..." -ForegroundColor Cyan
$nodeProcs = Get-Process node -ErrorAction SilentlyContinue | Where-Object { $_.Path -and ($_.Path -like "*itransit*" -or $_.Path -like "*$projectPath*") }
if ($nodeProcs) {
    foreach ($proc in $nodeProcs) {
        Write-Host "  Stopping Node.js (PID: $($proc.Id))" -ForegroundColor Yellow
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
        $stoppedAll += $proc.Id
    }
} else {
    Write-Host "  No project-scoped Node.js processes found" -ForegroundColor Gray
}

Write-Host "Checking for Python processes scoped to the project..." -ForegroundColor Cyan
$pyProcs = Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.Path -and ($_.Path -like "*itransit*" -or $_.Path -like "*$projectPath*") }
if ($pyProcs) {
    foreach ($proc in $pyProcs) {
        Write-Host "  Stopping Python (PID: $($proc.Id))" -ForegroundColor Yellow
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
        $stoppedAll += $proc.Id
    }
} else {
    Write-Host "  No project-scoped Python processes found" -ForegroundColor Gray
}

Write-Host "";
if ($stoppedAll) {
    Write-Host ("Stopped PIDs: {0}" -f ($stoppedAll -join ', ')) -ForegroundColor Cyan
} else {
    Write-Host "Nothing to stop; no iTransit+ processes detected." -ForegroundColor Gray
}

Write-Host "Done." -ForegroundColor Green

Pop-Location
