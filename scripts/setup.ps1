# Hospital Stress Early Warning System - Setup Script (Windows)
# This script helps set up the development environment on Windows

$ErrorActionPreference = "Stop"

Write-Host "🏥 Hospital Stress Early Warning System - Setup" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Check prerequisites
Write-Host "Checking prerequisites..." -ForegroundColor Yellow

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python is not installed. Please install Python 3.11 or higher." -ForegroundColor Red
    exit 1
}

# Check Node.js
try {
    $nodeVersion = node --version
    Write-Host "✅ Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js is not installed. Please install Node.js 18 or higher." -ForegroundColor Red
    exit 1
}

# Check gcloud
try {
    $gcloudVersion = gcloud --version 2>&1 | Select-Object -First 1
    Write-Host "✅ gcloud CLI found: $gcloudVersion" -ForegroundColor Green
} catch {
    Write-Host "⚠️  gcloud CLI not found. You'll need it for Google Cloud services." -ForegroundColor Yellow
    Write-Host "   Install from: https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Setting up backend..." -ForegroundColor Yellow
Set-Location backend

# Create virtual environment
if (-not (Test-Path "venv")) {
    Write-Host "Creating Python virtual environment..."
    python -m venv venv
}

# Activate virtual environment
& .\venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "Installing Python dependencies..."
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

# Create .env if it doesn't exist
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env file from template..."
    Copy-Item .env.example .env
    Write-Host "⚠️  Please edit backend\.env with your configuration" -ForegroundColor Yellow
}

Set-Location ..

Write-Host ""
Write-Host "Setting up frontend..." -ForegroundColor Yellow
Set-Location frontend

# Install dependencies
Write-Host "Installing Node.js dependencies..."
npm install --silent

# Create .env.local if it doesn't exist
if (-not (Test-Path ".env.local")) {
    Write-Host "Creating .env.local file from template..."
    Copy-Item .env.example .env.local
    Write-Host "⚠️  Please edit frontend\.env.local with your configuration" -ForegroundColor Yellow
}

Set-Location ..

Write-Host ""
Write-Host "✅ Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Configure backend\.env with your Google Cloud credentials"
Write-Host "2. Configure frontend\.env.local with your OAuth credentials"
Write-Host "3. Set up BigQuery: bq mk --dataset hospital_data"
Write-Host "4. Run BigQuery setup: bq query --use_legacy_sql=false < backend\config\bigquery_setup.sql"
Write-Host "5. Start backend: cd backend; .\venv\Scripts\Activate.ps1; uvicorn app.main:app --reload"
Write-Host "6. Start frontend: cd frontend; npm run dev"
Write-Host ""
Write-Host "📚 See README.md for detailed instructions" -ForegroundColor Cyan
