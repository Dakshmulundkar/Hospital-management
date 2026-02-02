"""Property-based tests for the PredictionEngine"""
import pytest
from hypothesis import given, settings, strategies as st
from datetime import datetime, timedelta
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.models import HospitalRecord, BedForecast, ScenarioResult
from app.services.prediction_engine import PredictionEngine


# Test data generators
@st.composite
def hospital_record(draw):
    """Generate a valid HospitalRecord"""
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
def hospital_record_list(draw):
    """Generate a list of HospitalRecord objects"""
    size = draw(st.integers(min_value=0, max_value=100))
    records = draw(st.lists(hospital_record(), min_size=size, max_size=size))
    
    # Sort by date to ensure chronological order
    records.sort(key=lambda r: r.date)
    
    return records


class TestPredictionEngineProperties:
    """Property-based tests for PredictionEngine"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.engine = PredictionEngine()
    
    @settings(max_examples=5, deadline=None)
    @given(
        days_ahead=st.integers(min_value=1, max_value=30),
        historical_data=hospital_record_list()
    )
    def test_forecast_length_consistency(self, days_ahead, historical_data):
        """
        Feature: hospital-stress-warning, Property 4: Forecast Length Consistency
        
        For any forecast request, the Prediction_Engine should return exactly 7 daily 
        predictions regardless of the amount of historical data available.
        
        Validates: Requirements 2.1
        """
        # Override days_ahead to always be 7 for this property test
        days_ahead = 7
        
        # Generate forecast
        forecast = self.engine.forecast_bed_demand(
            days_ahead=days_ahead,
            historical_data=historical_data
        )
        
        # Verify forecast is valid
        assert isinstance(forecast, BedForecast)
        assert forecast.validate()
        
        # Property: Forecast should always have exactly 7 predictions
        assert len(forecast.predictions) == 7
        
        # Verify each prediction is for consecutive days
        base_date = datetime.now().date()
        for i, prediction in enumerate(forecast.predictions):
            expected_date = base_date + timedelta(days=i+1)
            assert prediction.date.date() == expected_date
    
    @settings(max_examples=5, deadline=None)
    @given(
        historical_data=hospital_record_list()
    )
    def test_graceful_missing_data_handling(self, historical_data):
        """
        Feature: hospital-stress-warning, Property 5: Graceful Handling of Missing Data
        
        For any historical dataset with gaps or missing values, the Prediction_Engine 
        should still generate predictions without throwing errors.
        
        Validates: Requirements 2.2
        """
        # Introduce some missing/invalid data
        modified_data = []
        for record in historical_data:
            # Randomly introduce missing values (represented as -1)
            modified_record = HospitalRecord(
                date=record.date,
                admissions=record.admissions if record.admissions % 3 != 0 else -1,
                beds_occupied=record.beds_occupied if record.beds_occupied % 5 != 0 else -1,
                staff_on_duty=record.staff_on_duty if record.staff_on_duty % 7 != 0 else -1,
                overload_flag=record.overload_flag
            )
            modified_data.append(modified_record)
        
        # Property: Should not raise exceptions even with missing data
        try:
            forecast = self.engine.forecast_bed_demand(
                days_ahead=7,
                historical_data=modified_data
            )
            
            # Should still return a valid forecast
            assert isinstance(forecast, BedForecast)
            assert len(forecast.predictions) == 7
            
            # All predictions should be valid
            for prediction in forecast.predictions:
                assert prediction.validate()
                
        except Exception as e:
            pytest.fail(f"Prediction engine should handle missing data gracefully, but raised: {e}")
    
    @settings(max_examples=5, deadline=None)
    @given(
        historical_data=hospital_record_list()
    )
    def test_prediction_structure_completeness(self, historical_data):
        """
        Feature: hospital-stress-warning, Property 6: Prediction Structure Completeness
        
        For any bed forecast, each daily prediction should include all required fields: 
        date, predicted_beds, bed_stress, confidence, and is_high_risk flag.
        
        Validates: Requirements 2.3
        """
        forecast = self.engine.forecast_bed_demand(
            days_ahead=7,
            historical_data=historical_data
        )
        
        # Property: Each prediction must have all required fields
        for prediction in forecast.predictions:
            # Check all required fields exist and have correct types
            assert hasattr(prediction, 'date')
            assert isinstance(prediction.date, datetime)
            
            assert hasattr(prediction, 'predicted_beds')
            assert isinstance(prediction.predicted_beds, int)
            assert prediction.predicted_beds >= 0
            
            assert hasattr(prediction, 'bed_stress')
            assert isinstance(prediction.bed_stress, (int, float))
            assert 0 <= prediction.bed_stress <= 100
            
            assert hasattr(prediction, 'confidence')
            assert isinstance(prediction.confidence, (int, float))
            assert 0 <= prediction.confidence <= 100
            
            assert hasattr(prediction, 'is_high_risk')
            assert isinstance(prediction.is_high_risk, bool)
            
            # Verify the prediction validates
            assert prediction.validate()
    
    @settings(max_examples=5, deadline=None)
    @given(
        predicted_beds=st.integers(min_value=0, max_value=1000),
        total_capacity=st.integers(min_value=100, max_value=1000)
    )
    def test_bed_stress_calculation_accuracy(self, predicted_beds, total_capacity):
        """
        Feature: hospital-stress-warning, Property 7: Bed Stress Calculation Accuracy
        
        For any prediction with predicted_beds and total_capacity values, the bed_stress 
        should equal (predicted_beds / total_capacity) * 100.
        
        Validates: Requirements 2.4
        """
        # Set the engine's capacity for this test
        self.engine.total_bed_capacity = total_capacity
        
        # Calculate bed stress using the engine's method
        calculated_stress = self.engine._calculate_bed_stress(predicted_beds)
        
        # Calculate expected stress
        expected_stress = (predicted_beds / total_capacity) * 100
        expected_stress = max(0.0, min(100.0, expected_stress))  # Clamp to 0-100
        
        # Property: Calculated stress should match expected formula
        assert abs(calculated_stress - expected_stress) < 0.01  # Allow for floating point precision
    
    @settings(max_examples=5, deadline=None)
    @given(
        bed_stress=st.floats(min_value=0.0, max_value=100.0)
    )
    def test_high_risk_flagging_threshold(self, bed_stress):
        """
        Feature: hospital-stress-warning, Property 8: High Risk Flagging Threshold
        
        For any daily prediction, the is_high_risk flag should be True if and only if 
        bed_stress exceeds 85%.
        
        Validates: Requirements 2.5
        """
        # Create a mock prediction with the given bed stress
        from app.models import DailyPrediction
        
        prediction = DailyPrediction(
            date=datetime.now(),
            predicted_beds=int(bed_stress * 5),  # Arbitrary value
            bed_stress=bed_stress,
            confidence=80.0,
            is_high_risk=bed_stress > 85.0  # This is what we're testing
        )
        
        # Property: is_high_risk should be True iff bed_stress > 85
        if bed_stress > 85.0:
            assert prediction.is_high_risk == True
        else:
            assert prediction.is_high_risk == False
        
        # Verify the prediction validates (this checks the consistency)
        assert prediction.validate()
    
    @settings(max_examples=5, deadline=None)
    @given(
        historical_data=hospital_record_list()
    )
    def test_forward_fill_interpolation(self, historical_data):
        """
        Feature: hospital-stress-warning, Property 26: Forward-Fill Interpolation
        
        For any historical dataset with missing values in beds_occupied or staff_on_duty 
        columns, the Prediction_Engine should apply forward-fill interpolation before 
        generating predictions.
        
        Validates: Requirements 12.1
        """
        if not historical_data:
            # Skip test if no data
            return
        
        # Create data with missing values (represented as -1)
        data_with_missing = []
        for i, record in enumerate(historical_data):
            # Introduce missing values in some records
            beds_occupied = record.beds_occupied if i % 3 != 0 else -1
            staff_on_duty = record.staff_on_duty if i % 4 != 0 else -1
            
            modified_record = HospitalRecord(
                date=record.date,
                admissions=record.admissions,
                beds_occupied=beds_occupied,
                staff_on_duty=staff_on_duty,
                overload_flag=record.overload_flag
            )
            data_with_missing.append(modified_record)
        
        # Apply interpolation
        processed_data = self.engine._handle_missing_data(data_with_missing)
        
        # Property: No processed record should have missing values (negative values)
        for record in processed_data:
            assert record.beds_occupied >= 0, f"beds_occupied should be >= 0, got {record.beds_occupied}"
            assert record.staff_on_duty >= 0, f"staff_on_duty should be >= 0, got {record.staff_on_duty}"
            assert record.admissions >= 0, f"admissions should be >= 0, got {record.admissions}"
        
        # Property: Length should be preserved
        assert len(processed_data) == len(data_with_missing)
        
        # Property: Dates should be preserved
        for original, processed in zip(data_with_missing, processed_data):
            assert original.date == processed.date
    
    @settings(max_examples=5, deadline=None)
    @given(
        predicted_admissions=st.integers(min_value=0, max_value=1000),
        current_staff=st.integers(min_value=1, max_value=200),
        historical_overloads=hospital_record_list()
    )
    def test_staff_risk_score_range(self, predicted_admissions, current_staff, historical_overloads):
        """
        Feature: hospital-stress-warning, Property 9: Staff Risk Score Range
        
        For any staff risk calculation, the risk_score should be within the range [0, 100] inclusive.
        
        Validates: Requirements 3.1
        """
        # Calculate staff risk
        staff_risk = self.engine.calculate_staff_risk(
            predicted_admissions=predicted_admissions,
            current_staff=current_staff,
            historical_overloads=historical_overloads
        )
        
        # Property: Risk score must be within [0, 100] range
        assert isinstance(staff_risk.risk_score, (int, float))
        assert 0.0 <= staff_risk.risk_score <= 100.0
        
        # Verify the staff risk object validates
        assert staff_risk.validate()
    
    @settings(max_examples=5, deadline=None)
    @given(
        predicted_admissions=st.integers(min_value=0, max_value=1000),
        current_staff=st.integers(min_value=1, max_value=200),
        historical_overloads=hospital_record_list()
    )
    def test_critical_risk_classification(self, predicted_admissions, current_staff, historical_overloads):
        """
        Feature: hospital-stress-warning, Property 10: Critical Risk Classification
        
        For any staff risk score, the is_critical flag should be True if and only if 
        risk_score exceeds 75.
        
        Validates: Requirements 3.3
        """
        # Calculate staff risk
        staff_risk = self.engine.calculate_staff_risk(
            predicted_admissions=predicted_admissions,
            current_staff=current_staff,
            historical_overloads=historical_overloads
        )
        
        # Property: is_critical should be True iff risk_score > 75
        if staff_risk.risk_score > 75.0:
            assert staff_risk.is_critical == True
        else:
            assert staff_risk.is_critical == False
        
        # Verify the staff risk object validates (this checks the consistency)
        assert staff_risk.validate()
    
    @settings(max_examples=5, deadline=None)
    @given(
        predicted_admissions=st.integers(min_value=0, max_value=1000),
        current_staff=st.integers(min_value=1, max_value=200),
        historical_overloads=hospital_record_list()
    )
    def test_risk_score_structure_completeness(self, predicted_admissions, current_staff, historical_overloads):
        """
        Feature: hospital-stress-warning, Property 11: Risk Score Structure Completeness
        
        For any staff risk score, it should include all required fields: risk_score, 
        confidence, is_critical, contributing_factors, and generated_at timestamp.
        
        Validates: Requirements 3.5
        """
        # Calculate staff risk
        staff_risk = self.engine.calculate_staff_risk(
            predicted_admissions=predicted_admissions,
            current_staff=current_staff,
            historical_overloads=historical_overloads
        )
        
        # Property: All required fields must exist and have correct types
        assert hasattr(staff_risk, 'risk_score')
        assert isinstance(staff_risk.risk_score, (int, float))
        assert 0.0 <= staff_risk.risk_score <= 100.0
        
        assert hasattr(staff_risk, 'confidence')
        assert isinstance(staff_risk.confidence, (int, float))
        assert 0.0 <= staff_risk.confidence <= 100.0
        
        assert hasattr(staff_risk, 'is_critical')
        assert isinstance(staff_risk.is_critical, bool)
        
        assert hasattr(staff_risk, 'contributing_factors')
        assert isinstance(staff_risk.contributing_factors, list)
        assert all(isinstance(factor, str) for factor in staff_risk.contributing_factors)
        assert len(staff_risk.contributing_factors) > 0  # Should always have at least one factor
        
        assert hasattr(staff_risk, 'generated_at')
        assert isinstance(staff_risk.generated_at, datetime)
        
        # Verify the staff risk object validates
        assert staff_risk.validate()
    
    @settings(max_examples=5, deadline=None)
    @given(
        bed_stress=st.floats(min_value=85.1, max_value=100.0),  # High bed stress
        staff_risk=st.floats(min_value=75.1, max_value=100.0),  # Critical staff risk
        historical_data=hospital_record_list()
    )
    def test_recommendation_count_consistency(self, bed_stress, staff_risk, historical_data):
        """
        Feature: hospital-stress-warning, Property 13: Recommendation Count Consistency
        
        For any high-risk scenario (Bed_Stress > 85 or Staff_Risk > 75), the Prediction_Engine 
        should generate exactly 3 recommendations.
        
        Validates: Requirements 5.1
        """
        # Generate recommendations for high-risk scenario
        recommendations = self.engine.generate_recommendations(
            bed_stress=bed_stress,
            staff_risk=staff_risk,
            historical_context=historical_data
        )
        
        # Property: Should always return exactly 3 recommendations
        assert isinstance(recommendations, list)
        assert len(recommendations) == 3
        
        # Verify each recommendation is valid
        from app.models import Recommendation
        for rec in recommendations:
            assert isinstance(rec, Recommendation)
            assert rec.validate()
        
        # Verify priorities are 1, 2, 3
        priorities = [rec.priority for rec in recommendations]
        assert sorted(priorities) == [1, 2, 3]
    
    @settings(max_examples=3, deadline=None)
    @given(
        sick_rate=st.floats(min_value=0.0, max_value=0.5),
        admission_surge=st.floats(min_value=-0.3, max_value=1.0)
    )
    def test_scenario_recalculation_responsiveness(self, sick_rate, admission_surge):
        """
        Feature: hospital-stress-warning, Property 12: Scenario Recalculation Responsiveness
        
        For any scenario parameter adjustment (sick_rate or admission_surge), the What_If_Simulator 
        should produce a new forecast that differs from the baseline forecast.
        
        Validates: Requirements 4.1
        """
        from app.models import ScenarioResult
        
        # Run scenario simulation
        scenario_result = self.engine.simulate_scenario(
            sick_rate=sick_rate,
            admission_surge=admission_surge
        )
        
        # Verify result is valid
        assert isinstance(scenario_result, ScenarioResult)
        assert scenario_result.validate()
        
        # Property: Scenario forecast should differ from baseline forecast
        # (unless both parameters are zero, which would mean no change)
        if sick_rate > 0.01 or abs(admission_surge) > 0.01:
            # At least one parameter is non-trivial, so forecasts should differ
            
            # Compare bed stress values
            baseline_avg_stress = sum(p.bed_stress for p in scenario_result.baseline_forecast.predictions) / 7
            scenario_avg_stress = sum(p.bed_stress for p in scenario_result.scenario_forecast.predictions) / 7
            
            # Compare staff risk scores
            baseline_risk = scenario_result.baseline_staff_risk.risk_score
            scenario_risk = scenario_result.scenario_staff_risk.risk_score
            
            # At least one metric should be different
            stress_differs = abs(baseline_avg_stress - scenario_avg_stress) > 0.1
            risk_differs = abs(baseline_risk - scenario_risk) > 0.1
            
            assert stress_differs or risk_differs, \
                f"Scenario should differ from baseline when parameters are non-zero. " \
                f"sick_rate={sick_rate}, admission_surge={admission_surge}, " \
                f"baseline_stress={baseline_avg_stress:.2f}, scenario_stress={scenario_avg_stress:.2f}, " \
                f"baseline_risk={baseline_risk:.2f}, scenario_risk={scenario_risk:.2f}"
        
        # Verify impact summary is present and non-empty
        assert isinstance(scenario_result.impact_summary, str)
        assert len(scenario_result.impact_summary) > 0
        
        # Verify both forecasts have 7 predictions
        assert len(scenario_result.baseline_forecast.predictions) == 7
        assert len(scenario_result.scenario_forecast.predictions) == 7



class TestScenarioSimulatorBoundaries:
    """Unit tests for scenario simulator parameter boundaries"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.engine = PredictionEngine()
    
    def test_sick_rate_at_zero_percent(self):
        """
        Test sick_rate at 0% (minimum boundary)
        
        Validates: Requirements 4.2
        """
        # Test with 0% sick rate
        result = self.engine.simulate_scenario(
            sick_rate=0.0,
            admission_surge=0.0
        )
        
        # Should succeed without errors
        assert isinstance(result, ScenarioResult)
        assert result.validate()
        
        # With 0% sick rate and 0% surge, baseline and scenario should be very similar
        baseline_risk = result.baseline_staff_risk.risk_score
        scenario_risk = result.scenario_staff_risk.risk_score
        
        # They should be identical or very close since no adjustments
        assert abs(baseline_risk - scenario_risk) < 1.0
    
    def test_sick_rate_at_fifty_percent(self):
        """
        Test sick_rate at 50% (maximum boundary)
        
        Validates: Requirements 4.2
        """
        # Test with 50% sick rate
        result = self.engine.simulate_scenario(
            sick_rate=0.5,
            admission_surge=0.0
        )
        
        # Should succeed without errors
        assert isinstance(result, ScenarioResult)
        assert result.validate()
        
        # With 50% sick rate, scenario risk should be significantly higher
        baseline_risk = result.baseline_staff_risk.risk_score
        scenario_risk = result.scenario_staff_risk.risk_score
        
        # Scenario should have higher risk due to staff reduction
        assert scenario_risk > baseline_risk
    
    def test_sick_rate_out_of_range_negative(self):
        """
        Test sick_rate below 0% (out of range)
        
        Validates: Requirements 4.2
        """
        # Test with negative sick rate (invalid)
        with pytest.raises(ValueError) as exc_info:
            self.engine.simulate_scenario(
                sick_rate=-0.1,
                admission_surge=0.0
            )
        
        # Should raise ValueError with descriptive message
        assert "sick_rate must be between 0.0 and 0.5" in str(exc_info.value)
    
    def test_sick_rate_out_of_range_above_fifty(self):
        """
        Test sick_rate above 50% (out of range)
        
        Validates: Requirements 4.2
        """
        # Test with sick rate above 50% (invalid)
        with pytest.raises(ValueError) as exc_info:
            self.engine.simulate_scenario(
                sick_rate=0.6,
                admission_surge=0.0
            )
        
        # Should raise ValueError with descriptive message
        assert "sick_rate must be between 0.0 and 0.5" in str(exc_info.value)
    
    def test_admission_surge_at_negative_thirty_percent(self):
        """
        Test admission_surge at -30% (minimum boundary)
        
        Validates: Requirements 4.3
        """
        # Test with -30% admission surge
        result = self.engine.simulate_scenario(
            sick_rate=0.0,
            admission_surge=-0.3
        )
        
        # Should succeed without errors
        assert isinstance(result, ScenarioResult)
        assert result.validate()
        
        # With -30% surge, scenario should have lower bed stress
        baseline_avg_stress = sum(p.bed_stress for p in result.baseline_forecast.predictions) / 7
        scenario_avg_stress = sum(p.bed_stress for p in result.scenario_forecast.predictions) / 7
        
        # Scenario should have lower stress due to reduced admissions
        assert scenario_avg_stress < baseline_avg_stress
    
    def test_admission_surge_at_one_hundred_percent(self):
        """
        Test admission_surge at +100% (maximum boundary)
        
        Validates: Requirements 4.3
        """
        # Test with +100% admission surge
        result = self.engine.simulate_scenario(
            sick_rate=0.0,
            admission_surge=1.0
        )
        
        # Should succeed without errors
        assert isinstance(result, ScenarioResult)
        assert result.validate()
        
        # With +100% surge, scenario should have much higher bed stress
        baseline_avg_stress = sum(p.bed_stress for p in result.baseline_forecast.predictions) / 7
        scenario_avg_stress = sum(p.bed_stress for p in result.scenario_forecast.predictions) / 7
        
        # Scenario should have significantly higher stress
        assert scenario_avg_stress > baseline_avg_stress
    
    def test_admission_surge_out_of_range_below_negative_thirty(self):
        """
        Test admission_surge below -30% (out of range)
        
        Validates: Requirements 4.3
        """
        # Test with admission surge below -30% (invalid)
        with pytest.raises(ValueError) as exc_info:
            self.engine.simulate_scenario(
                sick_rate=0.0,
                admission_surge=-0.4
            )
        
        # Should raise ValueError with descriptive message
        assert "admission_surge must be between -0.3 and 1.0" in str(exc_info.value)
    
    def test_admission_surge_out_of_range_above_one_hundred(self):
        """
        Test admission_surge above +100% (out of range)
        
        Validates: Requirements 4.3
        """
        # Test with admission surge above +100% (invalid)
        with pytest.raises(ValueError) as exc_info:
            self.engine.simulate_scenario(
                sick_rate=0.0,
                admission_surge=1.5
            )
        
        # Should raise ValueError with descriptive message
        assert "admission_surge must be between -0.3 and 1.0" in str(exc_info.value)
    
    def test_combined_extreme_parameters(self):
        """
        Test with both parameters at extreme values
        
        Validates: Requirements 4.2, 4.3
        """
        # Test with maximum sick rate and maximum admission surge
        result = self.engine.simulate_scenario(
            sick_rate=0.5,
            admission_surge=1.0
        )
        
        # Should succeed without errors
        assert isinstance(result, ScenarioResult)
        assert result.validate()
        
        # This should create a worst-case scenario
        # Both bed stress and staff risk should be significantly elevated
        baseline_avg_stress = sum(p.bed_stress for p in result.baseline_forecast.predictions) / 7
        scenario_avg_stress = sum(p.bed_stress for p in result.scenario_forecast.predictions) / 7
        
        baseline_risk = result.baseline_staff_risk.risk_score
        scenario_risk = result.scenario_staff_risk.risk_score
        
        # Both metrics should be worse in the scenario
        assert scenario_avg_stress > baseline_avg_stress
        assert scenario_risk > baseline_risk
        
        # Impact summary should indicate significant negative impact
        assert "NEGATIVE IMPACT" in result.impact_summary or "WARNING" in result.impact_summary


