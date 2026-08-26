#Requires -Version 5.1
[CmdletBinding()]
param(
    [switch]$Docker
)

$ErrorActionPreference = 'Stop'
$Root = Split-Path $PSScriptRoot -Parent
Set-Location $Root
$PidFile = Join-Path $Root ".istream.pid"

function Write-Info  { param($m) Write-Host "[start] $m" -ForegroundColor Green }
function Write-Warn  { param($m) Write-Host "[start] $m" -ForegroundColor Yellow }
function Write-Fail  { param($m) Write-Host "[start] $m" -ForegroundColor Red; exit 1 }
function Write-Link  { param($m) Write-Host "  $m" -ForegroundColor Cyan }

# ── Full Docker mode ──────────────────────────────────────────────────────────
if ($Docker) {
    Write-Info "Starting full Docker stack (build + run)..."
    docker compose up --build -d
    Write-Host ""
    Write-Info "Stack is up. Access:"
    Write-Link "App         http://localhost:8080"
    Write-Link "Swagger UI  http://localhost:8080/swagger-ui.html"
    Write-Link "Prometheus  http://localhost:9090"
    Write-Link "Grafana     http://localhost:3002  (admin / admin)"
    exit 0
}

# ── Hybrid mode: Docker infra + local JAR ─────────────────────────────────────
if (Test-Path $PidFile) {
    $existingPid = Get-Content $PidFile
    if (Get-Process -Id $existingPid -ErrorAction SilentlyContinue) {
        Write-Warn "Application already running (PID $existingPid). Use .\scripts\stop.ps1 first."
        exit 0
    }
}

# Find JAR
$jar = Get-ChildItem "$Root\istream-app\target\istream-app-*.jar" -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $jar) {
    Write-Fail "JAR not found. Run .\scripts\setup.ps1 first."
}

# Start Docker infra
if (Get-Command docker -ErrorAction SilentlyContinue) {
    Write-Info "Starting infrastructure (Kafka, PostgreSQL, Redis) via Docker..."
    docker compose up -d zookeeper kafka postgres redis
    Write-Info "Waiting for services to be ready..."
    Start-Sleep -Seconds 20
} else {
    Write-Warn "Docker not found — infrastructure must be running manually."
    Write-Warn "See README.md 'Fully Local' section for manual Kafka/PostgreSQL/Redis setup."
}

# Load .env
if (Test-Path .env) {
    Get-Content .env | Where-Object { $_ -match '^\s*[^#]' -and $_ -match '=' } | ForEach-Object {
        $parts = $_ -split '=', 2
        [System.Environment]::SetEnvironmentVariable($parts[0].Trim(), $parts[1].Trim(), 'Process')
    }
    Write-Info "Loaded environment from .env"
}

$env:KAFKA_BROKERS    = if ($env:KAFKA_BROKERS)    { $env:KAFKA_BROKERS }    else { "localhost:9092" }
$env:DB_URL           = if ($env:DB_URL)           { $env:DB_URL }           else { "jdbc:postgresql://localhost:5433/istream" }
$env:DB_USER          = if ($env:DB_USER)          { $env:DB_USER }          else { "istream" }
$env:DB_PASSWORD      = if ($env:DB_PASSWORD)      { $env:DB_PASSWORD }      else { "istream" }
$env:REDIS_HOST       = if ($env:REDIS_HOST)       { $env:REDIS_HOST }       else { "localhost" }
$env:REDIS_PORT       = if ($env:REDIS_PORT)       { $env:REDIS_PORT }       else { "6379" }
$env:JWT_SECRET       = if ($env:JWT_SECRET)       { $env:JWT_SECRET }       else { "dev-secret-change-in-production-minimum-32-chars" }
$env:SERVER_PORT      = if ($env:SERVER_PORT)      { $env:SERVER_PORT }      else { "8080" }

$logsDir = Join-Path $Root "logs"
if (-not (Test-Path $logsDir)) { New-Item -ItemType Directory -Path $logsDir | Out-Null }

Write-Info "Starting iStream+..."
$proc = Start-Process java `
    -ArgumentList "-XX:MaxRAMPercentage=75.0", "-Djava.security.egd=file:/dev/./urandom", "-jar", $jar.FullName `
    -RedirectStandardOutput (Join-Path $logsDir "istream.log") `
    -RedirectStandardError  (Join-Path $logsDir "istream-err.log") `
    -PassThru -NoNewWindow

$proc.Id | Set-Content $PidFile
Write-Info "Application started (PID $($proc.Id)). Logs: logs\istream.log"

# Wait for readiness
Write-Info "Waiting for application to be ready..."
$ready = $false
for ($i = 0; $i -lt 30; $i++) {
    try {
        $r = Invoke-WebRequest "http://localhost:$($env:SERVER_PORT)/actuator/health" -UseBasicParsing -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($r.StatusCode -eq 200) { $ready = $true; break }
    } catch {}
    Start-Sleep -Seconds 2
}

if ($ready) {
    Write-Host ""
    Write-Info "Application is ready."
    Write-Link "App         http://localhost:$($env:SERVER_PORT)"
    Write-Link "Swagger UI  http://localhost:$($env:SERVER_PORT)/swagger-ui.html"
    Write-Link "Health      http://localhost:$($env:SERVER_PORT)/actuator/health"
    Write-Host ""
    Write-Info "Stop with: .\scripts\stop.ps1"
} else {
    Write-Warn "Application did not respond within 60s. Check logs\istream.log for errors."
}
