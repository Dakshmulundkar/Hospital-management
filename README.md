# Hospital Stress Early Warning System

AI-powered hospital capacity prediction and alerting system that forecasts bed demand and staff overload risks 7 days in advance.

## Project Structure

```
.
├── backend/              # FastAPI backend
│   ├── app/             # Application code
│   │   ├── api/         # API endpoints
│   │   ├── db/          # Database clients (BigQuery, Redis, Vertex AI)
│   │   ├── services/    # Business logic services
│   │   ├── config.py    # Configuration management
│   │   ├── main.py      # FastAPI application
│   │   └── models.py    # Data models
│   ├── config/          # Configuration files
│   │   └── bigquery_setup.sql
│   ├── tests/           # Test suite
│   ├── Dockerfile       # Docker configuration
│   └── requirements.txt # Python dependencies
│
├── frontend/            # Next.js 15 frontend
│   ├── src/
│   │   ├── app/        # Next.js App Router pages
│   │   ├── components/ # React components
│   │   └── lib/        # Utility functions
│   ├── package.json    # Node dependencies
│   └── vercel.json     # Vercel deployment config
│
└── .kiro/              # Kiro specs
    └── specs/
        └── hospital-stress-warning/
            ├── requirements.md
            ├── design.md
            └── tasks.md
```

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Google Cloud account with:
  - BigQuery API enabled
  - Vertex AI API enabled
  - Cloud Run API enabled
- Redis instance (local or cloud)

### Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your configuration

# Set up BigQuery
bq mk --dataset --location=US hospital_data
bq query --use_legacy_sql=false < config/bigquery_setup.sql

# Run locally
uvicorn app.main:app --reload --port 8080
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env.local
# Edit .env.local with your configuration

# Run locally
npm run dev
```

Visit http://localhost:3000 to see the application.

## Deployment

### Backend (Cloud Run)

```bash
cd backend

# Build and deploy
gcloud builds submit --config cloudbuild.yaml

# Or using Docker
docker build -t hospital-stress-backend .
docker run -p 8080:8080 --env-file .env hospital-stress-backend
```

### Frontend (Vercel)

```bash
cd frontend

# Deploy to Vercel
vercel deploy --prod
```

Or connect your GitHub repository to Vercel for automatic deployments.

## Architecture

- **Frontend**: Next.js 15 with App Router, Shadcn/UI, Tailwind CSS
- **Backend**: FastAPI with async support
- **Database**: BigQuery for data warehouse
- **Cache**: Redis for prediction caching
- **AI/ML**: Google Vertex AI (Gemini) for predictions
- **Auth**: NextAuth with Google OAuth
- **Deployment**: Vercel (frontend) + Cloud Run (backend)

## Features

- 7-day bed demand forecasting
- Staff overload risk assessment
- Automated email and Slack alerts
- Interactive what-if scenario simulator
- Natural language query interface
- Real-time dashboard with 30-second refresh
- Dark mode support
- Property-based testing for correctness

## Testing

### Backend Tests

```bash
cd backend
pytest tests/
```

### Frontend Tests

```bash
cd frontend
npm test
```

## Documentation

- [Requirements Document](.kiro/specs/hospital-stress-warning/requirements.md)
- [Design Document](.kiro/specs/hospital-stress-warning/design.md)
- [Implementation Tasks](.kiro/specs/hospital-stress-warning/tasks.md)
- [Backend README](backend/README.md)
- [Frontend README](frontend/README.md)

## License

Proprietary - All rights reserved
