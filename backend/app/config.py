"""Configuration management for the application"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # BigQuery Configuration
    bigquery_project_id: str = ""
    bigquery_dataset: str = "hospital_data"
    
    # Vertex AI Configuration
    vertex_ai_project: str = ""
    vertex_ai_location: str = "us-central1"
    vertex_ai_model: str = "gemini-1.5-pro"
    
    # Redis Configuration
    redis_url: str = "redis://localhost:6379"
    
    # Alert Service Configuration
    email_service_api_key: Optional[str] = None
    slack_webhook_url: Optional[str] = None
    
    # Application Configuration
    prediction_cache_ttl: int = 900  # 15 minutes in seconds
    dashboard_cache_ttl: int = 30  # 30 seconds
    staff_risk_cache_ttl: int = 600  # 10 minutes
    
    # File Upload Configuration
    max_upload_size_mb: int = 50
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
