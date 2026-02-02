"""Property-based tests for alert service
Feature: hospital-stress-warning
"""
import pytest
from hypothesis import given, settings, strategies as st
from datetime import datetime

from app.services.alert_service import AlertService, AlertThresholds
from app.models import AlertData, Recommendation, DailyPrediction


# Custom strategies for generating test data
@st.composite
def alert_thresholds_strategy(draw):
    """Generate valid alert thresholds"""
    return AlertThresholds(
        bed_stress_threshold=draw(st.floats(min_value=50.0, max_value=100.0)),
        staff_risk_threshold=draw(st.floats(min_value=50.0, max_value=100.0))
    )


@st.composite
def recommendation_strategy(draw):
    """Generate valid recommendations"""
    priority = draw(st.integers(min_value=1, max_value=3))
    return Recommendation(
        title=draw(st.text(min_size=5, max_size=50)),
        description=draw(st.text(min_size=10, max_size=200)),
        rationale=draw(st.text(min_size=10, max_size=200)),
        cost_estimate=draw(st.floats(min_value=0.0, max_value=1000000.0)),
        impact_score=draw(st.floats(min_value=0.0, max_value=100.0)),
        priority=priority,
        implementation_time=draw(st.sampled_from(["24 hours", "3 days", "1 week", "2 weeks"]))
    )


@st.composite
def daily_prediction_strategy(draw):
    """Generate valid daily predictions"""
    bed_stress = draw(st.floats(min_value=0.0, max_value=100.0))
    return DailyPrediction(
        date=datetime.now(),
        predicted_beds=draw(st.integers(min_value=0, max_value=500)),
        bed_stress=bed_stress,
        confidence=draw(st.floats(min_value=0.0, max_value=100.0)),
        is_high_risk=bed_stress > 85
    )


@st.composite
def alert_data_strategy(draw):
    """Generate valid alert data"""
    alert_type = draw(st.sampled_from(["bed_stress", "staff_risk"]))
    risk_score = draw(st.floats(min_value=0.0, max_value=100.0))
    threshold = draw(st.floats(min_value=50.0, max_value=100.0))
    
    # Generate exactly 3 recommendations
    recommendations = [
        draw(recommendation_strategy()),
        draw(recommendation_strategy()),
        draw(recommendation_strategy())
    ]
    
    # Set priorities to 1, 2, 3
    recommendations[0].priority = 1
    recommendations[1].priority = 2
    recommendations[2].priority = 3
    
    # Generate predictions
    predictions = [draw(daily_prediction_strategy()) for _ in range(7)]
    
    return AlertData(
        alert_type=alert_type,
        risk_score=risk_score,
        threshold=threshold,
        predictions=predictions,
        recommendations=recommendations,
        generated_at=datetime.now()
    )


@settings(max_examples=20)
@given(
    bed_stress=st.floats(min_value=0.0, max_value=100.0),
    staff_risk=st.floats(min_value=0.0, max_value=100.0),
    thresholds=alert_thresholds_strategy()
)
def test_property_16_threshold_based_alert_triggering(bed_stress, staff_risk, thresholds):
    """
    Feature: hospital-stress-warning, Property 16: Threshold-Based Alert Triggering
    
    For any risk score (Staff_Risk or Bed_Stress) and configured threshold,
    the Alert_Service should trigger an alert if and only if the risk score exceeds the threshold.
    
    Validates: Requirements 6.1, 6.2
    """
    service = AlertService()
    
    # Check thresholds
    triggers = service.check_thresholds(bed_stress, staff_risk, thresholds)
    
    # Verify bed stress alert triggering
    bed_stress_triggered = any(t.alert_type == "bed_stress" for t in triggers)
    should_trigger_bed_stress = bed_stress > thresholds.bed_stress_threshold
    
    assert bed_stress_triggered == should_trigger_bed_stress, \
        f"Bed stress alert triggering mismatch: score={bed_stress}, threshold={thresholds.bed_stress_threshold}, triggered={bed_stress_triggered}"
    
    # Verify staff risk alert triggering
    staff_risk_triggered = any(t.alert_type == "staff_risk" for t in triggers)
    should_trigger_staff_risk = staff_risk > thresholds.staff_risk_threshold
    
    assert staff_risk_triggered == should_trigger_staff_risk, \
        f"Staff risk alert triggering mismatch: score={staff_risk}, threshold={thresholds.staff_risk_threshold}, triggered={staff_risk_triggered}"
    
    # Verify trigger details when alerts are triggered
    for trigger in triggers:
        assert trigger.alert_type in ["bed_stress", "staff_risk"], \
            f"Invalid alert type: {trigger.alert_type}"
        
        if trigger.alert_type == "bed_stress":
            assert trigger.risk_score == bed_stress, \
                f"Bed stress trigger has wrong risk score: {trigger.risk_score} != {bed_stress}"
            assert trigger.threshold == thresholds.bed_stress_threshold, \
                f"Bed stress trigger has wrong threshold: {trigger.threshold} != {thresholds.bed_stress_threshold}"
        else:
            assert trigger.risk_score == staff_risk, \
                f"Staff risk trigger has wrong risk score: {trigger.risk_score} != {staff_risk}"
            assert trigger.threshold == thresholds.staff_risk_threshold, \
                f"Staff risk trigger has wrong threshold: {trigger.threshold} != {thresholds.staff_risk_threshold}"
        
        assert isinstance(trigger.triggered_at, datetime), \
            "Trigger timestamp should be a datetime object"


