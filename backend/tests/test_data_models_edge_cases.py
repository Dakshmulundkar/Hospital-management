"""Unit tests for data model edge cases
Tests boundary values for admissions, beds, staff counts and invalid data type handling
Requirements: 1.2
"""
import pytest
from datetime import datetime
from app.models import (
    HospitalRecord, DailyPrediction, BedForecast, StaffRiskScore,
    Recommendation, AlertData, ScenarioRequest, ScenarioResult,
    ValidationResult, DashboardData
)


class TestHospitalRecordEdgeCases:
    """Test edge cases for HospitalRecord validation"""
    
    def test_zero_values(self):
        """Test that zero values are valid"""
        record = HospitalRecord(
            date=datetime(2024, 1, 1),
            admissions=0,
            beds_occupied=0,
            staff_on_duty=0,
            overload_flag=False
        )
        assert record.validate() is True
    
    def test_negative_admissions(self):
        """Test that negative admissions are invalid"""
        record = HospitalRecord(
            date=datetime(2024, 1, 1),
            admissions=-1,
            beds_occupied=100,
            staff_on_duty=20,
            overload_flag=False
        )
        assert record.validate() is False
    
    def test_negative_beds_occupied(self):
        """Test that negative beds_occupied are invalid"""
        record = HospitalRecord(
            date=datetime(2024, 1, 1),
            admissions=50,
            beds_occupied=-1,
            staff_on_duty=20,
            overload_flag=False
        )
        assert record.validate() is False
    
    def test_negative_staff_on_duty(self):
        """Test that negative staff_on_duty are invalid"""
        record = HospitalRecord(
            date=datetime(2024, 1, 1),
            admissions=50,
            beds_occupied=100,
            staff_on_duty=-1,
            overload_flag=False
        )
        assert record.validate() is False
    
    def test_large_values(self):
        """Test that large but valid values are accepted"""
        record = HospitalRecord(
            date=datetime(2024, 1, 1),
            admissions=10000,
            beds_occupied=5000,
            staff_on_duty=1000,
            overload_flag=True
        )
        assert record.validate() is True
    
    def test_invalid_date_type(self):
        """Test that non-datetime date is invalid"""
        record = HospitalRecord(
            date="2024-01-01",  # String instead of datetime
            admissions=50,
            beds_occupied=100,
            staff_on_duty=20,
            overload_flag=False
        )
        assert record.validate() is False
    
    def test_invalid_overload_flag_type(self):
        """Test that non-boolean overload_flag is invalid"""
        record = HospitalRecord(
            date=datetime(2024, 1, 1),
            admissions=50,
            beds_occupied=100,
            staff_on_duty=20,
            overload_flag="false"  # String instead of bool
        )
        assert record.validate() is False


class TestDailyPredictionEdgeCases:
    """Test edge cases for DailyPrediction validation"""
    
    def test_bed_stress_at_boundary_85(self):
        """Test bed_stress exactly at 85% boundary"""
        prediction = DailyPrediction(
            date=datetime(2024, 1, 1),
            predicted_beds=100,
            bed_stress=85.0,
            confidence=90.0,
            is_high_risk=False  # Should be False at exactly 85
        )
        assert prediction.validate() is True
    
    def test_bed_stress_above_85(self):
        """Test bed_stress above 85% requires is_high_risk=True"""
        prediction = DailyPrediction(
            date=datetime(2024, 1, 1),
            predicted_beds=100,
            bed_stress=85.1,
            confidence=90.0,
            is_high_risk=True
        )
        assert prediction.validate() is True
    
    def test_bed_stress_above_85_wrong_flag(self):
        """Test bed_stress above 85% with is_high_risk=False is invalid"""
        prediction = DailyPrediction(
            date=datetime(2024, 1, 1),
            predicted_beds=100,
            bed_stress=86.0,
            confidence=90.0,
            is_high_risk=False  # Should be True
        )
        assert prediction.validate() is False
    
    def test_bed_stress_at_0(self):
        """Test bed_stress at 0%"""
        prediction = DailyPrediction(
            date=datetime(2024, 1, 1),
            predicted_beds=0,
            bed_stress=0.0,
            confidence=90.0,
            is_high_risk=False
        )
        assert prediction.validate() is True
    
    def test_bed_stress_at_100(self):
        """Test bed_stress at 100%"""
        prediction = DailyPrediction(
            date=datetime(2024, 1, 1),
            predicted_beds=500,
            bed_stress=100.0,
            confidence=90.0,
            is_high_risk=True
        )
        assert prediction.validate() is True
    
    def test_bed_stress_above_100(self):
        """Test bed_stress above 100% is invalid"""
        prediction = DailyPrediction(
            date=datetime(2024, 1, 1),
            predicted_beds=500,
            bed_stress=101.0,
            confidence=90.0,
            is_high_risk=True
        )
        assert prediction.validate() is False
    
    def test_confidence_below_0(self):
        """Test confidence below 0 is invalid"""
        prediction = DailyPrediction(
            date=datetime(2024, 1, 1),
            predicted_beds=100,
            bed_stress=75.0,
            confidence=-1.0,
            is_high_risk=False
        )
        assert prediction.validate() is False


