# Hospital Stress Early Warning System - Backend

FastAPI backend for the Hospital Stress Early Warning System.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Set up BigQuery:
```bash
# Create dataset and tables using the SQL script
bq mk --dataset --location=US hospital_data
bq query --use_legacy_sql=false < config/bigquery_setup.sql
```

4. Configure Google Cloud authentication:
```bash
# Set up application default credentials
gcloud auth application-default login
```

## Running Locally

```bash
uvicorn app.main:app --reload --port 8080
```

## Running with Docker

```bash
# Build image
docker build -t hospital-stress-backend .

# Run container
docker run -p 8080:8080 --env-file .env hospital-stress-backend
```

## Testing

```bash
pytest tests/
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8080/docs
- ReDoc: http://localhost:8080/redoc