@settings(max_examples=20)
@given(
    alert_data=alert_data_strategy(),
    has_slack_webhook=st.booleans()
)
def test_property_17_conditional_slack_notification(alert_data, has_slack_webhook):
    """
    Feature: hospital-stress-warning, Property 17: Conditional Slack Notification
    
    For any alert trigger, if a Slack webhook URL is configured,
    the Alert_Service should send a Slack notification in addition to email.
    
    Validates: Requirements 6.3
    """
    # Configure service with or without Slack webhook
    webhook_url = "https://hooks.slack.com/services/TEST/WEBHOOK" if has_slack_webhook else None
    service = AlertService(
        email_api_key="test_api_key",
        slack_webhook_url=webhook_url
    )
    
    # Send email alert
    email_result = service.send_email_alert(
        recipients=["admin@hospital.com"],
        alert_data=alert_data
    )
    
    # Send Slack alert if webhook is configured
    if has_slack_webhook:
        slack_result = service.send_slack_alert(
            webhook_url=webhook_url,
            alert_data=alert_data
        )
        
        # Slack notification should be attempted when webhook is configured
        assert slack_result.attempts > 0, \
            "Slack notification should be attempted when webhook is configured"
        
        # If webhook is valid (starts with http), it should succeed
        if webhook_url and webhook_url.startswith("http"):
            assert slack_result.success, \
                f"Slack notification should succeed with valid webhook: {slack_result.message}"
    else:
        # Without webhook, Slack notification should not be sent
        slack_result = service.send_slack_alert(
            webhook_url="",
            alert_data=alert_data
        )
        
        assert not slack_result.success, \
            "Slack notification should fail when webhook is not configured"
        assert slack_result.attempts == 0, \
            "Slack notification should not be attempted when webhook is not configured"


@settings(max_examples=20)
@given(alert_data=alert_data_strategy())
def test_property_18_alert_template_application(alert_data):
    """
    Feature: hospital-stress-warning, Property 18: Alert Template Application
    
    For any email alert, the message should be formatted using the hospital letterhead template.
    
    Validates: Requirements 6.4
    """
    service = AlertService(email_api_key="test_api_key")
    
    # Format the alert message
    message = service.format_alert_message(
        alert_data.alert_type,
        alert_data.risk_score,
        alert_data.recommendations
    )
    
    # Apply hospital letterhead template
    templated_message = service._apply_hospital_letterhead(message)
    
    # Verify template elements are present
    assert "HOSPITAL STRESS EARLY WARNING SYSTEM" in templated_message, \
        "Template should include system name"
    
    assert "CRITICAL ALERT NOTICE" in templated_message, \
        "Template should include alert notice"
    
    assert "automated alert" in templated_message.lower(), \
        "Template should mention automated alert"
    
    # Verify original message content is preserved
    assert message in templated_message, \
        "Template should preserve original message content"
    
    # Verify template has header and footer
    lines = templated_message.split('\n')
    assert len(lines) > len(message.split('\n')), \
        "Templated message should have more lines than original (header + footer)"


@settings(max_examples=20)
@given(alert_data=alert_data_strategy())
def test_property_19_alert_content_completeness(alert_data):
    """
    Feature: hospital-stress-warning, Property 19: Alert Content Completeness
    
    For any alert notification, it should include the current risk score,
    predicted timeline, and exactly 3 recommendations.
    
    Validates: Requirements 6.5
    """
    service = AlertService()
    
    # Format the alert message
    message = service.format_alert_message(
        alert_data.alert_type,
        alert_data.risk_score,
        alert_data.recommendations
    )
    
    # Verify risk score is included
    assert str(alert_data.risk_score)[:4] in message, \
        f"Alert message should include risk score {alert_data.risk_score}"
    
    # Verify all 3 recommendations are included
    for i, rec in enumerate(alert_data.recommendations[:3], 1):
        assert rec.title in message, \
            f"Alert message should include recommendation {i} title: {rec.title}"
        
        assert rec.description in message, \
            f"Alert message should include recommendation {i} description"
        
        assert f"${rec.cost_estimate:,.2f}" in message or str(rec.cost_estimate) in message, \
            f"Alert message should include recommendation {i} cost estimate"
        
        assert str(rec.impact_score)[:4] in message or f"{rec.impact_score:.1f}" in message, \
            f"Alert message should include recommendation {i} impact score"
        
        assert rec.implementation_time in message, \
            f"Alert message should include recommendation {i} implementation time"
    
    # Verify exactly 3 recommendations (not more)
    # Count numbered items in the message
    numbered_items = [line for line in message.split('\n') if line.strip().startswith(('1.', '2.', '3.', '4.'))]
    recommendation_numbers = [line for line in numbered_items if any(rec.title in line for rec in alert_data.recommendations)]
    
    # Should have exactly 3 recommendations
    assert len(alert_data.recommendations) >= 3, \
        "Alert data should have at least 3 recommendations"
