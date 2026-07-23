#Requires -Version 5.1
$ROOT = $PSScriptRoot

Write-Host "Starting PrimeCare+ Servers..." -ForegroundColor Cyan
Write-Host ""

if (-not $env:DB_PASSWORD) { $env:DB_PASSWORD = "postgres" }

$null = New-Item -ItemType Directory -Force -Path (Join-Path $ROOT ".pids")

# Start API Server
Write-Host "Starting API Server (Port 5000)..." -ForegroundColor Green
$apiProc = Start-Process `
    -FilePath (Join-Path $ROOT "api\venv\Scripts\python.exe") `
    -ArgumentList (Join-Path $ROOT "api\app.py") `
    -WorkingDirectory (Join-Path $ROOT "api") `
    -NoNewWindow `
    -RedirectStandardOutput (Join-Path $ROOT "api.log") `
    -RedirectStandardError  (Join-Path $ROOT "api-error.log") `
    -PassThru
$apiProc.Id | Out-File (Join-Path $ROOT ".pids\api.pid") -Encoding ascii
Write-Host "API Server started (PID $($apiProc.Id))" -ForegroundColor Green

Start-Sleep -Seconds 3

# Start Web Client
Write-Host "Starting Web Client (Port 5001)..." -ForegroundColor Green
$webProc = Start-Process `
    -FilePath (Join-Path $ROOT "web-app\venv\Scripts\python.exe") `
    -ArgumentList (Join-Path $ROOT "web-app\client.py") `
    -WorkingDirectory (Join-Path $ROOT "web-app") `
    -NoNewWindow `
    -RedirectStandardOutput (Join-Path $ROOT "web.log") `
    -RedirectStandardError  (Join-Path $ROOT "web-error.log") `
    -PassThru
$webProc.Id | Out-File (Join-Path $ROOT ".pids\web.pid") -Encoding ascii
Write-Host "Web Client started (PID $($webProc.Id))" -ForegroundColor Green

Write-Host ""
Write-Host "Both servers started!" -ForegroundColor Yellow
Write-Host "API Server: http://localhost:5000" -ForegroundColor White
Write-Host "Web Client: http://localhost:5001" -ForegroundColor White
Write-Host ""
Write-Host "Access the Reports module at: http://localhost:5001/reports" -ForegroundColor Magenta
Write-Host ""
Write-Host "To stop: .\stop_servers.ps1"
Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
