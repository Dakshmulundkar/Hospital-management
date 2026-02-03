# Hospital Stress Early Warning System

A comprehensive web application that uses AI to predict hospital capacity crises 7 days in advance, enabling proactive resource management and preventing patient care delays through intelligent forecasting and automated alerting.

## The Problem

Hospitals face critical capacity management challenges that put patient lives at risk:

- **Unpredictable surges** in patient admissions can overwhelm bed capacity within hours
- **Staff shortages** during peak periods lead to dangerous patient-to-nurse ratios
- **Reactive management** means hospitals only respond after problems occur
- **Lack of early warning** prevents proactive resource allocation and staff scheduling
- **Poor visibility** into future capacity needs makes planning impossible

These issues result in delayed patient care, staff burnout, increased mortality rates, and millions in lost revenue from diverted ambulances and cancelled procedures.

## Our Solution

An AI-powered early warning system that predicts hospital stress **7 days in advance**, giving administrators time to take preventive action:

**🔮 Predictive Intelligence**
- Forecasts bed demand using historical patterns, seasonal trends, and external factors
- Calculates staff overload risk based on patient-to-nurse ratios and workload analysis
- Provides confidence scores and risk assessments for each prediction

**⚡ Proactive Alerting**
- Automatically sends email and Slack notifications when thresholds are exceeded
- Generates prioritized action plans with cost estimates and implementation timelines
- Enables "what-if" scenario planning to test different staffing and capacity strategies

**📊 Real-time Monitoring**
- Live dashboard with 30-second refresh showing current and predicted stress levels
- Interactive charts and trend analysis to identify patterns
- Natural language AI assistant for quick insights and recommendations

**💡 Smart Recommendations**
- AI-generated action plans ranked by impact and cost-effectiveness
- Historical crisis analysis to learn from past events
- Customizable thresholds and alert preferences per hospital unit

## Quick Start

### Prerequisites

- Python 3.11+ and Node.js 18+
- Google Cloud account with BigQuery and Vertex AI enabled
- Redis instance (local or cloud)

### 1. Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Google Cloud and Redis configuration

# Set up BigQuery dataset
bq mk --dataset --location=US hospital_data
bq query --use_legacy_sql=false < config/bigquery_setup.sql

# Start the API server
uvicorn app.main:app --reload --port 8080
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env.local
# Edit .env.local with API URL and Google OAuth credentials

# Start the web application
npm run dev
```

### 3. Access the System

- **Web Interface**: http://localhost:3000
- **API Documentation**: http://localhost:8080/docs
- **Health Check**: http://localhost:8080/health

## Production Deployment

### Backend (Google Cloud Run)

```bash
cd backend
gcloud builds submit --config cloudbuild.yaml
```

### Frontend (Vercel)

```bash
cd frontend
vercel deploy --prod
```

Or connect your GitHub repository to Vercel for automatic deployments.

## Project Structure

```
├── backend/              # FastAPI backend with AI/ML services
├── frontend/             # Next.js web application
├── scripts/              # Setup and development scripts
└── SETUP.md             # Detailed setup instructions
```

## Technology Stack

**Backend (FastAPI)**
- Python 3.11+ with FastAPI for high-performance APIs
- Google BigQuery for scalable data warehousing
- Redis for real-time caching and performance
- Google Vertex AI (Gemini) for intelligent predictions
- Comprehensive testing with pytest and property-based testing

**Frontend (Next.js 15)**
- Modern React with Next.js App Router
- TypeScript for type safety and developer experience
- Tailwind CSS with Shadcn/UI for medical-grade interface design
- NextAuth with Google OAuth for secure authentication
- Real-time updates and responsive design

**Infrastructure**
- Google Cloud Run for scalable backend deployment
- Vercel for optimized frontend hosting
- Docker containerization for consistent deployments
- Automated CI/CD with health monitoring

## Key Features

**🎯 7-Day Forecasting**
- Bed demand predictions with confidence scores
- Staff overload risk assessment
- Seasonal and trend analysis
- Historical pattern recognition

**🚨 Smart Alerting**
- Configurable threshold monitoring
- Email and Slack notifications with hospital branding
- Automated retry logic for critical alerts
- Escalation policies for different risk levels

**📈 Interactive Dashboard**
- Real-time monitoring with 30-second refresh
- Trend indicators and risk visualization
- Mobile-responsive medical interface
- Dark mode support for 24/7 operations

**🔄 Scenario Planning**
- "What-if" simulations for different staffing levels
- Impact analysis for admission surges
- Cost-benefit analysis for resource allocation
- Quick preset scenarios for common situations

**🤖 AI Assistant**
- Natural language queries about hospital status
- Context-aware recommendations
- Historical crisis analysis and lessons learned
- Integration with hospital knowledge base

**📊 Data Management**
- CSV upload with comprehensive validation
- Automated data quality assessment
- Integration with existing hospital systems
- Secure data handling and privacy compliance

## Testing

```bash
# Backend tests (includes property-based testing)
cd backend && pytest tests/

# Frontend tests
cd frontend && npm test
```

## Documentation

- [Detailed Setup Guide](SETUP.md) - Complete installation and configuration
- [Backend API Documentation](http://localhost:8080/docs) - Interactive API explorer
- [Requirements Specification](.kiro/specs/hospital-stress-warning/requirements.md)
- [System Design](.kiro/specs/hospital-stress-warning/design.md)

## License

Proprietary - All rights reserved
