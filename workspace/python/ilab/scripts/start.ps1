#Requires -Version 5.1
<#
.SYNOPSIS
    Starts iLab+ AI Interview Simulator.
    Use -Mode desktop (default) for the native GUI app.
    Use -Mode web for the browser-accessible web server.
.EXAMPLE
    .\scripts\start.ps1
    .\scripts\start.ps1 -Mode web
    .\scripts\start.ps1 -Mode web -Port 9000
#>
param(
    [ValidateSet("desktop", "web")]
    [string]$Mode = "desktop",
    [int]$Port = 0      # 0 = unset; resolved later from .env or default
)
$ErrorActionPreference = "Stop"
$ROOT = Split-Path -Parent $PSScriptRoot
Set-Location $ROOT

function Write-Info { param($msg) Write-Host "[iLab+] $msg" -ForegroundColor Cyan }
function Write-Ok   { param($msg) Write-Host "[OK]    $msg" -ForegroundColor Green }
function Write-Warn { param($msg) Write-Host "[WARN]  $msg" -ForegroundColor Yellow }
function Write-Err  { param($msg) Write-Host "[ERROR] $msg" -ForegroundColor Red; exit 1 }

Write-Host ""
Write-Host "  iLab+  AI Interview Simulator  [mode: $Mode]" -ForegroundColor Cyan
Write-Host ""

# -- PID file ------------------------------------------------------------------
$null = New-Item -ItemType Directory -Force -Path (Join-Path $ROOT ".pids")
$pidFile = if ($Mode -eq "web") {
    Join-Path $ROOT ".pids\web.pid"
} else {
    Join-Path $ROOT ".pids\app.pid"
}

if (Test-Path $pidFile) {
    $existing = (Get-Content $pidFile -Raw).Trim()
    try {
        $proc = Get-Process -Id $existing -ErrorAction Stop
        Write-Warn "iLab+ ($Mode) is already running (PID $existing | Started $($proc.StartTime))"
        Write-Warn "Run .\scripts\stop.ps1 -Mode $Mode first, or delete $(Split-Path $pidFile -Leaf) to force a restart."
        exit 0
    } catch {
        Write-Warn "Stale PID file found ($existing) -- cleaning up"
        Remove-Item $pidFile -Force
    }
}

# -- Python prerequisite -------------------------------------------------------
Write-Info "Checking Python installation..."
try {
    $pyVersion = & python --version 2>&1
    Write-Ok "Found $pyVersion"
} catch {
    Write-Err "Python not found on PATH. Install Python 3.10+ and retry."
}

# -- Virtual environment -------------------------------------------------------
$venvDir     = Join-Path $ROOT ".venv"
$venvPython  = Join-Path $venvDir "Scripts\python.exe"
$venvPythonW = Join-Path $venvDir "Scripts\pythonw.exe"
$venvPip     = Join-Path $venvDir "Scripts\pip.exe"

if (-not (Test-Path $venvPython)) {
    Write-Info "Creating virtual environment at .venv ..."
    & python -m venv $venvDir
    if (-not (Test-Path $venvPython)) {
        Write-Err "Failed to create virtual environment. Check Python installation."
    }
    Write-Ok "Virtual environment created"
}

# -- Dependencies --------------------------------------------------------------
if ($Mode -eq "web") {
    $reqFile    = Join-Path $ROOT "requirements-web.txt"
    $markerFile = Join-Path $venvDir ".web_deps_installed"
} else {
    $reqFile    = Join-Path $ROOT "requirements.txt"
    $markerFile = Join-Path $venvDir ".desktop_deps_installed"
}

if (-not (Test-Path $reqFile)) {
    Write-Err "$(Split-Path $reqFile -Leaf) not found at $reqFile"
}

$reinstall = $false
if (-not (Test-Path $markerFile)) {
    $reinstall = $true
} else {
    if ((Get-Item $reqFile).LastWriteTime -gt (Get-Item $markerFile).LastWriteTime) {
        Write-Info "$(Split-Path $reqFile -Leaf) changed -- reinstalling dependencies..."
        $reinstall = $true
    }
}

if ($reinstall) {
    Write-Info "Installing Python dependencies (may take a minute on first run)..."
    & $venvPip install --upgrade pip --quiet
    & $venvPip install -r $reqFile
    if ($LASTEXITCODE -ne 0) { Write-Err "pip install failed. Check errors above." }
    Get-Date | Out-File $markerFile -Encoding ascii
    Write-Ok "Dependencies installed"
} else {
    Write-Ok "Dependencies up to date"
}

