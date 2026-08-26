#Requires -Version 5.1
$ErrorActionPreference = 'Stop'
$Root = Split-Path $PSScriptRoot -Parent
Set-Location $Root
$PidFile = Join-Path $Root ".istream.pid"

function Write-Info { param($m) Write-Host "[start-local] $m" -ForegroundColor Green }
function Write-Warn { param($m) Write-Host "[start-local] $m" -ForegroundColor Yellow }
function Write-Fail { param($m) Write-Host "[start-local] $m" -ForegroundColor Red; exit 1 }
function Write-Link { param($m) Write-Host "  $m" -ForegroundColor Cyan }

# Resolve JDK via JAVA_HOME (process env, then machine env)
$JavaHome = $env:JAVA_HOME
if (-not $JavaHome) {
    $JavaHome = [System.Environment]::GetEnvironmentVariable("JAVA_HOME", "Machine")
}
$JavaExe = if ($JavaHome -and (Test-Path "$JavaHome\bin\java.exe")) {
    Write-Info "Using Java from JAVA_HOME: $JavaHome"
    "$JavaHome\bin\java.exe"
} else { "java" }

# Guard: already running
if (Test-Path $PidFile) {
    $existingPid = Get-Content $PidFile
    if (Get-Process -Id $existingPid -ErrorAction SilentlyContinue) {
        Write-Warn "Already running (PID $existingPid). Run .\scripts\stop-local.ps1 first."
        exit 0
    }
}

# Find JAR
$jar = Get-ChildItem "$Root\istream-app\target\istream-app-*.jar" -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $jar) { Write-Fail "JAR not found. Run: .\mvnw.cmd clean package -DskipTests" }

# Load .env
if (Test-Path "$Root\.env") {
    Get-Content "$Root\.env" | Where-Object { $_ -match '^\s*[^#]' -and $_ -match '=' } | ForEach-Object {
        $parts = $_ -split '=', 2
        [System.Environment]::SetEnvironmentVariable($parts[0].Trim(), $parts[1].Trim(), 'Process')
    }
}

$env:DB_URL      = "jdbc:postgresql://localhost:5432/istream"
$env:DB_USER     = if ($env:DB_USER)     { $env:DB_USER }     else { "istream" }
$env:DB_PASSWORD = if ($env:DB_PASSWORD) { $env:DB_PASSWORD } else { "istream" }
$env:SERVER_PORT = if ($env:SERVER_PORT) { $env:SERVER_PORT } else { "8080" }
$env:JWT_SECRET  = if ($env:JWT_SECRET)  { $env:JWT_SECRET }  else { "dev-secret-change-in-production-minimum-32-chars" }

$logsDir = Join-Path $Root "logs"
if (-not (Test-Path $logsDir)) { New-Item -ItemType Directory -Path $logsDir | Out-Null }

Write-Info "Starting iStream+ (local mode)..."
$proc = Start-Process -FilePath $JavaExe `
    -ArgumentList @(
        "-XX:MaxRAMPercentage=75.0",
        "-Djava.security.egd=file:/dev/./urandom",
        "-jar", $jar.FullName,
        "--spring.profiles.active=local"
    ) `
    -RedirectStandardOutput (Join-Path $logsDir "istream.log") `
    -RedirectStandardError  (Join-Path $logsDir "istream-err.log") `
    -PassThru -NoNewWindow

$proc.Id | Set-Content $PidFile
Write-Info "PID $($proc.Id) saved. Logs: logs\istream.log"

# Wait for readiness
Write-Info "Waiting for application to be ready..."
$ready = $false
for ($i = 0; $i -lt 30; $i++) {
    try {
        $r = Invoke-WebRequest "http://localhost:$($env:SERVER_PORT)/actuator/health" `
            -UseBasicParsing -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($r.StatusCode -eq 200) { $ready = $true; break }
    } catch {}
    Start-Sleep -Seconds 2
}

if ($ready) {
    Write-Host ""
    Write-Info "Application is ready."
    Write-Link "App      http://localhost:$($env:SERVER_PORT)"
    Write-Link "Swagger  http://localhost:$($env:SERVER_PORT)/swagger-ui.html"
    Write-Link "Health   http://localhost:$($env:SERVER_PORT)/actuator/health"
    Write-Host ""
    Write-Info "Stop with: .\scripts\stop-local.ps1"
} else {
    Write-Warn "Did not respond within 60s. Check logs\istream.log for errors."
}
