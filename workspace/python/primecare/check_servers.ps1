# Server Health Check Script
Write-Host "PrimeCare+ Server Health Check" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Function to test endpoint
function Test-Endpoint {
    param(
        [string]$Url,
        [string]$Name
    )
    
    try {
        $response = Invoke-WebRequest -Uri $Url -TimeoutSec 5 -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-Host "✓ $Name is running" -ForegroundColor Green
            return $true
        }
    } catch {
        Write-Host "✗ $Name is not responding" -ForegroundColor Red
        Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Yellow
        return $false
    }
}

# Check API Server
Write-Host "Checking API Server (Port 5000)..." -ForegroundColor White
$apiRunning = Test-Endpoint -Url "http://localhost:5000/specialities" -Name "API Server"

Write-Host ""

# Check Web Client
Write-Host "Checking Web Client (Port 5001)..." -ForegroundColor White
$webRunning = Test-Endpoint -Url "http://localhost:5001/" -Name "Web Client"

Write-Host ""

# Check Reports Page
if ($webRunning) {
    Write-Host "Checking Reports Module..." -ForegroundColor White
    $reportsRunning = Test-Endpoint -Url "http://localhost:5001/reports" -Name "Reports Module"
} else {
    Write-Host "✗ Cannot check Reports Module (Web Client not running)" -ForegroundColor Red
    $reportsRunning = $false
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan

# Summary
if ($apiRunning -and $webRunning -and $reportsRunning) {
    Write-Host "✓ All services are running!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Access the application at:" -ForegroundColor White
    Write-Host "  Home: http://localhost:5001/" -ForegroundColor Cyan
    Write-Host "  Reports: http://localhost:5001/reports" -ForegroundColor Cyan
} else {
    Write-Host "✗ Some services are not running" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please run 'start_servers.ps1' or 'start_servers.bat' to start the servers" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
