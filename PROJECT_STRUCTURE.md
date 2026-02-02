# Hospital Stress Early Warning System - Project Structure

This document provides an overview of the complete project structure created for the Hospital Stress Early Warning System.

## Directory Structure

```
hospital-stress-warning/
├── .kiro/                          # Kiro specifications
│   └── specs/
│       └── hospital-stress-warning/
│           ├── requirements.md     # Requirements document
│           ├── design.md          # Design document
│           └── tasks.md           # Implementation tasks
│
├── backend/                        # FastAPI Backend
│   ├── app/                       # Application code
│   │   ├── api/                   # API endpoints (to be implemented)
│   │   ├── db/                    # Database clients
│   │   │   ├── bigquery_client.py # BigQuery client
│   │   │   ├── redis_client.py    # Redis cache client
│   │   │   └── vertex_ai_client.py # Vertex AI client
│   │   ├── services/              # Business logic (to be implemented)
│   │   ├── __init__.py
│   │   ├── config.py              # Configuration management
│   │   ├── main.py                # FastAPI application entry point
│   │   └── models.py              # Data models
│   │
│   ├── config/                    # Configuration files
│   │   ├── __init__.py
│   │   └── bigquery_setup.sql     # BigQuery schema setup
│   │
│   ├── tests/                     # Test suite
│   │   ├── __init__.py
│   │   └── test_setup.py          # Setup verification tests
│   │
│   ├── .dockerignore              # Docker ignore file
│   ├── .env.example               # Environment variables template
│   ├── cloudbuild.yaml            # Cloud Build configuration
│   ├── Dockerfile                 # Docker configuration
│   ├── pytest.ini                 # Pytest configuration
│   ├── README.md                  # Backend documentation
│   └── requirements.txt           # Python dependencies
│
├── frontend/                      # Next.js 15 Frontend
│   ├── src/
│   │   ├── app/                   # Next.js App Router
│   │   │   ├── globals.css        # Global styles
│   │   │   ├── layout.tsx         # Root layout
│   │   │   └── page.tsx           # Home page
│   │   │
│   │   ├── components/            # React components
│   │   │   └── ui/                # Shadcn/UI components
│   │   │       ├── button.tsx     # Button component
│   │   │       └── card.tsx       # Card component
│   │   │
│   │   ├── lib/                   # Utility functions
│   │   │   ├── api.ts             # API client
│   │   │   └── utils.ts           # Utility functions
│   │   │
│   │   └── types/                 # TypeScript types
│   │       └── index.ts           # Type definitions
│   │
│   ├── .env.example               # Environment variables template
│   ├── .eslintrc.json             # ESLint configuration
│   ├── .gitignore                 # Git ignore file
│   ├── next.config.js             # Next.js configuration
│   ├── package.json               # Node.js dependencies
│   ├── postcss.config.js          # PostCSS configuration
│   ├── README.md                  # Frontend documentation
│   ├── tailwind.config.ts         # Tailwind CSS configuration
│   ├── tsconfig.json              # TypeScript configuration
│   ├── vercel.json                # Vercel deployment config
│   └── vitest.config.ts           # Vitest configuration
│
├── scripts/                       # Setup scripts
│   ├── setup.ps1                  # Windows setup script
│   └── setup.sh                   # Unix/Linux setup script
│
├── .gitignore                     # Git ignore file
├── README.md                      # Main project documentation
├── SETUP.md                       # Detailed setup guide
└── PROJECT_STRUCTURE.md           # This file

```

## Key Components

### Backend (FastAPI)

**Core Files:**
- `app/main.py`: FastAPI application with health check endpoints
- `app/config.py`: Configuration management using Pydantic Settings
- `app/models.py`: Data models (HospitalRecord, BedForecast, etc.)

**Database Clients:**
- `app/db/bigquery_client.py`: BigQuery client for data storage
- `app/db/redis_client.py`: Redis client for caching
- `app/db/vertex_ai_client.py`: Vertex AI client for ML predictions

**Infrastructure:**
- `Dockerfile`: Container configuration for Cloud Run deployment
- `cloudbuild.yaml`: Google Cloud Build configuration
- `config/bigquery_setup.sql`: Database schema setup

**Testing:**
- `tests/test_setup.py`: Setup verification tests
- `pytest.ini`: Pytest configuration

### Frontend (Next.js 15)

**Core Files:**
- `src/app/page.tsx`: Landing page
- `src/app/layout.tsx`: Root layout with metadata
- `src/app/globals.css`: Global styles with Tailwind

**Components:**
- `src/components/ui/`: Shadcn/UI components (Button, Card)

