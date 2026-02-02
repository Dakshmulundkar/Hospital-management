"""Unit tests for synthetic data generator
Feature: hospital-stress-warning
"""
import pytest
from datetime import datetime, timedelta
from app.services.synthetic_data_generator import SyntheticDataGenerator
from app.models import HospitalRecord


class TestSyntheticDataGeneration:
    """Unit tests for synthetic data generation"""
    
    def test_generates_six_months_of_data(self):
        """Test that 6 months of data is generated when no data exists
        Validates: Requirements 1.6
        """
        generator = SyntheticDataGenerator(seed=42)
        end_date = datetime(2024, 6, 30)
        
        records = generator.generate_six_months(end_date=end_date)
        
        # 6 months = ~180 days, but we need to count exact days
        start_date = end_date - timedelta(days=180)
        expected_days = (end_date - start_date).days + 1  # +1 to include both start and end
        
        assert len(records) == expected_days
        assert records[0].date.date() == start_date.date()
        assert records[-1].date.date() == end_date.date()
    
    def test_generated_data_has_valid_structure(self):
        """Test that generated records have valid structure"""
        generator = SyntheticDataGenerator(seed=42)
        
        records = generator.generate_six_months()
        
        # Check all records are valid HospitalRecord objects
        assert all(isinstance(record, HospitalRecord) for record in records)
        
        # Check all records pass validation
        assert all(record.validate() for record in records)
    
    def test_generated_data_has_realistic_values(self):
        """Test that generated data has realistic hospital values"""
        generator = SyntheticDataGenerator(seed=42)
        
        records = generator.generate_six_months()
        
        # Check that values are in reasonable ranges
        for record in records:
            assert record.admissions >= 0
            assert record.beds_occupied >= 0
            assert record.staff_on_duty >= 1  # At least 1 staff member
            assert isinstance(record.overload_flag, bool)
    
    def test_generated_data_includes_weekday_weekend_patterns(self):
        """Test that generated data shows weekday/weekend variation"""
        generator = SyntheticDataGenerator(seed=42)
        end_date = datetime(2024, 6, 30)
        
        records = generator.generate_six_months(end_date=end_date)
        
        # Separate weekday and weekend records
        weekday_admissions = []
        weekend_admissions = []
        
        for record in records:
            if record.date.weekday() >= 5:  # Saturday or Sunday
                weekend_admissions.append(record.admissions)
            else:
                weekday_admissions.append(record.admissions)
        
        # Calculate averages
        avg_weekday = sum(weekday_admissions) / len(weekday_admissions)
        avg_weekend = sum(weekend_admissions) / len(weekend_admissions)
        
        # Weekend admissions should generally be lower than weekday
        # Allow some tolerance due to randomness
        assert avg_weekend < avg_weekday * 1.1
    
    def test_generated_data_includes_seasonal_variations(self):
        """Test that generated data shows seasonal patterns"""
        generator = SyntheticDataGenerator(seed=42)
        end_date = datetime(2024, 6, 30)
        
        records = generator.generate_six_months(end_date=end_date)
        
        # Separate winter and summer records
        winter_admissions = []
        summer_admissions = []
        
        for record in records:
            month = record.date.month
            if month in [12, 1, 2]:  # Winter
                winter_admissions.append(record.admissions)
            elif month in [6, 7, 8]:  # Summer
                summer_admissions.append(record.admissions)
        
        # Only compare if we have data for both seasons
        if winter_admissions and summer_admissions:
            avg_winter = sum(winter_admissions) / len(winter_admissions)
            avg_summer = sum(summer_admissions) / len(summer_admissions)
            
            # Winter admissions should generally be higher than summer
            assert avg_winter > avg_summer * 0.9
    
    def test_generated_data_includes_overload_events(self):
        """Test that generated data includes some overload events"""
        generator = SyntheticDataGenerator(seed=42)
        
        records = generator.generate_six_months()
        
        # Count overload events
        overload_count = sum(1 for record in records if record.overload_flag)
        
        # Should have at least some overload events (but not too many)
        assert overload_count > 0
        assert overload_count < len(records) * 0.5  # Less than 50% of days
    
    def test_generated_data_is_chronologically_ordered(self):
        """Test that generated data is in chronological order"""
        generator = SyntheticDataGenerator(seed=42)
        
        records = generator.generate_six_months()
        
        # Check that dates are in ascending order
        for i in range(1, len(records)):
            assert records[i].date > records[i-1].date
            # Check that dates are consecutive (1 day apart)
            assert (records[i].date - records[i-1].date).days == 1
    
    def test_generator_with_seed_is_reproducible(self):
        """Test that using the same seed produces identical results"""
        generator1 = SyntheticDataGenerator(seed=123)
        generator2 = SyntheticDataGenerator(seed=123)
        
        end_date = datetime(2024, 6, 30)
        records1 = generator1.generate_six_months(end_date=end_date)
        records2 = generator2.generate_six_months(end_date=end_date)
        
        # Should generate identical data
        assert len(records1) == len(records2)
        for r1, r2 in zip(records1, records2):
            assert r1.date == r2.date
            assert r1.admissions == r2.admissions
            assert r1.beds_occupied == r2.beds_occupied
            assert r1.staff_on_duty == r2.staff_on_duty
            assert r1.overload_flag == r2.overload_flag
    
    def test_generator_without_seed_produces_variation(self):
        """Test that generators without seed produce different results"""
        generator1 = SyntheticDataGenerator()
        generator2 = SyntheticDataGenerator()
        
        end_date = datetime(2024, 6, 30)
        records1 = generator1.generate_six_months(end_date=end_date)
        records2 = generator2.generate_six_months(end_date=end_date)
        
        # Should have same length but different values
        assert len(records1) == len(records2)
        
        # At least some values should be different
        differences = 0
        for r1, r2 in zip(records1, records2):
            if (r1.admissions != r2.admissions or 
                r1.beds_occupied != r2.beds_occupied or 
                r1.staff_on_duty != r2.staff_on_duty):
                differences += 1
        
        # Expect most records to be different due to randomness
        assert differences > len(records1) * 0.8
