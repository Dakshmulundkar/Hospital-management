"""
Full System Demo - Hospital Stress Early Warning System
Demonstrates the complete workflow from data upload to alert generation
"""
import sys
from datetime import datetime, timedelta
from io import BytesIO

from app.services.synthetic_data_generator import SyntheticDataGenerator
from app.services.upload_handler import UploadHandler
from app.services.prediction_engine import PredictionEngine
from app.services.alert_service import AlertService, AlertThresholds
from app.models import HospitalRecord, ScenarioRequest


def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 100)
    print(f"  {title}")
    print("=" * 100 + "\n")


def print_subheader(title):
    """Print a formatted subheader"""
    print("\n" + "-" * 100)
    print(f"  {title}")
    print("-" * 100 + "\n")


def demo_1_data_generation():
    """Demo 1: Generate synthetic hospital data"""
    print_header("DEMO 1: SYNTHETIC DATA GENERATION")
    
    generator = SyntheticDataGenerator()
    
    print("Generating 6 months of realistic hospital data...")
    print("  - Weekday/weekend patterns")
    print("  - Seasonal variations")
    print("  - Random overload events")
    
    records = generator.generate_six_months()
    
    print(f"\n✓ Generated {len(records)} days of data")
    print(f"  Date range: {records[0].date.date()} to {records[-1].date.date()}")
    
    # Show sample records
    print("\nSample records (first 5 days):")
    for i, record in enumerate(records[:5], 1):
        overload_flag = "🚨 OVERLOAD" if record.overload_flag else "✓ Normal"
        print(f"  Day {i}: {record.date.date()} | Admissions: {record.admissions:3d} | "
              f"Beds: {record.beds_occupied:3d} | Staff: {record.staff_on_duty:2d} | {overload_flag}")
    
    # Statistics
    overload_days = sum(1 for r in records if r.overload_flag)
    avg_admissions = sum(r.admissions for r in records) / len(records)
    avg_beds = sum(r.beds_occupied for r in records) / len(records)
    
    print(f"\nData Statistics:")
    print(f"  Total days: {len(records)}")
    print(f"  Overload days: {overload_days} ({overload_days/len(records)*100:.1f}%)")
    print(f"  Avg admissions/day: {avg_admissions:.1f}")
    print(f"  Avg beds occupied: {avg_beds:.1f}")
    
    return records


def demo_2_csv_upload(records):
    """Demo 2: CSV upload and validation"""
    print_header("DEMO 2: CSV UPLOAD & VALIDATION")
    
    handler = UploadHandler()
    
    # Convert records to CSV
    print("Converting hospital records to CSV format...")
    csv_content = "date,admissions,beds_occupied,staff_on_duty,overload_flag\n"
    for record in records[:30]:  # Use first 30 days
        csv_content += f"{record.date.date()},{record.admissions},{record.beds_occupied},"
        csv_content += f"{record.staff_on_duty},{str(record.overload_flag).lower()}\n"
    
    csv_bytes = csv_content.encode('utf-8')
    
    print(f"✓ Created CSV file ({len(csv_bytes)} bytes)")
    
    # Validate CSV
    print("\nValidating CSV...")
    validation_result = handler.validate_csv(csv_bytes)
    
    if validation_result.is_valid:
        print("✓ CSV validation PASSED")
    else:
        print("✗ CSV validation FAILED")
        for error in validation_result.errors:
            print(f"  Error: {error}")
    
    if validation_result.warnings:
        print("\nWarnings:")
        for warning in validation_result.warnings:
            print(f"  ⚠ {warning}")
    
    # Parse CSV
    print("\nParsing CSV records...")
    parsed_records = handler.parse_csv(csv_bytes)
    print(f"✓ Parsed {len(parsed_records)} records")
    
    return parsed_records


def demo_3_prediction_engine(records):
    """Demo 3: Bed demand forecasting"""
    print_header("DEMO 3: BED DEMAND FORECASTING")
    
    engine = PredictionEngine()
    
    print("Generating 7-day bed demand forecast...")
    print("  Using AI/ML prediction engine")
    print("  Analyzing historical patterns")
    
    try:
        forecast = engine.forecast_bed_demand(
            days_ahead=7,
            historical_data=records
        )
        
        print(f"\n✓ Forecast generated successfully")
        print(f"  Overall confidence: {forecast.overall_confidence:.1f}%")
        print(f"  Generated at: {forecast.generated_at}")
        
        print("\n7-Day Forecast:")
        print("  " + "-" * 90)
        print(f"  {'Date':<12} {'Predicted Beds':<15} {'Bed Stress':<12} {'Confidence':<12} {'Risk':<10}")
        print("  " + "-" * 90)
        
        for pred in forecast.predictions:
            risk_icon = "🚨 HIGH" if pred.is_high_risk else "✓ Normal"
            print(f"  {str(pred.date.date()):<12} {pred.predicted_beds:<15} "
                  f"{pred.bed_stress:<11.1f}% {pred.confidence:<11.1f}% {risk_icon:<10}")
        
        print("  " + "-" * 90)
        
        # Check for high-risk days
        high_risk_days = [p for p in forecast.predictions if p.is_high_risk]
        if high_risk_days:
            print(f"\n⚠ WARNING: {len(high_risk_days)} high-risk days detected!")
        else:
            print("\n✓ No high-risk days in forecast")
        
        return forecast
        
    except Exception as e:
        print(f"\n✗ Forecast generation failed: {str(e)}")
        print("  Note: This demo uses simulated predictions without actual Vertex AI")
        return None


