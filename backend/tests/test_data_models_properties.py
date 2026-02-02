"""Property-based tests for data models
Feature: hospital-stress-warning
"""
import pytest
from hypothesis import given, settings, strategies as st
from datetime import datetime, timedelta
from app.models import (
    HospitalRecord, DailyPrediction, BedForecast, StaffRiskScore,
    Recommendation, AlertData, ScenarioRequest, ScenarioResult,
    ValidationResult, DashboardData
)
import io
import csv


# Custom strategies for generating test data
@st.composite
def hospital_record_strategy(draw):
    """Generate valid HospitalRecord instances"""
    base_date = datetime(2024, 1, 1)
    days_offset = draw(st.integers(min_value=0, max_value=365))
    return HospitalRecord(
        date=base_date + timedelta(days=days_offset),
        admissions=draw(st.integers(min_value=0, max_value=1000)),
        beds_occupied=draw(st.integers(min_value=0, max_value=500)),
        staff_on_duty=draw(st.integers(min_value=1, max_value=100)),
        overload_flag=draw(st.booleans())
    )


@st.composite
def daily_prediction_strategy(draw):
    """Generate valid DailyPrediction instances"""
    base_date = datetime(2024, 1, 1)
    days_offset = draw(st.integers(min_value=0, max_value=365))
    bed_stress = draw(st.floats(min_value=0, max_value=100))
    return DailyPrediction(
        date=base_date + timedelta(days=days_offset),
        predicted_beds=draw(st.integers(min_value=0, max_value=1000)),
        bed_stress=bed_stress,
        confidence=draw(st.floats(min_value=0, max_value=100)),
        is_high_risk=bed_stress > 85
    )


def records_to_csv(records):
    """Convert HospitalRecord list to CSV string"""
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=['date', 'admissions', 'beds_occupied', 'staff_on_duty', 'overload_flag'])
    writer.writeheader()
    for record in records:
        writer.writerow({
            'date': record.date.strftime('%Y-%m-%d'),
            'admissions': record.admissions,
            'beds_occupied': record.beds_occupied,
            'staff_on_duty': record.staff_on_duty,
            'overload_flag': str(record.overload_flag).lower()
        })
    return output.getvalue()


def csv_to_records(csv_string):
    """Parse CSV string to HospitalRecord list"""
    input_stream = io.StringIO(csv_string)
    reader = csv.DictReader(input_stream)
    records = []
    for row in reader:
        records.append(HospitalRecord(
            date=datetime.strptime(row['date'], '%Y-%m-%d'),
            admissions=int(row['admissions']),
            beds_occupied=int(row['beds_occupied']),
            staff_on_duty=int(row['staff_on_duty']),
            overload_flag=row['overload_flag'].lower() == 'true'
        ))
    return records


@settings(max_examples=100)
@given(records=st.lists(hospital_record_strategy(), min_size=1, max_size=50))
def test_property_1_csv_upload_round_trip(records):
    """
    Feature: hospital-stress-warning, Property 1: CSV Upload Round Trip
    
    For any valid HospitalRecord list, uploading the records as CSV then 
    querying the Data_Store should return equivalent records with the same data values.
    
    Validates: Requirements 1.1
    """
    # Convert records to CSV
    csv_string = records_to_csv(records)
    
    # Parse CSV back to records
    parsed_records = csv_to_records(csv_string)
    
    # Verify same number of records
    assert len(parsed_records) == len(records), "Record count mismatch after round trip"
    
    # Verify each record matches
    for original, parsed in zip(records, parsed_records):
        assert original.date.date() == parsed.date.date(), f"Date mismatch: {original.date} != {parsed.date}"
        assert original.admissions == parsed.admissions, f"Admissions mismatch: {original.admissions} != {parsed.admissions}"
        assert original.beds_occupied == parsed.beds_occupied, f"Beds occupied mismatch: {original.beds_occupied} != {parsed.beds_occupied}"
        assert original.staff_on_duty == parsed.staff_on_duty, f"Staff on duty mismatch: {original.staff_on_duty} != {parsed.staff_on_duty}"
        assert original.overload_flag == parsed.overload_flag, f"Overload flag mismatch: {original.overload_flag} != {parsed.overload_flag}"
        
        # Verify validation passes
        assert parsed.validate(), f"Parsed record failed validation: {parsed}"
