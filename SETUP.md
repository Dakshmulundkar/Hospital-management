# Hospital Stress Early Warning System - Setup Guide

This guide walks you through setting up the Hospital Stress Early Warning System from scratch.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.11+**: [Download Python](https://www.python.org/downloads/)
- **Node.js 18+**: [Download Node.js](https://nodejs.org/)
- **Google Cloud SDK**: [Install gcloud CLI](https://cloud.google.com/sdk/docs/install)
- **Redis**: Local or cloud instance
  - Local: [Download Redis](https://redis.io/download) or use Docker: `docker run -d -p 6379:6379 redis`
  - Cloud: [Redis Cloud](https://redis.com/try-free/) or [Google Cloud Memorystore](https://cloud.google.com/memorystore)

## Google Cloud Setup

### 1. Create a Google Cloud Project

```bash
# Create a new project
gcloud projects create hospital-stress-system --name="Hospital Stress System"

# Set as active project
gcloud config set project hospital-stress-system
```

### 2. Enable Required APIs

```bash
# Enable BigQuery API
gcloud services enable bigquery.googleapis.com

# Enable Vertex AI API
gcloud services enable aiplatform.googleapis.com

# Enable Cloud Run API (for deployment)
gcloud services enable run.googleapis.com

# Enable Cloud Build API (for deployment)
gcloud services enable cloudbuild.googleapis.com
```

### 3. Set Up Authentication

```bash
# Create a service account
gcloud iam service-accounts create hospital-stress-sa \
    --display-name="Hospital Stress Service Account"

# Grant necessary permissions
gcloud projects add-iam-policy-binding hospital-stress-system \
    --member="serviceAccount:hospital-stress-sa@hospital-stress-system.iam.gserviceaccount.com" \
    --role="roles/bigquery.admin"

gcloud projects add-iam-policy-binding hospital-stress-system \
    --member="serviceAccount:hospital-stress-sa@hospital-stress-system.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"

# Create and download key
gcloud iam service-accounts keys create ~/hospital-stress-key.json \
    --iam-account=hospital-stress-sa@hospital-stress-system.iam.gserviceaccount.com

# Set environment variable
export GOOGLE_APPLICATION_CREDENTIALS=~/hospital-stress-key.json
```

### 4. Set Up BigQuery

```bash
# Create dataset
bq mk --dataset --location=US hospital_data

# Create tables
cd backend
bq query --use_legacy_sql=false < config/bigquery_setup.sql
```

## Backend Setup

### 1. Install Dependencies

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your configuration
# Required variables:
# - BIGQUERY_PROJECT_ID=hospital-stress-system
# - VERTEX_AI_PROJECT=hospital-stress-system
# - REDIS_URL=redis://localhost:6379
```

### 3. Run Backend

```bash
# Start the server
uvicorn app.main:app --reload --port 8080

# Test health endpoint
curl http://localhost:8080/health
```

### 4. Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/
```

## Frontend Setup

### 1. Install Dependencies

```bash
cd frontend

# Install Node.js dependencies
npm install
```

### 2. Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env.local

# Edit .env.local with your configuration
# Required variables:
# - NEXT_PUBLIC_API_URL=http://localhost:8080
# - NEXTAUTH_URL=http://localhost:3000
# - NEXTAUTH_SECRET=<generate-a-secret>
# - GOOGLE_CLIENT_ID=<your-oauth-client-id>
# - GOOGLE_CLIENT_SECRET=<your-oauth-client-secret>
```

### 3. Set Up Google OAuth

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to "APIs & Services" > "Credentials"
3. Click "Create Credentials" > "OAuth 2.0 Client ID"
4. Choose "Web application"
5. Add authorized redirect URIs:
   - `http://localhost:3000/api/auth/callback/google` (development)
   - `https://your-domain.com/api/auth/callback/google` (production)
6. Copy Client ID and Client Secret to `.env.local`

### 4. Generate NextAuth Secret

```bash
# Generate a random secret
openssl rand -base64 32

# Or use Node.js
node -e "console.log(require('crypto').randomBytes(32).toString('base64'))"

# Add to .env.local as NEXTAUTH_SECRET
```

### 5. Run Frontend

```bash
# Start development server
npm run dev

# Open browser
# Visit http://localhost:3000
```

### 6. Run Tests

```bash
# Run all tests
npm test

# Run in watch mode
npm run test:watch
```

## Quick Setup Script

For convenience, use the provided setup scripts:

### Windows (PowerShell)

```powershell
.\scripts\setup.ps1
```

### macOS/Linux (Bash)

```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

## Verification

After setup, verify everything is working:

### 1. Backend Health Check

```bash
curl http://localhost:8080/health
# Expected: {"status":"healthy"}

curl http://localhost:8080/ready
# Expected: {"status":"ready","services":{...}}
```

### 2. Frontend Access

Open http://localhost:3000 in your browser. You should see the landing page.

### 3. Run Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## Troubleshooting

### BigQuery Connection Issues

- Verify `GOOGLE_APPLICATION_CREDENTIALS` is set correctly
- Check that the service account has BigQuery permissions
- Ensure the dataset exists: `bq ls`

### Vertex AI Connection Issues

- Verify Vertex AI API is enabled
- Check service account has `aiplatform.user` role
- Ensure project ID is correct in `.env`

### Redis Connection Issues

- Verify Redis is running: `redis-cli ping` (should return "PONG")
- Check `REDIS_URL` in `.env` is correct
- For Docker: `docker ps` to verify Redis container is running

### OAuth Issues

- Verify redirect URIs match exactly in Google Cloud Console
- Check `NEXTAUTH_URL` matches your frontend URL
- Ensure `NEXTAUTH_SECRET` is set and not empty

## Next Steps

After successful setup:

1. Review the [Requirements Document](.kiro/specs/hospital-stress-warning/requirements.md)
2. Review the [Design Document](.kiro/specs/hospital-stress-warning/design.md)
3. Start implementing tasks from [tasks.md](.kiro/specs/hospital-stress-warning/tasks.md)
4. Upload sample hospital data via CSV
5. Test predictions and alerts

## Production Deployment

See [README.md](README.md) for deployment instructions to:
- Vercel (frontend)
- Google Cloud Run (backend)

## Support

For issues or questions:
- Check the documentation in `.kiro/specs/hospital-stress-warning/`
- Review error logs in the console
- Verify all environment variables are set correctly