class TestStaffRiskScoreEdgeCases:
    """Test edge cases for StaffRiskScore validation"""
    
    def test_risk_score_at_boundary_75(self):
        """Test risk_score exactly at 75 boundary"""
        score = StaffRiskScore(
            risk_score=75.0,
            confidence=90.0,
            is_critical=False,  # Should be False at exactly 75
            contributing_factors=["High admission rate"],
            generated_at=datetime(2024, 1, 1)
        )
        assert score.validate() is True
    
    def test_risk_score_above_75(self):
        """Test risk_score above 75 requires is_critical=True"""
        score = StaffRiskScore(
            risk_score=75.1,
            confidence=90.0,
            is_critical=True,
            contributing_factors=["High admission rate"],
            generated_at=datetime(2024, 1, 1)
        )
        assert score.validate() is True
    
    def test_risk_score_above_75_wrong_flag(self):
        """Test risk_score above 75 with is_critical=False is invalid"""
        score = StaffRiskScore(
            risk_score=80.0,
            confidence=90.0,
            is_critical=False,  # Should be True
            contributing_factors=["High admission rate"],
            generated_at=datetime(2024, 1, 1)
        )
        assert score.validate() is False
    
    def test_risk_score_at_0(self):
        """Test risk_score at 0"""
        score = StaffRiskScore(
            risk_score=0.0,
            confidence=90.0,
            is_critical=False,
            contributing_factors=[],
            generated_at=datetime(2024, 1, 1)
        )
        assert score.validate() is True
    
    def test_risk_score_at_100(self):
        """Test risk_score at 100"""
        score = StaffRiskScore(
            risk_score=100.0,
            confidence=90.0,
            is_critical=True,
            contributing_factors=["Critical staffing shortage"],
            generated_at=datetime(2024, 1, 1)
        )
        assert score.validate() is True
    
    def test_risk_score_above_100(self):
        """Test risk_score above 100 is invalid"""
        score = StaffRiskScore(
            risk_score=101.0,
            confidence=90.0,
            is_critical=True,
            contributing_factors=["Critical staffing shortage"],
            generated_at=datetime(2024, 1, 1)
        )
        assert score.validate() is False
    
    def test_empty_contributing_factors(self):
        """Test empty contributing_factors list is valid"""
        score = StaffRiskScore(
            risk_score=50.0,
            confidence=90.0,
            is_critical=False,
            contributing_factors=[],
            generated_at=datetime(2024, 1, 1)
        )
        assert score.validate() is True


class TestRecommendationEdgeCases:
    """Test edge cases for Recommendation validation"""
    
    def test_priority_1(self):
        """Test priority 1 is valid"""
        rec = Recommendation(
            title="Increase staffing",
            description="Add 5 nurses",
            rationale="High admission rate",
            cost_estimate=5000.0,
            impact_score=90.0,
            priority=1,
            implementation_time="24 hours"
        )
        assert rec.validate() is True
    
    def test_priority_3(self):
        """Test priority 3 is valid"""
        rec = Recommendation(
            title="Review protocols",
            description="Update procedures",
            rationale="Efficiency improvement",
            cost_estimate=1000.0,
            impact_score=50.0,
            priority=3,
            implementation_time="1 week"
        )
        assert rec.validate() is True
    
    def test_priority_0_invalid(self):
        """Test priority 0 is invalid"""
        rec = Recommendation(
            title="Increase staffing",
            description="Add 5 nurses",
            rationale="High admission rate",
            cost_estimate=5000.0,
            impact_score=90.0,
            priority=0,
            implementation_time="24 hours"
        )
        assert rec.validate() is False
    
    def test_priority_4_invalid(self):
        """Test priority 4 is invalid"""
        rec = Recommendation(
            title="Increase staffing",
            description="Add 5 nurses",
            rationale="High admission rate",
            cost_estimate=5000.0,
            impact_score=90.0,
            priority=4,
            implementation_time="24 hours"
        )
        assert rec.validate() is False
    
    def test_zero_cost_estimate(self):
        """Test zero cost estimate is valid"""
        rec = Recommendation(
            title="Reorganize shifts",
            description="Adjust schedules",
            rationale="Better coverage",
            cost_estimate=0.0,
            impact_score=60.0,
            priority=2,
            implementation_time="48 hours"
        )
        assert rec.validate() is True
    
    def test_negative_cost_estimate(self):
        """Test negative cost estimate is invalid"""
        rec = Recommendation(
            title="Increase staffing",
            description="Add 5 nurses",
            rationale="High admission rate",
            cost_estimate=-1000.0,
            impact_score=90.0,
            priority=1,
            implementation_time="24 hours"
        )
        assert rec.validate() is False
    
    def test_empty_title(self):
        """Test empty title is invalid"""
        rec = Recommendation(
            title="",
            description="Add 5 nurses",
            rationale="High admission rate",
            cost_estimate=5000.0,
            impact_score=90.0,
            priority=1,
            implementation_time="24 hours"
        )
        assert rec.validate() is False


