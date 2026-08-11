# Start backend (PowerShell) — placed in scripts/

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Join-Path $scriptDir '..'
Set-Location (Join-Path $repoRoot 'backend')

.\venv\Scripts\Activate.ps1
Write-Host 'Backend server starting on http://localhost:8000' -ForegroundColor Green
Write-Host 'API Documentation: http://localhost:8000/docs' -ForegroundColor Cyan
Write-Host ''
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
