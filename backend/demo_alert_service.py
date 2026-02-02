"""
Demo script for AlertService
Demonstrates the alert service functionality with sample data
"""
from datetime import datetime
from app.services.alert_service import AlertService, AlertThresholds
from app.models import AlertData, Recommendation, DailyPrediction


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def demo_threshold_checking():
    """Demonstrate threshold checking functionality"""
    print_section("DEMO 1: Threshold Checking")
    
    service = AlertService()
    thresholds = AlertThresholds(
        bed_stress_threshold=85.0,
        staff_risk_threshold=75.0
    )
    
    # Scenario 1: Both thresholds exceeded
    print("Scenario 1: Both thresholds exceeded")
    print(f"  Bed Stress: 92.5 (threshold: {thresholds.bed_stress_threshold})")
    print(f"  Staff Risk: 80.0 (threshold: {thresholds.staff_risk_threshold})")
    
    triggers = service.check_thresholds(92.5, 80.0, thresholds)
    print(f"\n  ✓ Triggered {len(triggers)} alerts:")
    for trigger in triggers:
        print(f"    - {trigger.alert_type}: {trigger.risk_score} > {trigger.threshold}")
    
    # Scenario 2: Only bed stress exceeded
    print("\n\nScenario 2: Only bed stress exceeded")
    print(f"  Bed Stress: 88.0 (threshold: {thresholds.bed_stress_threshold})")
    print(f"  Staff Risk: 65.0 (threshold: {thresholds.staff_risk_threshold})")
    
    triggers = service.check_thresholds(88.0, 65.0, thresholds)
    print(f"\n  ✓ Triggered {len(triggers)} alert(s):")
    for trigger in triggers:
        print(f"    - {trigger.alert_type}: {trigger.risk_score} > {trigger.threshold}")
    
    # Scenario 3: No thresholds exceeded
    print("\n\nScenario 3: No thresholds exceeded")
    print(f"  Bed Stress: 70.0 (threshold: {thresholds.bed_stress_threshold})")
    print(f"  Staff Risk: 60.0 (threshold: {thresholds.staff_risk_threshold})")
    
    triggers = service.check_thresholds(70.0, 60.0, thresholds)
    print(f"\n  ✓ Triggered {len(triggers)} alerts (all clear!)")


def demo_alert_message_formatting():
    """Demonstrate alert message formatting"""
    print_section("DEMO 2: Alert Message Formatting")
    
    service = AlertService()
    
    # Create sample recommendations
    recommendations = [
        Recommendation(
            title="Increase Staffing Immediately",
            description="Add 5 additional nurses to the night shift to handle predicted surge",
            rationale="Historical data shows similar patterns led to staff burnout",
            cost_estimate=5000.0,
            impact_score=92.0,
            priority=1,
            implementation_time="24 hours"
        ),
        Recommendation(
            title="Prepare Overflow Beds",
            description="Set up 10 overflow beds in the auxiliary wing",
            rationale="Bed capacity approaching 90% threshold",
            cost_estimate=3000.0,
            impact_score=85.0,
            priority=2,
            implementation_time="12 hours"
        ),
        Recommendation(
            title="Contact On-Call Staff",
            description="Alert on-call staff to be ready for immediate deployment",
            rationale="Potential staff shortage in next 48 hours",
            cost_estimate=500.0,
            impact_score=75.0,
            priority=3,
            implementation_time="2 hours"
        )
    ]
    
    # Format bed stress alert
    print("Bed Stress Alert Message:")
    print("-" * 80)
    message = service.format_alert_message("bed_stress", 92.5, recommendations)
    print(message)
    
    # Format staff risk alert
    print("\n\nStaff Risk Alert Message:")
    print("-" * 80)
    message = service.format_alert_message("staff_risk", 82.0, recommendations)
    print(message)


def demo_hospital_letterhead():
    """Demonstrate hospital letterhead template"""
    print_section("DEMO 3: Hospital Letterhead Template")
    
    service = AlertService()
    
    recommendations = [
        Recommendation(
            title="Emergency Staffing Protocol",
            description="Activate emergency staffing protocol",
            rationale="Critical staff shortage predicted",
            cost_estimate=10000.0,
            impact_score=95.0,
            priority=1,
            implementation_time="Immediate"
        ),
        Recommendation(
            title="Divert Non-Critical Admissions",
            description="Temporarily divert non-critical admissions to partner facilities",
            rationale="Bed capacity at 95%",
            cost_estimate=2000.0,
            impact_score=88.0,
            priority=2,
            implementation_time="6 hours"
        ),
        Recommendation(
            title="Cancel Elective Procedures",
            description="Cancel tomorrow's elective procedures to free up beds",
            rationale="Need to maintain emergency capacity",
            cost_estimate=15000.0,
            impact_score=80.0,
            priority=3,
            implementation_time="12 hours"
        )
    ]
    
    # Create message with letterhead
    message = service.format_alert_message("bed_stress", 96.5, recommendations)
    templated_message = service._apply_hospital_letterhead(message)
    
    print(templated_message)


