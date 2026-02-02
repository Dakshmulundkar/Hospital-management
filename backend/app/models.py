"""Data models for the Hospital Stress Early Warning System"""
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Optional


@dataclass
class HospitalRecord:
    date: datetime
    admissions: int
    beds_occupied: int
    staff_on_duty: int
    overload_flag: bool
    
    def validate(self) -> bool:
        """Validates data types and ranges"""
        if not isinstance(self.date, datetime):
            return False
        if not isinstance(self.admissions, int) or self.admissions < 0:
            return False
        if not isinstance(self.beds_occupied, int) or self.beds_occupied < 0:
            return False
        if not isinstance(self.staff_on_duty, int) or self.staff_on_duty < 0:
            return False
        if not isinstance(self.overload_flag, bool):
            return False
        return True


@dataclass
class DailyPrediction:
    date: datetime
    predicted_beds: int
    bed_stress: float  # 0-100
    confidence: float  # 0-100
    is_high_risk: bool  # True if bed_stress > 85
    
    def validate(self) -> bool:
        """Validates data types and ranges"""
        if not isinstance(self.date, datetime):
            return False
        if not isinstance(self.predicted_beds, int) or self.predicted_beds < 0:
            return False
        if not isinstance(self.bed_stress, (int, float)) or not (0 <= self.bed_stress <= 100):
            return False
        if not isinstance(self.confidence, (int, float)) or not (0 <= self.confidence <= 100):
            return False
        if not isinstance(self.is_high_risk, bool):
            return False
        # Validate is_high_risk flag consistency
        if self.bed_stress > 85 and not self.is_high_risk:
            return False
        if self.bed_stress <= 85 and self.is_high_risk:
            return False
        return True


@dataclass
class BedForecast:
    predictions: List[DailyPrediction]
    overall_confidence: float
    generated_at: datetime
    
    def validate(self) -> bool:
        """Validates data types and ranges"""
        if not isinstance(self.predictions, list):
            return False
        if len(self.predictions) != 7:
            return False
        if not all(isinstance(p, DailyPrediction) and p.validate() for p in self.predictions):
            return False
        if not isinstance(self.overall_confidence, (int, float)) or not (0 <= self.overall_confidence <= 100):
            return False
        if not isinstance(self.generated_at, datetime):
            return False
        return True


@dataclass
class StaffRiskScore:
    risk_score: float  # 0-100
    confidence: float  # 0-100
    is_critical: bool  # True if risk_score > 75
    contributing_factors: List[str]
    generated_at: datetime
    
    def validate(self) -> bool:
        """Validates data types and ranges"""
        if not isinstance(self.risk_score, (int, float)) or not (0 <= self.risk_score <= 100):
            return False
        if not isinstance(self.confidence, (int, float)) or not (0 <= self.confidence <= 100):
            return False
        if not isinstance(self.is_critical, bool):
            return False
        # Validate is_critical flag consistency
        if self.risk_score > 75 and not self.is_critical:
            return False
        if self.risk_score <= 75 and self.is_critical:
            return False
        if not isinstance(self.contributing_factors, list):
            return False
        if not all(isinstance(f, str) for f in self.contributing_factors):
            return False
        if not isinstance(self.generated_at, datetime):
            return False
        return True


@dataclass
class Recommendation:
    title: str
    description: str
    rationale: str  # Chain-of-thought explanation
    cost_estimate: float
    impact_score: float  # 0-100
    priority: int  # 1, 2, or 3
    implementation_time: str  # e.g., "24 hours", "3 days"
    
    def validate(self) -> bool:
        """Validates data types and ranges"""
        if not isinstance(self.title, str) or not self.title.strip():
            return False
        if not isinstance(self.description, str) or not self.description.strip():
            return False
        if not isinstance(self.rationale, str) or not self.rationale.strip():
            return False
        if not isinstance(self.cost_estimate, (int, float)) or self.cost_estimate < 0:
            return False
        if not isinstance(self.impact_score, (int, float)) or not (0 <= self.impact_score <= 100):
            return False
        if not isinstance(self.priority, int) or self.priority not in [1, 2, 3]:
            return False
        if not isinstance(self.implementation_time, str) or not self.implementation_time.strip():
            return False
        return True


@dataclass
class AlertData:
    alert_type: str  # "bed_stress" or "staff_risk"
    risk_score: float
    threshold: float
    predictions: List[DailyPrediction]
    recommendations: List[Recommendation]
    generated_at: datetime
    
    def validate(self) -> bool:
        """Validates data types and ranges"""
        if not isinstance(self.alert_type, str) or self.alert_type not in ["bed_stress", "staff_risk"]:
            return False
        if not isinstance(self.risk_score, (int, float)) or not (0 <= self.risk_score <= 100):
            return False
        if not isinstance(self.threshold, (int, float)) or not (50 <= self.threshold <= 100):
            return False
        if not isinstance(self.predictions, list):
            return False
        if not all(isinstance(p, DailyPrediction) and p.validate() for p in self.predictions):
            return False
        if not isinstance(self.recommendations, list) or len(self.recommendations) != 3:
            return False
        if not all(isinstance(r, Recommendation) and r.validate() for r in self.recommendations):
            return False
        if not isinstance(self.generated_at, datetime):
            return False
        return True


