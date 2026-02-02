-- BigQuery schema setup for Hospital Stress Early Warning System

-- Create dataset (run this first)
-- CREATE SCHEMA IF NOT EXISTS hospital_data;

-- Hospital logs table
CREATE TABLE IF NOT EXISTS hospital_data.logs (
  date DATE NOT NULL,
  admissions INT64 NOT NULL,
  beds_occupied INT64 NOT NULL,
  staff_on_duty INT64 NOT NULL,
  overload_flag BOOL NOT NULL,
  uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

-- Predictions table
CREATE TABLE IF NOT EXISTS hospital_data.predictions (
  prediction_id STRING NOT NULL,
  generated_at TIMESTAMP NOT NULL,
  forecast_date DATE NOT NULL,
  predicted_beds INT64 NOT NULL,
  bed_stress FLOAT64 NOT NULL,
  confidence FLOAT64 NOT NULL,
  is_high_risk BOOL NOT NULL
);

-- Alerts table
CREATE TABLE IF NOT EXISTS hospital_data.alerts (
  alert_id STRING NOT NULL,
  alert_type STRING NOT NULL,
  risk_score FLOAT64 NOT NULL,
  triggered_at TIMESTAMP NOT NULL,
  sent_email BOOL NOT NULL,
  sent_slack BOOL NOT NULL,
  recipients ARRAY<STRING>
);

-- Crisis history table for RAG system
CREATE TABLE IF NOT EXISTS hospital_data.crisis_history (
  crisis_id STRING NOT NULL,
  occurred_at TIMESTAMP NOT NULL,
  description STRING NOT NULL,
  resolution STRING,
  lessons_learned STRING,
  embedding ARRAY<FLOAT64>
);