def demo_email_alert_with_retry():
    """Demonstrate email alert with retry logic"""
    print_section("DEMO 4: Email Alert with Retry Logic")
    
    # Create sample alert data
    recommendations = [
        Recommendation(
            title="Increase Staffing",
            description="Add 5 nurses to night shift",
            rationale="High admission rate predicted",
            cost_estimate=5000.0,
            impact_score=85.0,
            priority=1,
            implementation_time="24 hours"
        ),
        Recommendation(
            title="Prepare Overflow Beds",
            description="Set up 10 overflow beds",
            rationale="Bed capacity approaching limit",
            cost_estimate=3000.0,
            impact_score=75.0,
            priority=2,
            implementation_time="12 hours"
        ),
        Recommendation(
            title="Contact On-Call Staff",
            description="Alert on-call staff",
            rationale="Potential staff shortage",
            cost_estimate=500.0,
            impact_score=60.0,
            priority=3,
            implementation_time="2 hours"
        )
    ]
    
    predictions = [
        DailyPrediction(
            date=datetime(2024, 1, i),
            predicted_beds=100 + i * 5,
            bed_stress=80.0 + i,
            confidence=90.0,
            is_high_risk=i > 5
        )
        for i in range(1, 8)
    ]
    
    alert_data = AlertData(
        alert_type="bed_stress",
        risk_score=87.5,
        threshold=85.0,
        predictions=predictions,
        recommendations=recommendations,
        generated_at=datetime.now()
    )
    
    # Scenario 1: Successful email delivery
    print("Scenario 1: Email delivery with API key configured")
    service = AlertService(email_api_key="demo_api_key_12345", max_retries=3)
    
    result = service.send_email_alert(
        recipients=["admin@hospital.com", "director@hospital.com"],
        alert_data=alert_data
    )
    
    print(f"  Status: {'✓ SUCCESS' if result.success else '✗ FAILED'}")
    print(f"  Message: {result.message}")
    print(f"  Attempts: {result.attempts}")
    
    # Scenario 2: No API key configured
    print("\n\nScenario 2: Email delivery without API key")
    service = AlertService(email_api_key=None)
    
    result = service.send_email_alert(
        recipients=["admin@hospital.com"],
        alert_data=alert_data
    )
    
    print(f"  Status: {'✓ SUCCESS' if result.success else '✗ FAILED'}")
    print(f"  Message: {result.message}")
    print(f"  Attempts: {result.attempts}")


def demo_slack_alert():
    """Demonstrate Slack alert functionality"""
    print_section("DEMO 5: Slack Alert Integration")
    
    # Create sample alert data
    recommendations = [
        Recommendation(
            title="Critical: Activate Emergency Protocol",
            description="Immediate action required - activate emergency staffing protocol",
            rationale="Staff risk at critical level",
            cost_estimate=10000.0,
            impact_score=95.0,
            priority=1,
            implementation_time="Immediate"
        ),
        Recommendation(
            title="Contact Emergency Staff",
            description="Call in emergency backup staff",
            rationale="Current staff insufficient for predicted load",
            cost_estimate=8000.0,
            impact_score=90.0,
            priority=2,
            implementation_time="2 hours"
        ),
        Recommendation(
            title="Prepare Crisis Management",
            description="Activate crisis management team",
            rationale="Multiple risk factors converging",
            cost_estimate=5000.0,
            impact_score=85.0,
            priority=3,
            implementation_time="4 hours"
        )
    ]
    
    predictions = [
        DailyPrediction(
            date=datetime(2024, 1, i),
            predicted_beds=120 + i * 8,
            bed_stress=85.0 + i * 2,
            confidence=88.0,
            is_high_risk=True
        )
        for i in range(1, 8)
    ]
    
    alert_data = AlertData(
        alert_type="staff_risk",
        risk_score=82.0,
        threshold=75.0,
        predictions=predictions,
        recommendations=recommendations,
        generated_at=datetime.now()
    )
    
    # Scenario 1: Slack webhook configured
    print("Scenario 1: Slack notification with webhook configured")
    service = AlertService(slack_webhook_url="https://hooks.slack.com/services/TEST/WEBHOOK")
    
    result = service.send_slack_alert(
        webhook_url="https://hooks.slack.com/services/TEST/WEBHOOK",
        alert_data=alert_data
    )
    
    print(f"  Status: {'✓ SUCCESS' if result.success else '✗ FAILED'}")
    print(f"  Message: {result.message}")
    print(f"  Attempts: {result.attempts}")
    
    # Scenario 2: No webhook configured
    print("\n\nScenario 2: Slack notification without webhook")
    service = AlertService()
    
    result = service.send_slack_alert(
        webhook_url="",
        alert_data=alert_data
    )
    
    print(f"  Status: {'✓ SUCCESS' if result.success else '✗ FAILED'}")
    print(f"  Message: {result.message}")
    print(f"  Attempts: {result.attempts}")


def main():
    """Run all demos"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "  HOSPITAL STRESS EARLY WARNING SYSTEM - ALERT SERVICE DEMO".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")
    
    demo_threshold_checking()
    demo_alert_message_formatting()
    demo_hospital_letterhead()
    demo_email_alert_with_retry()
    demo_slack_alert()
    
    print("\n" + "=" * 80)
    print("  DEMO COMPLETE")
    print("=" * 80 + "\n")
    print("The AlertService is ready for integration with the Hospital Stress Early Warning System!")
    print("\nKey Features Demonstrated:")
    print("  ✓ Threshold-based alert triggering")
    print("  ✓ Formatted alert messages with recommendations")
    print("  ✓ Hospital letterhead template application")
    print("  ✓ Email delivery with retry logic")
    print("  ✓ Slack webhook integration")
    print("  ✓ Comprehensive error handling")
    print()


if __name__ == "__main__":
    main()