@dataclass
class ScenarioRequest:
    sick_rate: float  # 0.0 to 0.5
    admission_surge: float  # -0.3 to 1.0
    baseline_date: datetime
    
    def validate(self) -> bool:
        """Validates data types and ranges"""
        if not isinstance(self.sick_rate, (int, float)) or not (0.0 <= self.sick_rate <= 0.5):
            return False
        if not isinstance(self.admission_surge, (int, float)) or not (-0.3 <= self.admission_surge <= 1.0):
            return False
        if not isinstance(self.baseline_date, datetime):
            return False
        return True


@dataclass
class ScenarioResult:
    baseline_forecast: BedForecast
    scenario_forecast: BedForecast
    baseline_staff_risk: StaffRiskScore
    scenario_staff_risk: StaffRiskScore
    impact_summary: str
    
    def validate(self) -> bool:
        """Validates data types and ranges"""
        if not isinstance(self.baseline_forecast, BedForecast) or not self.baseline_forecast.validate():
            return False
        if not isinstance(self.scenario_forecast, BedForecast) or not self.scenario_forecast.validate():
            return False
        if not isinstance(self.baseline_staff_risk, StaffRiskScore) or not self.baseline_staff_risk.validate():
            return False
        if not isinstance(self.scenario_staff_risk, StaffRiskScore) or not self.scenario_staff_risk.validate():
            return False
        if not isinstance(self.impact_summary, str) or not self.impact_summary.strip():
            return False
        return True


@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    
    def validate(self) -> bool:
        """Validates data types"""
        if not isinstance(self.is_valid, bool):
            return False
        if not isinstance(self.errors, list):
            return False
        if not all(isinstance(e, str) for e in self.errors):
            return False
        if not isinstance(self.warnings, list):
            return False
        if not all(isinstance(w, str) for w in self.warnings):
            return False
        return True


@dataclass
class DashboardData:
    bed_stress_current: float
    staff_risk_current: float
    active_alerts_count: int
    recommendations_count: int
    seven_day_forecast: BedForecast
    seven_day_staff_risk: List[StaffRiskScore]
    trend_indicators: Dict[str, str]  # "up", "down", "stable"
    
    def validate(self) -> bool:
        """Validates data types and ranges"""
        if not isinstance(self.bed_stress_current, (int, float)) or not (0 <= self.bed_stress_current <= 100):
            return False
        if not isinstance(self.staff_risk_current, (int, float)) or not (0 <= self.staff_risk_current <= 100):
            return False
        if not isinstance(self.active_alerts_count, int) or self.active_alerts_count < 0:
            return False
        if not isinstance(self.recommendations_count, int) or self.recommendations_count < 0:
            return False
        if not isinstance(self.seven_day_forecast, BedForecast) or not self.seven_day_forecast.validate():
            return False
        if not isinstance(self.seven_day_staff_risk, list) or len(self.seven_day_staff_risk) != 7:
            return False
        if not all(isinstance(s, StaffRiskScore) and s.validate() for s in self.seven_day_staff_risk):
            return False
        if not isinstance(self.trend_indicators, dict):
            return False
        valid_trends = ["up", "down", "stable"]
        if not all(isinstance(k, str) and isinstance(v, str) and v in valid_trends 
                   for k, v in self.trend_indicators.items()):
            return False
        return True


@dataclass
class CrisisLesson:
    crisis_id: str
    date: datetime
    crisis_description: str
    bed_stress: float
    staff_risk: float
    actions_taken: List[str]
    outcome: str
    lessons_learned: str
    similarity_score: Optional[float] = None  # Populated during retrieval
    
    def validate(self) -> bool:
        """Validates data types and ranges"""
        if not isinstance(self.crisis_id, str) or not self.crisis_id.strip():
            return False
        if not isinstance(self.date, datetime):
            return False
        if not isinstance(self.crisis_description, str) or not self.crisis_description.strip():
            return False
        if not isinstance(self.bed_stress, (int, float)) or not (0 <= self.bed_stress <= 100):
            return False
        if not isinstance(self.staff_risk, (int, float)) or not (0 <= self.staff_risk <= 100):
            return False
        if not isinstance(self.actions_taken, list):
            return False
        if not all(isinstance(a, str) for a in self.actions_taken):
            return False
        if not isinstance(self.outcome, str) or not self.outcome.strip():
            return False
        if not isinstance(self.lessons_learned, str) or not self.lessons_learned.strip():
            return False
        if self.similarity_score is not None:
            if not isinstance(self.similarity_score, (int, float)) or not (0 <= self.similarity_score <= 1):
                return False
        return True


@dataclass
class HospitalContext:
    current_bed_stress: float
    current_staff_risk: float
    recent_trends: str
    predicted_admissions: int
    current_staff: int
    
    def validate(self) -> bool:
        """Validates data types and ranges"""
        if not isinstance(self.current_bed_stress, (int, float)) or not (0 <= self.current_bed_stress <= 100):
            return False
        if not isinstance(self.current_staff_risk, (int, float)) or not (0 <= self.current_staff_risk <= 100):
            return False
        if not isinstance(self.recent_trends, str):
            return False
        if not isinstance(self.predicted_admissions, int) or self.predicted_admissions < 0:
            return False
        if not isinstance(self.current_staff, int) or self.current_staff < 0:
            return False
        return True