class TestScenarioRequestEdgeCases:
    """Test edge cases for ScenarioRequest validation"""
    
    def test_sick_rate_at_0(self):
        """Test sick_rate at 0%"""
        req = ScenarioRequest(
            sick_rate=0.0,
            admission_surge=0.0,
            baseline_date=datetime(2024, 1, 1)
        )
        assert req.validate() is True
    
    def test_sick_rate_at_50_percent(self):
        """Test sick_rate at 50%"""
        req = ScenarioRequest(
            sick_rate=0.5,
            admission_surge=0.0,
            baseline_date=datetime(2024, 1, 1)
        )
        assert req.validate() is True
    
    def test_sick_rate_above_50_percent(self):
        """Test sick_rate above 50% is invalid"""
        req = ScenarioRequest(
            sick_rate=0.51,
            admission_surge=0.0,
            baseline_date=datetime(2024, 1, 1)
        )
        assert req.validate() is False
    
    def test_admission_surge_at_minus_30_percent(self):
        """Test admission_surge at -30%"""
        req = ScenarioRequest(
            sick_rate=0.0,
            admission_surge=-0.3,
            baseline_date=datetime(2024, 1, 1)
        )
        assert req.validate() is True
    
    def test_admission_surge_at_100_percent(self):
        """Test admission_surge at 100%"""
        req = ScenarioRequest(
            sick_rate=0.0,
            admission_surge=1.0,
            baseline_date=datetime(2024, 1, 1)
        )
        assert req.validate() is True
    
    def test_admission_surge_below_minus_30_percent(self):
        """Test admission_surge below -30% is invalid"""
        req = ScenarioRequest(
            sick_rate=0.0,
            admission_surge=-0.31,
            baseline_date=datetime(2024, 1, 1)
        )
        assert req.validate() is False
    
    def test_admission_surge_above_100_percent(self):
        """Test admission_surge above 100% is invalid"""
        req = ScenarioRequest(
            sick_rate=0.0,
            admission_surge=1.01,
            baseline_date=datetime(2024, 1, 1)
        )
        assert req.validate() is False


class TestBedForecastEdgeCases:
    """Test edge cases for BedForecast validation"""
    
    def test_exactly_7_predictions(self):
        """Test that exactly 7 predictions is valid"""
        predictions = [
            DailyPrediction(
                date=datetime(2024, 1, i),
                predicted_beds=100,
                bed_stress=75.0,
                confidence=90.0,
                is_high_risk=False
            )
            for i in range(1, 8)
        ]
        forecast = BedForecast(
            predictions=predictions,
            overall_confidence=90.0,
            generated_at=datetime(2024, 1, 1)
        )
        assert forecast.validate() is True
    
    def test_less_than_7_predictions(self):
        """Test that less than 7 predictions is invalid"""
        predictions = [
            DailyPrediction(
                date=datetime(2024, 1, i),
                predicted_beds=100,
                bed_stress=75.0,
                confidence=90.0,
                is_high_risk=False
            )
            for i in range(1, 6)
        ]
        forecast = BedForecast(
            predictions=predictions,
            overall_confidence=90.0,
            generated_at=datetime(2024, 1, 1)
        )
        assert forecast.validate() is False
    
    def test_more_than_7_predictions(self):
        """Test that more than 7 predictions is invalid"""
        predictions = [
            DailyPrediction(
                date=datetime(2024, 1, i),
                predicted_beds=100,
                bed_stress=75.0,
                confidence=90.0,
                is_high_risk=False
            )
            for i in range(1, 10)
        ]
        forecast = BedForecast(
            predictions=predictions,
            overall_confidence=90.0,
            generated_at=datetime(2024, 1, 1)
        )
        assert forecast.validate() is False


