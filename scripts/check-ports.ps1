#!/usr/bin/env pwsh
# Repo-level port auditor (PowerShell) — reads ports.yml and reports listeners
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Manifest = Join-Path $Root 'ports.yml'
if (-not (Test-Path $Manifest)) { Write-Host "ports.yml not found at $Manifest" -ForegroundColor Red; exit 1 }

$text = Get-Content $Manifest -Raw
$matches = [regex]::Matches($text, '\b[0-9]{2,5}\b')
$ports = $matches | ForEach-Object { $_.Value } | Sort-Object -Unique
foreach ($portValue in $ports) {
    $conns = Get-NetTCPConnection -LocalPort $portValue -State Listen -ErrorAction SilentlyContinue
    if ($conns) {
        $owning = $conns | Select-Object -ExpandProperty OwningProcess -Unique
        foreach ($thePid in $owning) {
            $proc = Get-Process -Id $thePid -ErrorAction SilentlyContinue
            if ($proc) { Write-Host "Port $portValue -> PID $thePid -> $($proc.ProcessName)" -ForegroundColor Yellow } else { Write-Host "Port $portValue -> PID $thePid (process not found)" -ForegroundColor Gray }
        }
    }
}

Write-Host "Done." -ForegroundColor Green