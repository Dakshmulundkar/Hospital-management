"""Alert Service for Hospital Stress Early Warning System"""
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
import time
import logging
from datetime import datetime

from app.models import AlertData, Recommendation, DailyPrediction

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class AlertThresholds:
    """Configuration for alert thresholds"""
    bed_stress_threshold: float = 85.0
    staff_risk_threshold: float = 75.0


@dataclass
class AlertTrigger:
    """Represents a triggered alert"""
    alert_type: str  # "bed_stress" or "staff_risk"
    risk_score: float
    threshold: float
    triggered_at: datetime


@dataclass
class EmailResult:
    """Result of email delivery attempt"""
    success: bool
    message: str
    attempts: int


@dataclass
class SlackResult:
    """Result of Slack notification attempt"""
    success: bool
    message: str
    attempts: int


class AlertService:
    """Service for monitoring thresholds and sending notifications"""
    
    def __init__(
        self,
        email_api_key: Optional[str] = None,
        slack_webhook_url: Optional[str] = None,
        max_retries: int = 3
    ):
        """
        Initialize AlertService
        
        Args:
            email_api_key: API key for email service (e.g., SendGrid)
            slack_webhook_url: Webhook URL for Slack notifications
            max_retries: Maximum number of retry attempts for failed deliveries
        """
        self.email_api_key = email_api_key
        self.slack_webhook_url = slack_webhook_url
        self.max_retries = max_retries
        
    def check_thresholds(
        self,
        bed_stress: float,
        staff_risk: float,
        thresholds: AlertThresholds
    ) -> List[AlertTrigger]:
        """
        Checks if any thresholds are exceeded
        
        Args:
            bed_stress: Current bed stress level (0-100)
            staff_risk: Current staff risk level (0-100)
            thresholds: Alert threshold configuration
            
        Returns:
            List of triggered alerts
        """
        triggers = []
        current_time = datetime.now()
        
        # Check bed stress threshold
        if bed_stress > thresholds.bed_stress_threshold:
            triggers.append(AlertTrigger(
                alert_type="bed_stress",
                risk_score=bed_stress,
                threshold=thresholds.bed_stress_threshold,
                triggered_at=current_time
            ))
            logger.info(f"Bed stress alert triggered: {bed_stress} > {thresholds.bed_stress_threshold}")
        
        # Check staff risk threshold
        if staff_risk > thresholds.staff_risk_threshold:
            triggers.append(AlertTrigger(
                alert_type="staff_risk",
                risk_score=staff_risk,
                threshold=thresholds.staff_risk_threshold,
                triggered_at=current_time
            ))
            logger.info(f"Staff risk alert triggered: {staff_risk} > {thresholds.staff_risk_threshold}")
        
        return triggers
    
    def format_alert_message(
        self,
        alert_type: str,
        risk_score: float,
        recommendations: List[Recommendation]
    ) -> str:
        """
        Formats alert message with recommendations
        
        Args:
            alert_type: Type of alert ("bed_stress" or "staff_risk")
            risk_score: Current risk score
            recommendations: List of recommendations
            
        Returns:
            Formatted message string
        """
        # Determine alert title based on type
        if alert_type == "bed_stress":
            title = "Hospital Bed Capacity Alert"
            metric_name = "Bed Stress Level"
        else:
            title = "Staff Overload Risk Alert"
            metric_name = "Staff Risk Score"
        
        # Build message
        message = f"""
{title}
{'=' * len(title)}

ALERT: {metric_name} has exceeded the configured threshold.

Current {metric_name}: {risk_score:.1f}

RECOMMENDED ACTIONS:
"""
        
        # Add top 3 recommendations
        for i, rec in enumerate(recommendations[:3], 1):
            message += f"""
{i}. {rec.title}
   Priority: {rec.priority}
   Description: {rec.description}
   Cost Estimate: ${rec.cost_estimate:,.2f}
   Impact Score: {rec.impact_score:.1f}/100
   Implementation Time: {rec.implementation_time}
   
"""
        
        message += """
Please review these recommendations and take appropriate action.

---
Hospital Stress Early Warning System
"""
        
        return message
    
    def _apply_hospital_letterhead(self, message: str) -> str:
        """
        Applies hospital letterhead template to message
        
        Args:
            message: Plain text message
            
        Returns:
            Message with hospital letterhead template
        """
        letterhead = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║           HOSPITAL STRESS EARLY WARNING SYSTEM               ║
║                                                              ║
║                    CRITICAL ALERT NOTICE                     ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

"""
        
        footer = """

