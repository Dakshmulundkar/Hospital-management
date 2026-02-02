#!/bin/bash

# Hospital Stress Early Warning System - Setup Script
# This script helps set up the development environment

set -e

echo "🏥 Hospital Stress Early Warning System - Setup"
echo "================================================"
echo ""

# Check prerequisites
echo "Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11 or higher."
    exit 1
fi
echo "✅ Python 3 found: $(python3 --version)"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18 or higher."
    exit 1
fi
echo "✅ Node.js found: $(node --version)"

# Check gcloud
if ! command -v gcloud &> /dev/null; then
    echo "⚠️  gcloud CLI not found. You'll need it for Google Cloud services."
    echo "   Install from: https://cloud.google.com/sdk/docs/install"
else
    echo "✅ gcloud CLI found: $(gcloud --version | head -n 1)"
fi

echo ""
echo "Setting up backend..."
cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit backend/.env with your configuration"
fi

cd ..

echo ""
echo "Setting up frontend..."
cd frontend

# Install dependencies
echo "Installing Node.js dependencies..."
npm install --silent

# Create .env.local if it doesn't exist
if [ ! -f ".env.local" ]; then
    echo "Creating .env.local file from template..."
    cp .env.example .env.local
    echo "⚠️  Please edit frontend/.env.local with your configuration"
fi

cd ..

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Configure backend/.env with your Google Cloud credentials"
echo "2. Configure frontend/.env.local with your OAuth credentials"
echo "3. Set up BigQuery: cd backend && bq mk --dataset hospital_data"
echo "4. Run BigQuery setup: bq query --use_legacy_sql=false < config/bigquery_setup.sql"
echo "5. Start backend: cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo "6. Start frontend: cd frontend && npm run dev"
echo ""
echo "📚 See README.md for detailed instructions"
