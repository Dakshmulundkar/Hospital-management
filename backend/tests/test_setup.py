"""Test to verify project setup is correct"""
import pytest
from app.config import settings
from app.models import HospitalRecord, BedForecast, DailyPrediction
from datetime import datetime


def test_settings_loaded():
    """Test that settings are loaded"""
    assert settings is not None
    assert settings.bigquery_dataset == "hospital_data"


def test_hospital_record_validation():
    """Test HospitalRecord validation"""
    # Valid record
    record = HospitalRecord(
        date=datetime.now(),
        admissions=50,
        beds_occupied=100,
        staff_on_duty=20,
        overload_flag=False
    )
    assert record.validate() is True
    
    # Invalid record (negative values)
    invalid_record = HospitalRecord(
        date=datetime.now(),
        admissions=-5,
        beds_occupied=100,
        staff_on_duty=20,
        overload_flag=False
    )
    assert invalid_record.validate() is False


def test_daily_prediction_structure():
    """Test DailyPrediction data structure"""
    prediction = DailyPrediction(
        date=datetime.now(),
        predicted_beds=120,
        bed_stress=85.5,
        confidence=92.0,
        is_high_risk=True
    )
    assert prediction.predicted_beds == 120
    assert prediction.bed_stress == 85.5
    assert prediction.is_high_risk is True


def test_bed_forecast_structure():
    """Test BedForecast data structure"""
    predictions = [
        DailyPrediction(
            date=datetime.now(),
            predicted_beds=100,
            bed_stress=75.0,
            confidence=90.0,
            is_high_risk=False
        )
    ]
    forecast = BedForecast(
        predictions=predictions,
        overall_confidence=90.0,
        generated_at=datetime.now()
    )
    assert len(forecast.predictions) == 1
    assert forecast.overall_confidence == 90.0