class TestAlertDataEdgeCases:
    """Test edge cases for AlertData validation"""
    
    def test_exactly_3_recommendations(self):
        """Test that exactly 3 recommendations is valid"""
        predictions = [
            DailyPrediction(
                date=datetime(2024, 1, i),
                predicted_beds=100,
                bed_stress=90.0,
                confidence=90.0,
                is_high_risk=True
            )
            for i in range(1, 8)
        ]
        recommendations = [
            Recommendation(
                title=f"Action {i}",
                description=f"Description {i}",
                rationale=f"Rationale {i}",
                cost_estimate=1000.0 * i,
                impact_score=90.0 - (i * 10),
                priority=i,
                implementation_time="24 hours"
            )
            for i in range(1, 4)
        ]
        alert = AlertData(
            alert_type="bed_stress",
            risk_score=90.0,
            threshold=85.0,
            predictions=predictions,
            recommendations=recommendations,
            generated_at=datetime(2024, 1, 1)
        )
        assert alert.validate() is True
    
    def test_less_than_3_recommendations(self):
        """Test that less than 3 recommendations is invalid"""
        predictions = [
            DailyPrediction(
                date=datetime(2024, 1, i),
                predicted_beds=100,
                bed_stress=90.0,
                confidence=90.0,
                is_high_risk=True
            )
            for i in range(1, 8)
        ]
        recommendations = [
            Recommendation(
                title="Action 1",
                description="Description 1",
                rationale="Rationale 1",
                cost_estimate=1000.0,
                impact_score=90.0,
                priority=1,
                implementation_time="24 hours"
            )
        ]
        alert = AlertData(
            alert_type="bed_stress",
            risk_score=90.0,
            threshold=85.0,
            predictions=predictions,
            recommendations=recommendations,
            generated_at=datetime(2024, 1, 1)
        )
        assert alert.validate() is False
    
    def test_threshold_at_50(self):
        """Test threshold at minimum 50"""
        predictions = [
            DailyPrediction(
                date=datetime(2024, 1, i),
                predicted_beds=100,
                bed_stress=90.0,
                confidence=90.0,
                is_high_risk=True
            )
            for i in range(1, 8)
        ]
        recommendations = [
            Recommendation(
                title=f"Action {i}",
                description=f"Description {i}",
                rationale=f"Rationale {i}",
                cost_estimate=1000.0,
                impact_score=90.0,
                priority=i,
                implementation_time="24 hours"
            )
            for i in range(1, 4)
        ]
        alert = AlertData(
            alert_type="staff_risk",
            risk_score=90.0,
            threshold=50.0,
            predictions=predictions,
            recommendations=recommendations,
            generated_at=datetime(2024, 1, 1)
        )
        assert alert.validate() is True
    
    def test_threshold_below_50(self):
        """Test threshold below 50 is invalid"""
        predictions = [
            DailyPrediction(
                date=datetime(2024, 1, i),
                predicted_beds=100,
                bed_stress=90.0,
                confidence=90.0,
                is_high_risk=True
            )
            for i in range(1, 8)
        ]
        recommendations = [
            Recommendation(
                title=f"Action {i}",
                description=f"Description {i}",
                rationale=f"Rationale {i}",
                cost_estimate=1000.0,
                impact_score=90.0,
                priority=i,
                implementation_time="24 hours"
            )
            for i in range(1, 4)
        ]
        alert = AlertData(
            alert_type="staff_risk",
            risk_score=90.0,
            threshold=49.0,
            predictions=predictions,
            recommendations=recommendations,
            generated_at=datetime(2024, 1, 1)
        )
        assert alert.validate() is False
    
    def test_invalid_alert_type(self):
        """Test invalid alert_type is rejected"""
        predictions = [
            DailyPrediction(
                date=datetime(2024, 1, i),
                predicted_beds=100,
                bed_stress=90.0,
                confidence=90.0,
                is_high_risk=True
            )
            for i in range(1, 8)
        ]
        recommendations = [
            Recommendation(
                title=f"Action {i}",
                description=f"Description {i}",
                rationale=f"Rationale {i}",
                cost_estimate=1000.0,
                impact_score=90.0,
                priority=i,
                implementation_time="24 hours"
            )
            for i in range(1, 4)
        ]
        alert = AlertData(
            alert_type="invalid_type",
            risk_score=90.0,
            threshold=85.0,
            predictions=predictions,
            recommendations=recommendations,
            generated_at=datetime(2024, 1, 1)
        )
        assert alert.validate() is False
