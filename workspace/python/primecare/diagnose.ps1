# PrimeCare+ Diagnostic Script
Write-Host "PrimeCare+ Diagnostic Tool" -ForegroundColor Cyan
Write-Host "==========================" -ForegroundColor Cyan
Write-Host ""

# Check 1: Files exist
Write-Host "1. Checking files..." -ForegroundColor Yellow
$files = @(
    "C:\Users\SanjeevMenon\workspace\python\primecare\api\app.py",
    "C:\Users\SanjeevMenon\workspace\python\primecare\web-app\client.py",
    "C:\Users\SanjeevMenon\workspace\python\primecare\web-app\reports.html"
)

foreach ($file in $files) {
    if (Test-Path $file) {
        Write-Host "  ✓ $($file.Split('\')[-1]) exists" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $($file.Split('\')[-1]) missing" -ForegroundColor Red
    }
}

Write-Host ""

# Check 2: Virtual environments
Write-Host "2. Checking virtual environments..." -ForegroundColor Yellow
$venvs = @(
    "C:\Users\SanjeevMenon\workspace\python\primecare\api\venv\Scripts\python.exe",
    "C:\Users\SanjeevMenon\workspace\python\primecare\web-app\venv\Scripts\python.exe"
)

foreach ($venv in $venvs) {
    if (Test-Path $venv) {
        Write-Host "  ✓ $($venv.Split('\')[-4..-1] -join '\') exists" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $($venv.Split('\')[-4..-1] -join '\') missing" -ForegroundColor Red
    }
}

Write-Host ""

# Check 3: Ports in use
Write-Host "3. Checking if ports are in use..." -ForegroundColor Yellow
$ports = @(5000, 5001)

foreach ($port in $ports) {
    $connections = netstat -ano | Select-String ":$port "
    if ($connections) {
        Write-Host "  ⚠ Port $port is in use" -ForegroundColor Yellow
        Write-Host "    $connections" -ForegroundColor Gray
    } else {
        Write-Host "  ✓ Port $port is available" -ForegroundColor Green
    }
}

Write-Host ""

# Check 4: PostgreSQL
Write-Host "4. Checking PostgreSQL..." -ForegroundColor Yellow
try {
    $pgService = Get-Service -Name "postgresql*" -ErrorAction SilentlyContinue
    if ($pgService) {
        if ($pgService.Status -eq 'Running') {
            Write-Host "  ✓ PostgreSQL service is running" -ForegroundColor Green
        } else {
            Write-Host "  ✗ PostgreSQL service is not running" -ForegroundColor Red
            Write-Host "    Status: $($pgService.Status)" -ForegroundColor Yellow
        }
    } else {
        Write-Host "  ⚠ PostgreSQL service not found" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  ⚠ Unable to check PostgreSQL service" -ForegroundColor Yellow
}

Write-Host ""

# Check 5: API endpoints in app.py
Write-Host "5. Checking API endpoints in app.py..." -ForegroundColor Yellow
$appPyPath = "C:\Users\SanjeevMenon\workspace\python\primecare\api\app.py"
if (Test-Path $appPyPath) {
    $content = Get-Content $appPyPath -Raw
    $endpoints = @(
        "/reports/summary",
        "/reports/appointments",
        "/reports/doctors",
        "/reports/specialities",
        "/reports/patients",
        "/reports/revenue",
        "/reports/export"
    )
    
    foreach ($endpoint in $endpoints) {
        if ($content -match [regex]::Escape($endpoint)) {
            Write-Host "  ✓ $endpoint endpoint found" -ForegroundColor Green
        } else {
            Write-Host "  ✗ $endpoint endpoint missing" -ForegroundColor Red
        }
    }
}

Write-Host ""

# Check 6: Client route
Write-Host "6. Checking client route..." -ForegroundColor Yellow
$clientPyPath = "C:\Users\SanjeevMenon\workspace\python\primecare\web-app\client.py"
if (Test-Path $clientPyPath) {
    $content = Get-Content $clientPyPath -Raw
    if ($content -match "@app\.route\('/reports'\)") {
        Write-Host "  ✓ /reports route found in client.py" -ForegroundColor Green
    } else {
        Write-Host "  ✗ /reports route missing in client.py" -ForegroundColor Red
    }
    
    if ($content -match "render_template\('reports\.html'\)") {
        Write-Host "  ✓ reports.html template reference found" -ForegroundColor Green
    } else {
        Write-Host "  ✗ reports.html template reference missing" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "==========================" -ForegroundColor Cyan
Write-Host ""

# Recommendations
Write-Host "Recommendations:" -ForegroundColor Cyan
Write-Host ""
Write-Host "If all checks passed:" -ForegroundColor White
Write-Host "  1. Run 'start_servers.ps1' to start both servers" -ForegroundColor Gray
Write-Host "  2. Wait 5 seconds for servers to start" -ForegroundColor Gray
Write-Host "  3. Open http://localhost:5001/reports in browser" -ForegroundColor Gray
Write-Host ""
Write-Host "If ports are in use:" -ForegroundColor White
Write-Host "  Kill the processes using those ports or restart your computer" -ForegroundColor Gray
Write-Host ""
Write-Host "If PostgreSQL is not running:" -ForegroundColor White
Write-Host "  Start PostgreSQL service or install PostgreSQL" -ForegroundColor Gray

Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
