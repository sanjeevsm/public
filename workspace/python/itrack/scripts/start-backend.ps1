# Resolve the backend directory relative to this script so paths are portable
Set-Location (Resolve-Path (Join-Path $PSScriptRoot '..\backend'))

# Activate the virtual environment in the backend folder (dot-source)
. .\venv\Scripts\Activate.ps1

Write-Host 'Backend server starting on http://localhost:8000' -ForegroundColor Green
Write-Host 'API Documentation: http://localhost:8000/docs' -ForegroundColor Cyan
Write-Host ''
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
