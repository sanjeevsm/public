# PrimeCare+ Startup Script
Write-Host "Starting PrimeCare+ Servers..." -ForegroundColor Cyan
Write-Host ""

# Set environment variable
$env:DB_PASSWORD = "postgres"

# Start API Server
Write-Host "Starting API Server (Port 5000)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "`$env:DB_PASSWORD='postgres'; C:\Users\SanjeevMenon\workspace\python\primecare\api\venv\Scripts\python.exe C:\Users\SanjeevMenon\workspace\python\primecare\api\app.py" -WindowStyle Normal

Start-Sleep -Seconds 3

# Start Web Client
Write-Host "Starting Web Client (Port 5001)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "`$env:DB_PASSWORD='postgres'; C:\Users\SanjeevMenon\workspace\python\primecare\web-app\venv\Scripts\python.exe C:\Users\SanjeevMenon\workspace\python\primecare\web-app\client.py" -WindowStyle Normal

Write-Host ""
Write-Host "Both servers started!" -ForegroundColor Yellow
Write-Host "API Server: http://localhost:5000" -ForegroundColor White
Write-Host "Web Client: http://localhost:5001" -ForegroundColor White
Write-Host ""
Write-Host "Access the Reports module at: http://localhost:5001/reports" -ForegroundColor Magenta
Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