# == Desktop mode ==============================================================
if ($Mode -eq "desktop") {

    # Fix Tcl/Tk library path (Python 3.13 on Windows stores tcl under base\tcl\)
    $pythonBase = & $venvPython -c "import sys; print(sys.base_prefix)"
    $tclLib     = Join-Path $pythonBase "tcl\tcl8.6"
    $tkLib      = Join-Path $pythonBase "tcl\tk8.6"
    if (Test-Path $tclLib) {
        [System.Environment]::SetEnvironmentVariable("TCL_LIBRARY", $tclLib, "Process")
        [System.Environment]::SetEnvironmentVariable("TK_LIBRARY",  $tkLib,  "Process")
        Write-Ok "Tcl/Tk path set ($tclLib)"
    }

    Write-Info "Launching iLab+ desktop app ..."
    $appProc = Start-Process `
        -FilePath      $venvPythonW `
        -ArgumentList  "main.py" `
        -WorkingDirectory $ROOT `
        -PassThru

    $appProc.Id | Out-File $pidFile -Encoding ascii
    Write-Ok "Desktop app launched (PID $($appProc.Id))"

    Start-Sleep 3
    if ($appProc.HasExited) {
        Remove-Item $pidFile -Force -ErrorAction SilentlyContinue
        Write-Host ""
        Write-Host "[ERROR] iLab+ exited immediately (exit code $($appProc.ExitCode))." -ForegroundColor Red
        Write-Host "        Run manually to see the error:" -ForegroundColor Red
        Write-Host "        .venv\Scripts\python.exe main.py" -ForegroundColor Yellow
        exit 1
    }

    Write-Host ""
    Write-Host "  iLab+ desktop is running!" -ForegroundColor Green
    Write-Host "  PID -> $($appProc.Id)" -ForegroundColor Green
    Write-Host ""
    Write-Host "  To stop: .\scripts\stop.ps1" -ForegroundColor Gray
    Write-Host ""

# == Web mode ==================================================================
} else {

    # Load .env if present (key=value pairs, # comments ignored)
    $envFile = Join-Path $ROOT ".env"
    if (Test-Path $envFile) {
        Get-Content $envFile | ForEach-Object {
            if ($_ -match '^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$') {
                $k = $Matches[1]
                $v = $Matches[2].Trim().Trim('"').Trim("'")
                if ($k -and -not $k.StartsWith('#')) {
                    [System.Environment]::SetEnvironmentVariable($k, $v, "Process")
                }
            }
        }
        Write-Ok "Loaded .env"
    } else {
        Write-Warn ".env not found -- copy .env.example to .env to configure ILAB_SECRET and PORT"
    }

    # Resolve port: -Port parameter > .env PORT > default 8000
    if ($Port -gt 0) {
        # -Port flag wins
    } elseif ([System.Environment]::GetEnvironmentVariable("PORT")) {
        $Port = [int][System.Environment]::GetEnvironmentVariable("PORT")
    } else {
        $Port = 8000
    }

    # Resolve bind host: .env HOST > default 0.0.0.0 (all interfaces = LAN accessible)
    $BindHost = [System.Environment]::GetEnvironmentVariable("HOST")
    if (-not $BindHost) { $BindHost = "0.0.0.0" }

    # Warn if session secret is unset
    if (-not [System.Environment]::GetEnvironmentVariable("ILAB_SECRET")) {
        Write-Warn "ILAB_SECRET is not set -- a random secret is generated each restart."
        Write-Warn "User sessions are lost on restart. Set ILAB_SECRET in .env to persist them."
    }

    # Note: Gunicorn does not support Windows natively.
    # Flask's built-in server (threaded=True, debug=False) is used here.
    # For production on Windows, use WSL + Gunicorn, or deploy to Linux.
    Write-Warn "Gunicorn is not supported on Windows -- using Flask built-in server."
    Write-Warn "For production deployments use WSL/Linux with Gunicorn (see wsgi.py)."

    Write-Info "Starting iLab+ web server on $BindHost`:$Port ..."

    # Set env vars for the child process (inherited on Windows)
    $env:HOST        = $BindHost
    $env:PORT        = "$Port"
    $env:FLASK_DEBUG = "0"

    $logFile = Join-Path $ROOT ".pids\web.log"

    $webProc = Start-Process `
        -FilePath         $venvPython `
        -ArgumentList     "flask_app.py" `
        -WorkingDirectory $ROOT `
        -RedirectStandardOutput $logFile `
        -RedirectStandardError  $logFile `
        -NoNewWindow `
        -PassThru

    $webProc.Id | Out-File $pidFile -Encoding ascii
    Write-Ok "Web server launched (PID $($webProc.Id))"

    Start-Sleep 3
    if ($webProc.HasExited) {
        Remove-Item $pidFile -Force -ErrorAction SilentlyContinue
        Write-Host ""
        Write-Host "  Last log output:" -ForegroundColor Yellow
        if (Test-Path $logFile) { Get-Content $logFile -Tail 20 }
        Write-Host ""
        Write-Host "[ERROR] Web server exited immediately (exit code $($webProc.ExitCode))." -ForegroundColor Red
        Write-Host "        Check $logFile for details." -ForegroundColor Yellow
        Write-Host "        Or run manually: .venv\Scripts\python.exe flask_app.py" -ForegroundColor Yellow
        exit 1
    }

    # Resolve LAN IP for the network access URL
    $lanIP = (Get-NetIPAddress -AddressFamily IPv4 |
              Where-Object { $_.IPAddress -notmatch '^(127\.|169\.254\.)' -and $_.PrefixOrigin -ne 'WellKnown' } |
              Sort-Object -Property { ($_.IPAddress -split '\.')[0..2] -join '.' } |
              Select-Object -Last 1).IPAddress

    Write-Host ""
    Write-Host "  iLab+ web is running!" -ForegroundColor Green
    Write-Host "  PID         -> $($webProc.Id)" -ForegroundColor Green
    Write-Host "  Local URL   -> http://localhost:$Port" -ForegroundColor Green
    if ($lanIP) {
        Write-Host "  Network URL -> http://${lanIP}:$Port  (share this with others on your LAN)" -ForegroundColor Cyan
    }
    Write-Host "  Logs        -> $logFile" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  Each user opens the URL in their browser and enters" -ForegroundColor Gray
    Write-Host "  their own API key in Settings -- keys never leave their browser." -ForegroundColor Gray
    Write-Host ""
    Write-Host "  To stop: .\scripts\stop.ps1 -Mode web" -ForegroundColor Gray
    Write-Host ""
}