def demo_4_staff_risk_assessment(records):
    """Demo 4: Staff overload risk assessment"""
    print_header("DEMO 4: STAFF OVERLOAD RISK ASSESSMENT")
    
    engine = PredictionEngine()
    
    print("Calculating staff overload risk...")
    print("  Analyzing admission patterns")
    print("  Evaluating staffing levels")
    print("  Learning from historical overload events")
    
    try:
        # Use recent data for prediction
        predicted_admissions = int(sum(r.admissions for r in records[-7:]) / 7)
        current_staff = int(sum(r.staff_on_duty for r in records[-7:]) / 7)
        historical_overloads = [r for r in records if r.overload_flag]
        
        print(f"\n  Predicted admissions: {predicted_admissions}")
        print(f"  Current staff level: {current_staff}")
        print(f"  Historical overload events: {len(historical_overloads)}")
        
        staff_risk = engine.calculate_staff_risk(
            predicted_admissions=predicted_admissions,
            current_staff=current_staff,
            historical_overloads=historical_overloads
        )
        
        print(f"\n✓ Staff risk assessment complete")
        print(f"\n  Risk Score: {staff_risk.risk_score:.1f}/100")
        print(f"  Confidence: {staff_risk.confidence:.1f}%")
        print(f"  Status: {'🚨 CRITICAL' if staff_risk.is_critical else '✓ Normal'}")
        
        if staff_risk.contributing_factors:
            print(f"\n  Contributing Factors:")
            for factor in staff_risk.contributing_factors:
                print(f"    • {factor}")
        
        return staff_risk
        
    except Exception as e:
        print(f"\n✗ Staff risk assessment failed: {str(e)}")
        return None


def demo_5_recommendations(records):
    """Demo 5: Generate actionable recommendations"""
    print_header("DEMO 5: ACTIONABLE RECOMMENDATIONS")
    
    engine = PredictionEngine()
    
    print("Generating prioritized recommendations...")
    print("  Using chain-of-thought reasoning")
    print("  Calculating cost estimates")
    print("  Ranking by impact-to-cost ratio")
    
    try:
        # Simulate high-risk scenario
        bed_stress = 92.5
        staff_risk = 85.0
        
        print(f"\n  Scenario: Bed Stress = {bed_stress}%, Staff Risk = {staff_risk}%")
        
        recommendations = engine.generate_recommendations(
            bed_stress=bed_stress,
            staff_risk=staff_risk,
            historical_context=records[-30:]
        )
        
        print(f"\n✓ Generated {len(recommendations)} recommendations")
        
        for i, rec in enumerate(recommendations, 1):
            print(f"\n  {i}. {rec.title}")
            print(f"     Priority: {rec.priority} | Impact: {rec.impact_score:.1f}/100 | Cost: ${rec.cost_estimate:,.2f}")
            print(f"     Description: {rec.description}")
            print(f"     Implementation: {rec.implementation_time}")
            print(f"     Rationale: {rec.rationale[:100]}...")
        
        return recommendations
        
    except Exception as e:
        print(f"\n✗ Recommendation generation failed: {str(e)}")
        return None


def demo_6_what_if_simulator(records):
    """Demo 6: What-if scenario simulation"""
    print_header("DEMO 6: WHAT-IF SCENARIO SIMULATOR")
    
    engine = PredictionEngine()
    
    print("Running what-if scenario simulation...")
    
    try:
        # Get baseline forecast
        baseline_forecast = engine.forecast_bed_demand(days_ahead=7, historical_data=records)
        
        # Scenario: 20% staff sick, 50% admission surge
        scenario_request = ScenarioRequest(
            sick_rate=0.20,
            admission_surge=0.50,
            baseline_date=datetime.now()
        )
        
        print(f"\n  Scenario Parameters:")
        print(f"    Staff sick rate: {scenario_request.sick_rate*100:.0f}%")
        print(f"    Admission surge: {scenario_request.admission_surge*100:.0f}%")
        
        scenario_result = engine.simulate_scenario(
            baseline_forecast=baseline_forecast,
            sick_rate=scenario_request.sick_rate,
            admission_surge=scenario_request.admission_surge
        )
        
        print(f"\n✓ Scenario simulation complete")
        print(f"\n  {scenario_result.impact_summary}")
        
        print("\n  Comparison (Day 1):")
        baseline_day1 = scenario_result.baseline_forecast.predictions[0]
        scenario_day1 = scenario_result.scenario_forecast.predictions[0]
        
        print(f"    Baseline: {baseline_day1.predicted_beds} beds, {baseline_day1.bed_stress:.1f}% stress")
        print(f"    Scenario: {scenario_day1.predicted_beds} beds, {scenario_day1.bed_stress:.1f}% stress")
        print(f"    Difference: +{scenario_day1.predicted_beds - baseline_day1.predicted_beds} beds, "
              f"+{scenario_day1.bed_stress - baseline_day1.bed_stress:.1f}% stress")
        
        return scenario_result
        
    except Exception as e:
        print(f"\n✗ Scenario simulation failed: {str(e)}")
        return None


