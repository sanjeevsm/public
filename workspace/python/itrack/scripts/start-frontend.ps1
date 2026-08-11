# Start frontend (PowerShell) — placed in scripts/

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Join-Path $scriptDir '..'
Set-Location (Join-Path $repoRoot 'frontend')
Write-Host 'Frontend server starting on http://localhost:3000' -ForegroundColor Green
Write-Host ''
npm run dev