**Utilities:**
- `src/lib/api.ts`: API client for backend communication
- `src/lib/utils.ts`: Utility functions (cn for class merging)

**Types:**
- `src/types/index.ts`: TypeScript type definitions

**Configuration:**
- `package.json`: Dependencies and scripts
- `tsconfig.json`: TypeScript configuration
- `tailwind.config.ts`: Tailwind CSS configuration
- `vercel.json`: Vercel deployment configuration

### Infrastructure

**Setup Scripts:**
- `scripts/setup.ps1`: Automated setup for Windows
- `scripts/setup.sh`: Automated setup for Unix/Linux

**Documentation:**
- `README.md`: Main project overview and quick start
- `SETUP.md`: Detailed setup instructions
- `backend/README.md`: Backend-specific documentation
- `frontend/README.md`: Frontend-specific documentation

**Configuration:**
- `.gitignore`: Git ignore patterns
- `.env.example` files: Environment variable templates

## Technology Stack

### Backend
- **Framework**: FastAPI 0.109.0
- **Database**: Google BigQuery
- **Cache**: Redis 5.0.1
- **AI/ML**: Google Vertex AI (Gemini 1.5 Pro)
- **Testing**: Pytest 7.4.3, Hypothesis 6.92.1
- **Deployment**: Google Cloud Run

### Frontend
- **Framework**: Next.js 15.0.3
- **UI Library**: Shadcn/UI with Radix UI
- **Styling**: Tailwind CSS 3.4.1
- **Auth**: NextAuth 5.0.0-beta.4
- **Charts**: Recharts 2.10.3
- **Testing**: Vitest 1.1.0, fast-check 3.15.0
- **Deployment**: Vercel

### Infrastructure
- **Container**: Docker
- **CI/CD**: Google Cloud Build
- **Monitoring**: Health check endpoints
- **Authentication**: Google OAuth 2.0

## Environment Variables

### Backend (.env)
```
BIGQUERY_PROJECT_ID=your-project-id
BIGQUERY_DATASET=hospital_data
VERTEX_AI_PROJECT=your-project-id
VERTEX_AI_LOCATION=us-central1
VERTEX_AI_MODEL=gemini-1.5-pro
REDIS_URL=redis://localhost:6379
EMAIL_SERVICE_API_KEY=your-sendgrid-api-key
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
PREDICTION_CACHE_TTL=900
DASHBOARD_CACHE_TTL=30
STAFF_RISK_CACHE_TTL=600
MAX_UPLOAD_SIZE_MB=50
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8080
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-secret-key-here
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

## API Endpoints

### Health Checks
- `GET /health`: Liveness probe
- `GET /ready`: Readiness probe with service checks

### To Be Implemented (Future Tasks)
- `POST /upload-logs`: Upload CSV hospital logs
- `POST /predict-beds`: Generate bed demand forecast
- `POST /staff-risk`: Calculate staff risk score
- `GET /dashboard-data`: Get dashboard summary
- `POST /recommendations`: Generate recommendations
- `POST /send-alert`: Send alert notifications
- `POST /simulate-scenario`: Run what-if simulation

## Data Models

### Core Models (Implemented)
- `HospitalRecord`: Historical hospital data
- `DailyPrediction`: Single day prediction
- `BedForecast`: 7-day forecast
- `StaffRiskScore`: Staff overload risk
- `Recommendation`: Actionable recommendation
- `AlertData`: Alert notification data
- `ScenarioRequest`: What-if scenario parameters
- `ScenarioResult`: Scenario simulation results
- `ValidationResult`: Data validation results
- `DashboardData`: Dashboard summary data

## Next Steps

1. **Task 2**: Implement data models and validation
2. **Task 3**: Implement CSV upload handler
3. **Task 4**: Implement synthetic data generation
4. **Task 6**: Implement prediction engine core
5. Continue through remaining tasks in `tasks.md`

## Development Workflow

1. Start backend: `cd backend && uvicorn app.main:app --reload`
2. Start frontend: `cd frontend && npm run dev`
3. Run backend tests: `cd backend && pytest`
4. Run frontend tests: `cd frontend && npm test`
5. Check health: `curl http://localhost:8080/health`

## Deployment Workflow

### Backend to Cloud Run
```bash
cd backend
gcloud builds submit --config cloudbuild.yaml
```

### Frontend to Vercel
```bash
cd frontend
vercel deploy --prod
```

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [BigQuery Documentation](https://cloud.google.com/bigquery/docs)
- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
- [Shadcn/UI Documentation](https://ui.shadcn.com/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
