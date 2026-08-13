# iTrack+ Local Setup Script for Windows (No Docker) - moved to scripts/

param(
    [switch]$SkipMongoCheck,
    [switch]$InstallMongo
)

Write-Host "🚀 iTrack+ Local Setup (Non-Docker)" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Resolve script and repo paths
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Join-Path $scriptDir '..'
Set-Location $repoRoot

# Check Python
Write-Host "📦 Checking Python installation..." -ForegroundColor Yellow
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Python is not installed." -ForegroundColor Red
    Write-Host "📥 Please install Python 3.11+ from: https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "   Make sure to check 'Add Python to PATH' during installation" -ForegroundColor Yellow
    exit 1
}

$pythonVersion = python --version 2>&1
Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green

# Check Node.js
Write-Host "📦 Checking Node.js installation..." -ForegroundColor Yellow
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Node.js is not installed." -ForegroundColor Red
    Write-Host "📥 Please install Node.js 16+ from: https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}

$nodeVersion = node --version
Write-Host "✅ Node.js found: $nodeVersion" -ForegroundColor Green

# Check MongoDB
if (-not $SkipMongoCheck) {
    Write-Host "📦 Checking MongoDB installation..." -ForegroundColor Yellow
    if (-not (Get-Command mongod -ErrorAction SilentlyContinue)) {
        Write-Host "⚠️  MongoDB is not installed or not in PATH." -ForegroundColor Yellow
        
        if ($InstallMongo) {
            Write-Host "📥 Installing MongoDB via Chocolatey..." -ForegroundColor Cyan
            if (-not (Get-Command choco -ErrorAction SilentlyContinue)) {
                Write-Host "❌ Chocolatey not installed. Please install MongoDB manually." -ForegroundColor Red
                Write-Host "   Download from: https://www.mongodb.com/try/download/community" -ForegroundColor Yellow
                exit 1
            }
            choco install mongodb -y
        } else {
            Write-Host ""
            Write-Host "📥 MongoDB Installation Options:" -ForegroundColor Cyan
            Write-Host "   1. Manual: https://www.mongodb.com/try/download/community" -ForegroundColor White
            Write-Host "   2. Via Chocolatey: choco install mongodb" -ForegroundColor White
            Write-Host "   3. Use MongoDB Atlas (cloud): https://www.mongodb.com/cloud/atlas" -ForegroundColor White
            Write-Host ""
            Write-Host "   Or run with -InstallMongo flag to auto-install" -ForegroundColor Yellow
            Write-Host "   Or use -SkipMongoCheck if using MongoDB Atlas" -ForegroundColor Yellow
            exit 1
        }
    } else {
        Write-Host "✅ MongoDB found" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "🔧 Setting up Backend..." -ForegroundColor Cyan
Write-Host "========================" -ForegroundColor Cyan

# Create virtual environment for backend
Set-Location backend
if (Test-Path "venv") {
    Write-Host "♻️  Virtual environment already exists, using it..." -ForegroundColor Yellow
} else {
    Write-Host "📦 Creating Python virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate virtual environment
Write-Host "🔌 Activating virtual environment..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "📥 Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

Set-Location ..

Write-Host ""
Write-Host "🎨 Setting up Frontend..." -ForegroundColor Cyan
Write-Host "========================" -ForegroundColor Cyan

Set-Location frontend

# Install npm dependencies
if (Test-Path "node_modules") {
    Write-Host "♻️  Node modules already exist, skipping install..." -ForegroundColor Yellow
} else {
    Write-Host "📥 Installing npm dependencies..." -ForegroundColor Yellow
    npm install
}

Set-Location ..

Write-Host ""
Write-Host "⚙️  Setting up environment configuration..." -ForegroundColor Cyan
Write-Host "===========================================" -ForegroundColor Cyan

# Create .env file if it doesn't exist
if (-not (Test-Path ".env")) {
    Write-Host "📝 Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    
    # Update MongoDB URL for local setup
    $envContent = Get-Content ".env" -Raw
    $envContent = $envContent -replace "mongodb://mongodb:27017", "mongodb://localhost:27017"
    Set-Content ".env" $envContent
    
    Write-Host "✅ .env file created" -ForegroundColor Green
    Write-Host "⚠️  Please update .env file with your configuration" -ForegroundColor Yellow
} else {
    Write-Host "✅ .env file already exists" -ForegroundColor Green
}

# Create frontend .env file
if (-not (Test-Path "frontend/.env")) {
    Write-Host "📝 Creating frontend .env file..." -ForegroundColor Yellow
    Set-Content "frontend/.env" "VITE_API_URL=http://localhost:8002"
    Write-Host "✅ Frontend .env file created" -ForegroundColor Green
} else {
    Write-Host "✅ Frontend .env file already exists" -ForegroundColor Green
}

Write-Host ""
Write-Host "✅ Setup Complete!" -ForegroundColor Green
Write-Host "==================" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Next Steps:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Make sure MongoDB is running:" -ForegroundColor White
Write-Host "   mongod --dbpath C:\data\db" -ForegroundColor Yellow
Write-Host "   (or start MongoDB service)" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Start the application:" -ForegroundColor White
Write-Host "   .\scripts\start-local.ps1" -ForegroundColor Yellow
Write-Host ""
Write-Host "3. Access the application:" -ForegroundColor White
Write-Host "   Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "   Backend:  http://localhost:8002" -ForegroundColor Cyan
Write-Host "   API Docs: http://localhost:8002/docs" -ForegroundColor Cyan
Write-Host ""
