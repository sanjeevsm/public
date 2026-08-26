#Requires -Version 5.1
[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$Root = Split-Path $PSScriptRoot -Parent
Set-Location $Root

function Write-Info  { param($m) Write-Host "[setup] $m" -ForegroundColor Green }
function Write-Warn  { param($m) Write-Host "[setup] $m" -ForegroundColor Yellow }
function Write-Fail  { param($m) Write-Host "[setup] $m" -ForegroundColor Red; exit 1 }

Write-Info "streamsource — setup"
Write-Host ""

# ── Java 21+ ──────────────────────────────────────────────────────────────────
if (-not (Get-Command java -ErrorAction SilentlyContinue)) {
    Write-Fail "Java not found. Install Java 21+ from https://adoptium.net and re-run."
}

$javaVersion = (java -version 2>&1 | Select-String 'version "(\d+)' | ForEach-Object { $_.Matches.Groups[1].Value })
if ([int]$javaVersion -lt 21) {
    Write-Fail "Java 21+ required (found $javaVersion). Install from https://adoptium.net"
}
Write-Info "Java $javaVersion found."

# ── Maven ─────────────────────────────────────────────────────────────────────
if (-not (Get-Command mvn -ErrorAction SilentlyContinue)) {
    Write-Fail "Maven not found. Install Maven 3.9+ from https://maven.apache.org/download.cgi"
}

$mvnVersion = (mvn --version 2>&1 | Select-Object -First 1).Split(" ")[2]
Write-Info "Maven $mvnVersion found."

# ── .env ──────────────────────────────────────────────────────────────────────
if (-not (Test-Path .env)) {
    Copy-Item .env.example .env
    Write-Info ".env created from .env.example — review and update values before starting."
} else {
    Write-Info ".env already exists — skipping."
}

# ── Build ─────────────────────────────────────────────────────────────────────
Write-Info "Building project (skipping tests)..."
mvn clean package -DskipTests -q
Write-Info "Build complete."

Write-Host ""
Write-Info "Setup complete. Next steps:"
Write-Host "  1. Edit .env and set JWT_SECRET and DB_PASSWORD"
Write-Host "  2. Run: .\scripts\start.ps1           (hybrid: Docker infra + local JAR)"
Write-Host "     Run: .\scripts\start.ps1 -Docker   (full Docker stack)"