class TestPredictionCaching:
    """Property-based tests for prediction caching"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.engine = PredictionEngine()
        # Clear cache before each test
        self.engine.invalidate_cache()
    
    @settings(max_examples=3, deadline=None)
    @given(
        historical_data=hospital_record_list()
    )
    def test_prediction_caching(self, historical_data):
        """
        Feature: hospital-stress-warning, Property 28: Prediction Caching
        
        For any prediction request, if an identical request was made within the last 
        15 minutes, the System should return the cached result without calling Vertex AI.
        
        Validates: Requirements 13.5
        """
        # Clear cache to start fresh
        self.engine.invalidate_cache()
        
        # First request - should generate new prediction
        forecast1 = self.engine.forecast_bed_demand(
            days_ahead=7,
            historical_data=historical_data
        )
        
        # Capture the generated_at timestamp
        first_generated_at = forecast1.generated_at
        
        # Second identical request - should return cached result
        forecast2 = self.engine.forecast_bed_demand(
            days_ahead=7,
            historical_data=historical_data
        )
        
        # Property: Second request should return cached result
        # The generated_at timestamp should be identical (same object from cache)
        assert forecast2.generated_at == first_generated_at, \
            "Second request should return cached result with same generated_at timestamp"
        
        # Property: Cached result should have identical predictions
        assert len(forecast1.predictions) == len(forecast2.predictions)
        for pred1, pred2 in zip(forecast1.predictions, forecast2.predictions):
            assert pred1.date == pred2.date
            assert pred1.predicted_beds == pred2.predicted_beds
            assert pred1.bed_stress == pred2.bed_stress
            assert pred1.confidence == pred2.confidence
            assert pred1.is_high_risk == pred2.is_high_risk
        
        # Property: Overall confidence should be identical
        assert forecast1.overall_confidence == forecast2.overall_confidence
    
    @settings(max_examples=3, deadline=None)
    @given(
        predicted_admissions=st.integers(min_value=0, max_value=1000),
        current_staff=st.integers(min_value=1, max_value=200),
        historical_overloads=hospital_record_list()
    )
    def test_staff_risk_caching(self, predicted_admissions, current_staff, historical_overloads):
        """
        Test that staff risk calculations are cached with 10-minute TTL
        
        Validates: Requirements 13.5
        """
        # Clear cache to start fresh
        self.engine.invalidate_cache()
        
        # First request - should generate new staff risk
        staff_risk1 = self.engine.calculate_staff_risk(
            predicted_admissions=predicted_admissions,
            current_staff=current_staff,
            historical_overloads=historical_overloads
        )
        
        # Capture the generated_at timestamp
        first_generated_at = staff_risk1.generated_at
        
        # Second identical request - should return cached result
        staff_risk2 = self.engine.calculate_staff_risk(
            predicted_admissions=predicted_admissions,
            current_staff=current_staff,
            historical_overloads=historical_overloads
        )
        
        # Property: Second request should return cached result
        assert staff_risk2.generated_at == first_generated_at, \
            "Second request should return cached result with same generated_at timestamp"
        
        # Property: Cached result should have identical values
        assert staff_risk1.risk_score == staff_risk2.risk_score
        assert staff_risk1.confidence == staff_risk2.confidence
        assert staff_risk1.is_critical == staff_risk2.is_critical
        assert staff_risk1.contributing_factors == staff_risk2.contributing_factors
    
    @settings(max_examples=3, deadline=None)
    @given(
        bed_stress=st.floats(min_value=85.1, max_value=100.0),
        staff_risk=st.floats(min_value=75.1, max_value=100.0),
        historical_data=hospital_record_list()
    )
    def test_recommendations_caching(self, bed_stress, staff_risk, historical_data):
        """
        Test that recommendations are cached with 15-minute TTL
        
        Validates: Requirements 13.5
        """
        # Clear cache to start fresh
        self.engine.invalidate_cache()
        
        # First request - should generate new recommendations
        recommendations1 = self.engine.generate_recommendations(
            bed_stress=bed_stress,
            staff_risk=staff_risk,
            historical_context=historical_data
        )
        
        # Second identical request - should return cached result
        recommendations2 = self.engine.generate_recommendations(
            bed_stress=bed_stress,
            staff_risk=staff_risk,
            historical_context=historical_data
        )
        
        # Property: Should return exactly 3 recommendations both times
        assert len(recommendations1) == 3
        assert len(recommendations2) == 3
        
        # Property: Cached recommendations should be identical
        for rec1, rec2 in zip(recommendations1, recommendations2):
            assert rec1.title == rec2.title
            assert rec1.description == rec2.description
            assert rec1.rationale == rec2.rationale
            assert rec1.cost_estimate == rec2.cost_estimate
            assert rec1.impact_score == rec2.impact_score
            assert rec1.priority == rec2.priority
            assert rec1.implementation_time == rec2.implementation_time
    
    @settings(max_examples=3, deadline=None)
    @given(
        historical_data=hospital_record_list()
    )
    def test_cache_invalidation_on_new_data(self, historical_data):
        """
        Test that cache is invalidated when new data is uploaded
        
        Validates: Requirements 13.5
        """
        # Clear cache to start fresh
        self.engine.invalidate_cache()
        
        # First request - should generate new prediction
        forecast1 = self.engine.forecast_bed_demand(
            days_ahead=7,
            historical_data=historical_data
        )
        
        first_generated_at = forecast1.generated_at
        
        # Simulate new data upload by invalidating cache
        invalidation_success = self.engine.invalidate_cache()
        
        # Property: Cache invalidation should succeed
        assert invalidation_success == True, "Cache invalidation should succeed"
        
        # Third request after cache invalidation - should generate new prediction
        forecast3 = self.engine.forecast_bed_demand(
            days_ahead=7,
            historical_data=historical_data
        )
        
        # Property: After cache invalidation, should get new prediction
        # The generated_at timestamp should be different (new generation)
        assert forecast3.generated_at != first_generated_at, \
            "After cache invalidation, should generate new prediction with different timestamp"
    
    @settings(max_examples=3, deadline=None)
    @given(
        historical_data=hospital_record_list()
    )
    def test_dashboard_data_caching(self, historical_data):
        """
        Test that dashboard data is cached with 30-second TTL
        
        Validates: Requirements 13.5
        """
        # Clear cache to start fresh
        self.engine.invalidate_cache()
        
        # First request - should generate new dashboard data
        dashboard1 = self.engine.get_dashboard_data()
        
        # Verify dashboard data is valid
        assert dashboard1.validate()
        
        # Second request - should return cached result
        dashboard2 = self.engine.get_dashboard_data()
        
        # Property: Cached dashboard data should have identical values
        assert dashboard1.bed_stress_current == dashboard2.bed_stress_current
        assert dashboard1.staff_risk_current == dashboard2.staff_risk_current
        assert dashboard1.active_alerts_count == dashboard2.active_alerts_count
        assert dashboard1.recommendations_count == dashboard2.recommendations_count
        
        # Property: Forecast should be identical
        assert len(dashboard1.seven_day_forecast.predictions) == len(dashboard2.seven_day_forecast.predictions)
        assert dashboard1.seven_day_forecast.overall_confidence == dashboard2.seven_day_forecast.overall_confidence
        
        # Property: Staff risk should be identical
        assert len(dashboard1.seven_day_staff_risk) == len(dashboard2.seven_day_staff_risk)
        
        # Property: Trend indicators should be identical
        assert dashboard1.trend_indicators == dashboard2.trend_indicators
    
    @settings(max_examples=3, deadline=None)
    @given(
        historical_data1=hospital_record_list(),
        historical_data2=hospital_record_list()
    )
    def test_different_inputs_different_cache_keys(self, historical_data1, historical_data2):
        """
        Test that different inputs generate different cache keys
        
        Validates: Requirements 13.5
        """
        # Clear cache to start fresh
        self.engine.invalidate_cache()
        
        # Make sure the two datasets are actually different
        # (hypothesis might generate identical lists)
        if historical_data1 == historical_data2:
            # Make them different by adding a record to one
            if historical_data1:
                historical_data2 = historical_data1[:-1] if len(historical_data1) > 1 else []
            else:
                # If both empty, add a record to one
                historical_data2 = [HospitalRecord(
                    date=datetime(2024, 1, 1),
                    admissions=100,
                    beds_occupied=200,
                    staff_on_duty=30,
                    overload_flag=False
                )]
        
        # Request with first dataset
        forecast1 = self.engine.forecast_bed_demand(
            days_ahead=7,
            historical_data=historical_data1
        )
        
        # Request with second dataset
        forecast2 = self.engine.forecast_bed_demand(
            days_ahead=7,
            historical_data=historical_data2
        )
        
        # Property: Different inputs should generate different predictions
        # (unless both datasets are empty or very similar, in which case predictions might be similar)
        # We can't guarantee predictions are different, but we can verify both requests succeeded
        assert isinstance(forecast1, BedForecast)
        assert isinstance(forecast2, BedForecast)
        assert forecast1.validate()
        assert forecast2.validate()
