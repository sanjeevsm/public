#Requires -Version 5.1
<#
.SYNOPSIS
    Starts iLab+ AI Interview Simulator as a native Windows process.
    Run setup first if this is a fresh install (venv + pip install).
#>
$ErrorActionPreference = "Stop"
$ROOT = Split-Path -Parent $PSScriptRoot
Set-Location $ROOT

function Write-Info { param($msg) Write-Host "[iLab+] $msg" -ForegroundColor Cyan }
function Write-Ok   { param($msg) Write-Host "[OK]    $msg" -ForegroundColor Green }
function Write-Warn { param($msg) Write-Host "[WARN]  $msg" -ForegroundColor Yellow }
function Write-Err  { param($msg) Write-Host "[ERROR] $msg" -ForegroundColor Red; exit 1 }

Write-Host ""
Write-Host "  iLab+  AI Interview Simulator" -ForegroundColor Cyan
Write-Host ""

# -- Check for a running instance ------------------------------------------------
$null = New-Item -ItemType Directory -Force -Path (Join-Path $ROOT ".pids")
$pidFile = Join-Path $ROOT ".pids\app.pid"

if (Test-Path $pidFile) {
    $existing = (Get-Content $pidFile -Raw).Trim()
    try {
        $proc = Get-Process -Id $existing -ErrorAction Stop
        Write-Warn "iLab+ is already running (PID $existing | Started $($proc.StartTime))"
        Write-Warn "Run .\scripts\stop.ps1 first, or delete .pids\app.pid to force a fresh start."
        exit 0
    } catch {
        Write-Warn "Stale PID file found ($existing) - cleaning up"
        Remove-Item $pidFile -Force
    }
}

# -- Python prerequisite ---------------------------------------------------------
Write-Info "Checking Python installation..."
try {
    $pyVersion = & python --version 2>&1
    Write-Ok "Found $pyVersion"
} catch {
    Write-Err "Python not found on PATH. Install Python 3.10+ and retry."
}

# -- Virtual environment ---------------------------------------------------------
$venvDir     = Join-Path $ROOT ".venv"
$venvPythonW = Join-Path $venvDir "Scripts\pythonw.exe"
$venvPip     = Join-Path $venvDir "Scripts\pip.exe"

if (-not (Test-Path $venvPythonW)) {
    Write-Info "Creating virtual environment at .venv ..."
    & python -m venv $venvDir
    if (-not (Test-Path $venvPythonW)) {
        Write-Err "Failed to create virtual environment. Check Python installation."
    }
    Write-Ok "Virtual environment created"
}

# -- Install / verify dependencies -----------------------------------------------
$markerFile = Join-Path $venvDir ".deps_installed"
$reqFile    = Join-Path $ROOT "requirements.txt"

if (-not (Test-Path $reqFile)) {
    Write-Err "requirements.txt not found at $reqFile"
}

$reinstall = $false
if (-not (Test-Path $markerFile)) {
    $reinstall = $true
} else {
    $reqTime    = (Get-Item $reqFile).LastWriteTime
    $markerTime = (Get-Item $markerFile).LastWriteTime
    if ($reqTime -gt $markerTime) {
        Write-Info "requirements.txt changed - reinstalling dependencies..."
        $reinstall = $true
    }
}

if ($reinstall) {
    Write-Info "Installing Python dependencies (this may take a minute on first run)..."
    & $venvPip install --upgrade pip --quiet
    & $venvPip install -r $reqFile
    if ($LASTEXITCODE -ne 0) {
        Write-Err "pip install failed. Check errors above."
    }
    Get-Date | Out-File $markerFile -Encoding ascii
    Write-Ok "Dependencies installed"
} else {
    Write-Ok "Dependencies up to date"
}

# -- Fix Tcl/Tk library path (Python 3.13 on Windows stores tcl under base\tcl\) -
$venvPythonExe = Join-Path $venvDir "Scripts\python.exe"
$pythonBase    = & $venvPythonExe -c "import sys; print(sys.base_prefix)"
$tclLib        = Join-Path $pythonBase "tcl\tcl8.6"
$tkLib         = Join-Path $pythonBase "tcl\tk8.6"
if (Test-Path $tclLib) {
    [System.Environment]::SetEnvironmentVariable("TCL_LIBRARY", $tclLib, "Process")
    [System.Environment]::SetEnvironmentVariable("TK_LIBRARY",  $tkLib,  "Process")
    Write-Ok "Tcl/Tk path set ($tclLib)"
}

# -- Launch iLab+ -------------------------------------------------------------
Write-Info "Launching iLab+ ..."

$appProc = Start-Process `
    -FilePath $venvPythonW `
    -ArgumentList "main.py" `
    -WorkingDirectory $ROOT `
    -PassThru

$appProc.Id | Out-File $pidFile -Encoding ascii
Write-Ok "iLab+ launched (PID $($appProc.Id))"

# -- Quick alive check -----------------------------------------------------------
Start-Sleep 3

if ($appProc.HasExited) {
    $exitCode = $appProc.ExitCode
    Remove-Item $pidFile -Force -ErrorAction SilentlyContinue
    Write-Host ""
    Write-Host "[ERROR]    iLab+ exited immediately (exit code $exitCode)." -ForegroundColor Red
    Write-Host "           Run manually to see the error:" -ForegroundColor Red
    Write-Host "           .venv\Scripts\python.exe main.py" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "  iLab+ is running!" -ForegroundColor Green
Write-Host "  PID  -> $($appProc.Id)" -ForegroundColor Green
Write-Host ""
Write-Host "To stop: .\scripts\stop.ps1" -ForegroundColor Gray
Write-Host ""
