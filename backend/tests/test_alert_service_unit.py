"""Unit tests for alert service
Feature: hospital-stress-warning
"""
import pytest
from datetime import datetime
from unittest.mock import Mock, patch

from app.services.alert_service import AlertService, AlertThresholds
from app.models import AlertData, Recommendation, DailyPrediction


@pytest.fixture
def sample_alert_data():
    """Create sample alert data for testing"""
    recommendations = [
        Recommendation(
            title="Increase staffing",
            description="Add 5 additional nurses to the night shift",
            rationale="High admission rate predicted",
            cost_estimate=5000.0,
            impact_score=85.0,
            priority=1,
            implementation_time="24 hours"
        ),
        Recommendation(
            title="Prepare overflow beds",
            description="Set up 10 overflow beds in the auxiliary wing",
            rationale="Bed capacity approaching limit",
            cost_estimate=3000.0,
            impact_score=75.0,
            priority=2,
            implementation_time="12 hours"
        ),
        Recommendation(
            title="Contact on-call staff",
            description="Alert on-call staff to be ready for deployment",
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
            is_high_risk=False
        )
        for i in range(1, 8)
    ]
    
    return AlertData(
        alert_type="bed_stress",
        risk_score=87.5,
        threshold=85.0,
        predictions=predictions,
        recommendations=recommendations,
        generated_at=datetime.now()
    )


def test_email_delivery_retry_on_failure(sample_alert_data):
    """
    Test email delivery failures and retries
    Validates: Requirements 6.1, 6.2
    """
    # Create service with custom retry logic
    service = AlertService(email_api_key="test_key", max_retries=3)
    
    # Mock the simulate method to fail first 2 attempts, succeed on 3rd
    call_count = 0
    def mock_email_send(recipients, message, attempt):
        nonlocal call_count
        call_count += 1
        return attempt == 3  # Succeed on 3rd attempt
    
    service._simulate_email_send = mock_email_send
    
    # Send email alert
    result = service.send_email_alert(
        recipients=["admin@hospital.com"],
        alert_data=sample_alert_data
    )
    
    # Should succeed after retries
    assert result.success, "Email should succeed after retries"
    assert result.attempts == 3, f"Should have made 3 attempts, made {result.attempts}"
    assert call_count == 3, f"Should have called send 3 times, called {call_count}"


def test_email_delivery_all_retries_fail(sample_alert_data):
    """
    Test email delivery when all retries fail
    Validates: Requirements 6.1, 6.2
    """
    # Create service with custom retry logic
    service = AlertService(email_api_key="test_key", max_retries=3)
    
    # Mock the simulate method to always fail
    call_count = 0
    def mock_email_send(recipients, message, attempt):
        nonlocal call_count
        call_count += 1
        return False  # Always fail
    
    service._simulate_email_send = mock_email_send
    
    # Send email alert
    result = service.send_email_alert(
        recipients=["admin@hospital.com"],
        alert_data=sample_alert_data
    )
    
    # Should fail after all retries
    assert not result.success, "Email should fail after all retries"
    assert result.attempts == 3, f"Should have made 3 attempts, made {result.attempts}"
    assert call_count == 3, f"Should have called send 3 times, called {call_count}"
    assert "failed after 3 attempts" in result.message.lower()


def test_email_delivery_no_api_key(sample_alert_data):
    """
    Test email delivery when API key is not configured
    Validates: Requirements 6.1
    """
    # Create service without API key
    service = AlertService(email_api_key=None)
    
    # Send email alert
    result = service.send_email_alert(
        recipients=["admin@hospital.com"],
        alert_data=sample_alert_data
    )
    
    # Should fail immediately
    assert not result.success, "Email should fail without API key"
    assert result.attempts == 0, "Should not attempt to send without API key"
    assert "not configured" in result.message.lower()


def test_email_delivery_no_recipients(sample_alert_data):
    """
    Test email delivery when no recipients are provided
    Validates: Requirements 6.1
    """
    # Create service with API key
    service = AlertService(email_api_key="test_key")
    
    # Send email alert with no recipients
    result = service.send_email_alert(
        recipients=[],
        alert_data=sample_alert_data
    )
    
    # Should fail immediately
    assert not result.success, "Email should fail without recipients"
    assert result.attempts == 0, "Should not attempt to send without recipients"
    assert "no recipients" in result.message.lower()


def test_slack_webhook_retry_on_failure(sample_alert_data):
    """
    Test Slack webhook failures and retries
    Validates: Requirements 6.3
    """
    # Create service
    service = AlertService(slack_webhook_url="https://hooks.slack.com/test", max_retries=3)
    
    # Mock the simulate method to fail first 2 attempts, succeed on 3rd
    call_count = 0
    def mock_slack_send(webhook_url, payload, attempt):
        nonlocal call_count
        call_count += 1
        return attempt == 3  # Succeed on 3rd attempt
    
    service._simulate_slack_send = mock_slack_send
    
    # Send Slack alert
    result = service.send_slack_alert(
        webhook_url="https://hooks.slack.com/test",
        alert_data=sample_alert_data
    )
    
    # Should succeed after retries
    assert result.success, "Slack should succeed after retries"
    assert result.attempts == 3, f"Should have made 3 attempts, made {result.attempts}"
    assert call_count == 3, f"Should have called send 3 times, called {call_count}"