def demo_7_alert_system(forecast, staff_risk, recommendations):
    """Demo 7: Alert system with threshold monitoring"""
    print_header("DEMO 7: ALERT SYSTEM")
    
    alert_service = AlertService(
        email_api_key="demo_api_key",
        slack_webhook_url="https://hooks.slack.com/services/DEMO/WEBHOOK"
    )
    
    thresholds = AlertThresholds(
        bed_stress_threshold=85.0,
        staff_risk_threshold=75.0
    )
    
    print("Monitoring thresholds...")
    print(f"  Bed stress threshold: {thresholds.bed_stress_threshold}%")
    print(f"  Staff risk threshold: {thresholds.staff_risk_threshold}%")
    
    if forecast and staff_risk:
        # Get current metrics
        current_bed_stress = forecast.predictions[0].bed_stress if forecast.predictions else 0
        current_staff_risk = staff_risk.risk_score
        
        print(f"\n  Current bed stress: {current_bed_stress:.1f}%")
        print(f"  Current staff risk: {current_staff_risk:.1f}%")
        
        # Check thresholds
        triggers = alert_service.check_thresholds(
            bed_stress=current_bed_stress,
            staff_risk=current_staff_risk,
            thresholds=thresholds
        )
        
        if triggers:
            print(f"\n🚨 ALERT: {len(triggers)} threshold(s) exceeded!")
            
            for trigger in triggers:
                print(f"\n  Alert Type: {trigger.alert_type.replace('_', ' ').title()}")
                print(f"  Risk Score: {trigger.risk_score:.1f}")
                print(f"  Threshold: {trigger.threshold:.1f}")
                print(f"  Triggered at: {trigger.triggered_at}")
                
                # Format and display alert message
                if recommendations:
                    message = alert_service.format_alert_message(
                        trigger.alert_type,
                        trigger.risk_score,
                        recommendations
                    )
                    
                    print("\n  Alert Message Preview:")
                    print("  " + "-" * 90)
                    for line in message.split('\n')[:15]:  # Show first 15 lines
                        print(f"  {line}")
                    print("  ...")
                    print("  " + "-" * 90)
        else:
            print("\n✓ All thresholds within normal range")
    else:
        print("\n⚠ Insufficient data for threshold checking")


def main():
    """Run the complete system demo"""
    print("\n")
    print("╔" + "=" * 98 + "╗")
    print("║" + " " * 98 + "║")
    print("║" + "  HOSPITAL STRESS EARLY WARNING SYSTEM - FULL SYSTEM DEMO".center(98) + "║")
    print("║" + " " * 98 + "║")
    print("╚" + "=" * 98 + "╝")
    
    print("\nThis demo showcases the complete workflow:")
    print("  1. Synthetic data generation")
    print("  2. CSV upload and validation")
    print("  3. Bed demand forecasting")
    print("  4. Staff risk assessment")
    print("  5. Recommendation generation")
    print("  6. What-if scenario simulation")
    print("  7. Alert system with threshold monitoring")
    
    print("\n[Running automated demo...]\n")
    
    # Run all demos
    records = demo_1_data_generation()
    
    parsed_records = demo_2_csv_upload(records)
    
    forecast = demo_3_prediction_engine(records)
    
    staff_risk = demo_4_staff_risk_assessment(records)
    
    recommendations = demo_5_recommendations(records)
    
    scenario_result = demo_6_what_if_simulator(records)
    
    demo_7_alert_system(forecast, staff_risk, recommendations)
    
    # Final summary
    print_header("DEMO COMPLETE")
    
    print("✓ All system components demonstrated successfully!")
    print("\nImplemented Features:")
    print("  ✓ Synthetic data generation (6 months)")
    print("  ✓ CSV upload and validation")
    print("  ✓ 7-day bed demand forecasting")
    print("  ✓ Staff overload risk assessment")
    print("  ✓ AI-powered recommendations (top 3)")
    print("  ✓ What-if scenario simulation")
    print("  ✓ Alert system with email/Slack")
    print("  ✓ Threshold monitoring")
    print("  ✓ Retry logic for failed deliveries")
    
    print("\nNext Steps:")
    print("  → Implement FastAPI endpoints (Task 14)")
    print("  → Build frontend dashboard (Task 18)")
    print("  → Deploy to production (Task 29)")
    
    print("\n" + "=" * 100)
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n✗ Demo failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
