$P = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Resolve-Path (Join-Path $P "..")
$logsDir  = Join-Path $repoRoot "logs"
New-Item -ItemType Directory -Path $logsDir -Force | Out-Null

Write-Host "Starting iTransit+ (Local Mode)" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Starting Backend Server..." -ForegroundColor Cyan
Start-Process powershell `
    -ArgumentList @("-NoProfile", "-ExecutionPolicy", "Bypass", "-NonInteractive", "-File", (Join-Path $P "start-backend.ps1")) `
    -WindowStyle Hidden
Write-Host "  URL: http://localhost:8003" -ForegroundColor Cyan

Start-Sleep -Seconds 3

Write-Host ""
Write-Host "Starting Frontend Server..." -ForegroundColor Cyan
Start-Process powershell `
    -ArgumentList @("-NoProfile", "-ExecutionPolicy", "Bypass", "-NonInteractive", "-File", (Join-Path $P "start-frontend.ps1")) `
    -WindowStyle Hidden
Write-Host "  URL: http://localhost:3001" -ForegroundColor Cyan

Write-Host ""
Write-Host "iTransit+ is starting in background." -ForegroundColor Green
Write-Host "  Frontend: http://localhost:3001" -ForegroundColor White
Write-Host "  Backend:  http://localhost:8003" -ForegroundColor White
Write-Host "  API Docs: http://localhost:8003/docs" -ForegroundColor White
Write-Host ""
Write-Host "To stop: .\scripts\stop-all.ps1" -ForegroundColor Yellow