╔══════════════════════════════════════════════════════════════╗
║  This is an automated alert from the Hospital Stress         ║
║  Early Warning System. For questions or support, please      ║
║  contact your system administrator.                          ║
╚══════════════════════════════════════════════════════════════╝
"""
        
        return letterhead + message + footer
    
    def send_email_alert(
        self,
        recipients: List[str],
        alert_data: AlertData,
        template: str = "hospital_letterhead"
    ) -> EmailResult:
        """
        Sends formatted email notification with retry logic
        
        Args:
            recipients: List of email addresses
            alert_data: Alert data including risk scores and recommendations
            template: Template name (default: "hospital_letterhead")
            
        Returns:
            EmailResult with delivery status
        """
        if not self.email_api_key:
            logger.warning("Email API key not configured, skipping email alert")
            return EmailResult(
                success=False,
                message="Email API key not configured",
                attempts=0
            )
        
        if not recipients:
            logger.warning("No recipients provided for email alert")
            return EmailResult(
                success=False,
                message="No recipients provided",
                attempts=0
            )
        
        # Format the alert message
        message = self.format_alert_message(
            alert_data.alert_type,
            alert_data.risk_score,
            alert_data.recommendations
        )
        
        # Apply template
        if template == "hospital_letterhead":
            message = self._apply_hospital_letterhead(message)
        
        # Retry logic
        for attempt in range(1, self.max_retries + 1):
            try:
                # Simulate email sending (in production, use SendGrid or similar)
                logger.info(f"Attempt {attempt}: Sending email to {len(recipients)} recipients")
                
                # In production, this would be:
                # import sendgrid
                # sg = sendgrid.SendGridAPIClient(api_key=self.email_api_key)
                # response = sg.send(...)
                
                # For now, simulate success
                success = self._simulate_email_send(recipients, message, attempt)
                
                if success:
                    logger.info(f"Email alert sent successfully on attempt {attempt}")
                    return EmailResult(
                        success=True,
                        message=f"Email sent to {len(recipients)} recipients",
                        attempts=attempt
                    )
                else:
                    logger.warning(f"Email delivery failed on attempt {attempt}")
                    if attempt < self.max_retries:
                        time.sleep(1)  # Wait 1 second before retry
                    
            except Exception as e:
                logger.error(f"Email delivery error on attempt {attempt}: {str(e)}")
                if attempt < self.max_retries:
                    time.sleep(1)  # Wait 1 second before retry
        
        # All retries failed
        return EmailResult(
            success=False,
            message=f"Email delivery failed after {self.max_retries} attempts",
            attempts=self.max_retries
        )
    
    def send_slack_alert(
        self,
        webhook_url: str,
        alert_data: AlertData
    ) -> SlackResult:
        """
        Sends Slack notification via webhook with retry logic
        
        Args:
            webhook_url: Slack webhook URL
            alert_data: Alert data including risk scores and recommendations
            
        Returns:
            SlackResult with delivery status
        """
        if not webhook_url:
            logger.warning("Slack webhook URL not provided, skipping Slack alert")
            return SlackResult(
                success=False,
                message="Slack webhook URL not provided",
                attempts=0
            )
        
        # Format message for Slack
        message = self.format_alert_message(
            alert_data.alert_type,
            alert_data.risk_score,
            alert_data.recommendations
        )
        
        # Build Slack payload
        payload = {
            "text": f"🚨 Hospital Alert: {alert_data.alert_type.replace('_', ' ').title()}",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"🚨 {alert_data.alert_type.replace('_', ' ').title()} Alert"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Risk Score:* {alert_data.risk_score:.1f}\n*Threshold:* {alert_data.threshold:.1f}"
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Recommended Actions:*"
                    }
                }
            ]
        }
        
        # Add recommendations
        for i, rec in enumerate(alert_data.recommendations[:3], 1):
            payload["blocks"].append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{i}. {rec.title}*\n{rec.description}\n_Cost: ${rec.cost_estimate:,.2f} | Impact: {rec.impact_score:.1f}/100_"
                }
            })
        
        # Retry logic
        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(f"Attempt {attempt}: Sending Slack notification")
                
                # In production, this would be:
                # import requests
                # response = requests.post(webhook_url, json=payload)
                # response.raise_for_status()
                
                # For now, simulate success
                success = self._simulate_slack_send(webhook_url, payload, attempt)
                
                if success:
                    logger.info(f"Slack alert sent successfully on attempt {attempt}")
                    return SlackResult(
                        success=True,
                        message="Slack notification sent",
                        attempts=attempt
                    )
                else:
                    logger.warning(f"Slack delivery failed on attempt {attempt}")
                    if attempt < self.max_retries:
                        time.sleep(1)  # Wait 1 second before retry
                    
            except Exception as e:
                logger.error(f"Slack delivery error on attempt {attempt}: {str(e)}")
                if attempt < self.max_retries:
                    time.sleep(1)  # Wait 1 second before retry
        
        # All retries failed
        return SlackResult(
            success=False,
            message=f"Slack delivery failed after {self.max_retries} attempts",
            attempts=self.max_retries
        )
    
    def _simulate_email_send(self, recipients: List[str], message: str, attempt: int) -> bool:
        """
        Simulates email sending for testing purposes
        In production, this would be replaced with actual email service integration
        """
        # Simulate success on first attempt for valid recipients
        return len(recipients) > 0 and attempt == 1
    
    def _simulate_slack_send(self, webhook_url: str, payload: Dict[str, Any], attempt: int) -> bool:
        """
        Simulates Slack webhook sending for testing purposes
        In production, this would be replaced with actual HTTP request
        """
        # Simulate success on first attempt for valid webhook
        return webhook_url.startswith("http") and attempt == 1