def test_slack_webhook_all_retries_fail(sample_alert_data):
    """
    Test Slack webhook when all retries fail
    Validates: Requirements 6.3
    """
    # Create service
    service = AlertService(slack_webhook_url="https://hooks.slack.com/test", max_retries=3)
    
    # Mock the simulate method to always fail
    call_count = 0
    def mock_slack_send(webhook_url, payload, attempt):
        nonlocal call_count
        call_count += 1
        return False  # Always fail
    
    service._simulate_slack_send = mock_slack_send
    
    # Send Slack alert
    result = service.send_slack_alert(
        webhook_url="https://hooks.slack.com/test",
        alert_data=sample_alert_data
    )
    
    # Should fail after all retries
    assert not result.success, "Slack should fail after all retries"
    assert result.attempts == 3, f"Should have made 3 attempts, made {result.attempts}"
    assert call_count == 3, f"Should have called send 3 times, called {call_count}"
    assert "failed after 3 attempts" in result.message.lower()


def test_slack_webhook_no_url(sample_alert_data):
    """
    Test Slack webhook when URL is not provided
    Validates: Requirements 6.3
    """
    # Create service
    service = AlertService()
    
    # Send Slack alert without URL
    result = service.send_slack_alert(
        webhook_url="",
        alert_data=sample_alert_data
    )
    
    # Should fail immediately
    assert not result.success, "Slack should fail without webhook URL"
    assert result.attempts == 0, "Should not attempt to send without webhook URL"
    assert "not provided" in result.message.lower()


def test_slack_webhook_invalid_url(sample_alert_data):
    """
    Test Slack webhook with invalid URL format
    Validates: Requirements 6.3
    """
    # Create service
    service = AlertService()
    
    # Send Slack alert with invalid URL
    result = service.send_slack_alert(
        webhook_url="not-a-valid-url",
        alert_data=sample_alert_data
    )
    
    # Should fail (simulate method checks for http prefix)
    assert not result.success, "Slack should fail with invalid URL"


def test_alert_message_formatting(sample_alert_data):
    """
    Test that alert messages are properly formatted
    Validates: Requirements 6.4, 6.5
    """
    service = AlertService()
    
    # Format message
    message = service.format_alert_message(
        sample_alert_data.alert_type,
        sample_alert_data.risk_score,
        sample_alert_data.recommendations
    )
    
    # Verify message contains key elements
    assert "Hospital Bed Capacity Alert" in message
    assert "87.5" in message or "87" in message  # Risk score
    assert "Increase staffing" in message  # First recommendation
    assert "Prepare overflow beds" in message  # Second recommendation
    assert "Contact on-call staff" in message  # Third recommendation
    
    # Verify all recommendations have required fields
    for rec in sample_alert_data.recommendations:
        assert rec.title in message
        assert rec.description in message
        assert rec.implementation_time in message


def test_hospital_letterhead_template():
    """
    Test that hospital letterhead template is applied correctly
    Validates: Requirements 6.4
    """
    service = AlertService()
    
    # Create a simple message
    simple_message = "This is a test alert message."
    
    # Apply letterhead
    templated = service._apply_hospital_letterhead(simple_message)
    
    # Verify template elements
    assert "HOSPITAL STRESS EARLY WARNING SYSTEM" in templated
    assert "CRITICAL ALERT NOTICE" in templated
    assert simple_message in templated
    assert "automated alert" in templated.lower()
    
    # Verify message is longer than original (has header and footer)
    assert len(templated) > len(simple_message)


def test_threshold_checking_both_exceeded():
    """
    Test threshold checking when both thresholds are exceeded
    Validates: Requirements 6.1, 6.2
    """
    service = AlertService()
    thresholds = AlertThresholds(bed_stress_threshold=80.0, staff_risk_threshold=70.0)
    
    # Both exceed thresholds
    triggers = service.check_thresholds(
        bed_stress=85.0,
        staff_risk=75.0,
        thresholds=thresholds
    )
    
    # Should have 2 triggers
    assert len(triggers) == 2
    
    # Verify both types are present
    alert_types = [t.alert_type for t in triggers]
    assert "bed_stress" in alert_types
    assert "staff_risk" in alert_types


def test_threshold_checking_none_exceeded():
    """
    Test threshold checking when no thresholds are exceeded
    Validates: Requirements 6.1, 6.2
    """
    service = AlertService()
    thresholds = AlertThresholds(bed_stress_threshold=80.0, staff_risk_threshold=70.0)
    
    # Neither exceeds thresholds
    triggers = service.check_thresholds(
        bed_stress=75.0,
        staff_risk=65.0,
        thresholds=thresholds
    )
    
    # Should have no triggers
    assert len(triggers) == 0


def test_threshold_checking_exact_threshold():
    """
    Test threshold checking when values equal thresholds (should not trigger)
    Validates: Requirements 6.1, 6.2
    """
    service = AlertService()
    thresholds = AlertThresholds(bed_stress_threshold=80.0, staff_risk_threshold=70.0)
    
    # Values equal thresholds (should not trigger - must exceed)
    triggers = service.check_thresholds(
        bed_stress=80.0,
        staff_risk=70.0,
        thresholds=thresholds
    )
    
    # Should have no triggers (must exceed, not equal)
    assert len(triggers) == 0
