"""Prediction engine for hospital stress forecasting using Vertex AI"""
import json
import hashlib
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import pandas as pd
import numpy as np

from ..models import (
    HospitalRecord, BedForecast, DailyPrediction, StaffRiskScore,
    Recommendation, ScenarioRequest, ScenarioResult, HospitalContext
)
from ..db.vertex_ai_client import vertex_ai_client
from ..db.bigquery_client import bigquery_client
from ..db.redis_client import redis_client
from ..config import settings
from .rag_system import rag_system


class PredictionEngine:
    """AI-powered prediction engine for hospital capacity and staff risk forecasting"""
    
    def __init__(self):
        self.vertex_client = vertex_ai_client
        self.bigquery_client = bigquery_client
        self.redis_client = redis_client
        self.total_bed_capacity = 500  # Default capacity, should be configurable
    
    def forecast_bed_demand(
        self, 
        days_ahead: int = 7,
        historical_data: Optional[List[HospitalRecord]] = None
    ) -> BedForecast:
        """
        Generates 7-day bed demand forecast using Vertex AI
        
        Args:
            days_ahead: Number of days to forecast (default 7)
            historical_data: Optional historical data, if None will query from BigQuery
            
        Returns:
            BedForecast with daily predictions and confidence scores
        """
        # Check cache first
        cache_key = self._generate_cache_key("forecast", days_ahead, historical_data)
        cached_result = self.redis_client.get(cache_key)
        if cached_result:
            return BedForecast(**cached_result)
        
        # Get historical data if not provided
        if historical_data is None:
            historical_data = self._get_historical_data()
        
        # Handle missing data with forward-fill interpolation
        processed_data = self._handle_missing_data(historical_data)
        
        # Generate forecast using Vertex AI
        forecast_data = self._generate_ai_forecast(processed_data, days_ahead)
        
        # Create daily predictions
        predictions = []
        base_date = datetime.now().date()
        
        for i, day_data in enumerate(forecast_data):
            prediction_date = base_date + timedelta(days=i+1)
            predicted_beds = day_data.get('predicted_beds', 0)
            confidence = day_data.get('confidence', 50.0)
            
            # Calculate bed stress
            bed_stress = self._calculate_bed_stress(predicted_beds)
            
            # Determine high risk flag
            is_high_risk = bed_stress > 85.0
            
            prediction = DailyPrediction(
                date=datetime.combine(prediction_date, datetime.min.time()),
                predicted_beds=predicted_beds,
                bed_stress=bed_stress,
                confidence=confidence,
                is_high_risk=is_high_risk
            )
            predictions.append(prediction)
        
        # Calculate overall confidence
        overall_confidence = self.calculate_confidence(
            data_quality=self._assess_data_quality(processed_data),
            data_completeness=self._assess_data_completeness(processed_data),
            historical_accuracy=80.0  # Default historical accuracy
        )
        
        # Create forecast object
        forecast = BedForecast(
            predictions=predictions,
            overall_confidence=overall_confidence,
            generated_at=datetime.now()
        )
        
        # Cache the result
        self.redis_client.set(
            cache_key, 
            forecast.__dict__, 
            settings.prediction_cache_ttl
        )
        
        return forecast
    
    def calculate_confidence(
        self,
        data_quality: float,
        data_completeness: float,
        historical_accuracy: float
    ) -> float:
        """
        Calculates confidence score for predictions based on data quality metrics
        
        Args:
            data_quality: Quality score of the data (0-100)
            data_completeness: Completeness score of the data (0-100)
            historical_accuracy: Historical prediction accuracy (0-100)
            
        Returns:
            Confidence score (0-100)
        """
        # Weighted average of quality factors
        weights = {
            'quality': 0.4,
            'completeness': 0.3,
            'accuracy': 0.3
        }
        
        confidence = (
            data_quality * weights['quality'] +
            data_completeness * weights['completeness'] +
            historical_accuracy * weights['accuracy']
        )
        
        # Ensure confidence is within bounds
        return max(0.0, min(100.0, confidence))
    
    def _get_historical_data(self, days_back: int = 180) -> List[HospitalRecord]:
        """Retrieve historical data from BigQuery"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_back)
            sql = f"""
            SELECT date, admissions, beds_occupied, staff_on_duty, overload_flag
            FROM `{self.bigquery_client.get_table_ref('logs')}`
            WHERE date >= '{cutoff_date.date()}'
            ORDER BY date ASC
            """
            
            results = self.bigquery_client.query(sql)
            
            records = []
            for row in results:
                record = HospitalRecord(
                    date=datetime.combine(row['date'], datetime.min.time()),
                    admissions=row['admissions'],
                    beds_occupied=row['beds_occupied'],
                    staff_on_duty=row['staff_on_duty'],
                    overload_flag=row['overload_flag']
                )
                records.append(record)
            
            return records
            
        except Exception as e:
            print(f"Error retrieving historical data: {e}")
            return []
    
    def _handle_missing_data(self, data: List[HospitalRecord]) -> List[HospitalRecord]:
        """
        Handle missing data using forward-fill interpolation
        
        Args:
            data: List of hospital records with potential missing values
            
        Returns:
            List of hospital records with interpolated values
        """
        if not data:
            return data
        
        # Convert to DataFrame for easier manipulation
        df_data = []
        for record in data:
            df_data.append({
                'date': record.date,
                'admissions': record.admissions,
                'beds_occupied': record.beds_occupied,
                'staff_on_duty': record.staff_on_duty,
                'overload_flag': record.overload_flag
            })
        
        df = pd.DataFrame(df_data)
        
        # Forward fill missing values for numeric columns
        numeric_columns = ['admissions', 'beds_occupied', 'staff_on_duty']
        for col in numeric_columns:
            # Replace any None or negative values with NaN, then forward fill
            df[col] = df[col].replace([None, -1], np.nan)
            df[col] = df[col].ffill()
            # If still NaN (at the beginning), use 0
            df[col] = df[col].fillna(0)
        
        # Convert back to HospitalRecord objects
        processed_records = []
        for _, row in df.iterrows():
            record = HospitalRecord(
                date=row['date'],
                admissions=int(row['admissions']),
                beds_occupied=int(row['beds_occupied']),
                staff_on_duty=int(row['staff_on_duty']),
                overload_flag=row['overload_flag']
            )
            processed_records.append(record)
        
        return processed_records
    
    def _generate_ai_forecast(self, historical_data: List[HospitalRecord], days_ahead: int) -> List[Dict[str, Any]]:
        """Generate forecast using Vertex AI"""
        # Prepare historical data for the prompt
        data_summary = self._prepare_data_summary(historical_data)
        
        prompt = f"""
You are a hospital capacity forecasting expert. Given the following historical data:

{data_summary}

Generate a {days_ahead}-day forecast of bed demand. For each day, provide:
1. Predicted number of beds occupied
2. Confidence score (0-100)
3. Brief reasoning

Consider seasonal patterns, day-of-week effects, and recent trends.
Format your response as JSON with this structure:
[
  {{
    "day": 1,
    "predicted_beds": 250,
    "confidence": 85,
    "reasoning": "Based on recent trends..."
  }},
  ...
]
"""
        
        try:
            response = self.vertex_client.generate_content(
                prompt=prompt,
                temperature=0.2,  # Lower temperature for more consistent predictions
                max_tokens=2048
            )
            
            if response:
                # Parse JSON response
                forecast_data = json.loads(response)
                return forecast_data[:days_ahead]  # Ensure we only get requested days
            
        except Exception as e:
            print(f"Error generating AI forecast: {e}")
        
        # Fallback: generate simple forecast based on recent averages
        return self._generate_fallback_forecast(historical_data, days_ahead)
    
    def _prepare_data_summary(self, data: List[HospitalRecord]) -> str:
        """Prepare a summary of historical data for AI prompt"""
        if not data:
            return "No historical data available"
        
        # Get recent 30 days for summary
        recent_data = data[-30:] if len(data) > 30 else data
        
        summary_lines = []
        summary_lines.append("Recent hospital data (last 30 days):")
        summary_lines.append("Date | Admissions | Beds Occupied | Staff | Overload")
        summary_lines.append("-" * 55)
        
        for record in recent_data[-10:]:  # Show last 10 days
            date_str = record.date.strftime("%Y-%m-%d")
            overload_str = "YES" if record.overload_flag else "NO"
            summary_lines.append(
                f"{date_str} | {record.admissions:10d} | {record.beds_occupied:12d} | "
                f"{record.staff_on_duty:5d} | {overload_str:8s}"
            )
        
        # Add statistics
        avg_beds = sum(r.beds_occupied for r in recent_data) / len(recent_data)
        avg_admissions = sum(r.admissions for r in recent_data) / len(recent_data)
        overload_count = sum(1 for r in recent_data if r.overload_flag)
        
        summary_lines.append("")
        summary_lines.append(f"Average beds occupied: {avg_beds:.1f}")
        summary_lines.append(f"Average daily admissions: {avg_admissions:.1f}")
        summary_lines.append(f"Overload events in last 30 days: {overload_count}")
        
        return "\n".join(summary_lines)
    
    def _generate_fallback_forecast(self, data: List[HospitalRecord], days_ahead: int) -> List[Dict[str, Any]]:
        """Generate simple forecast based on recent averages when AI fails"""
        if not data:
            # Return default forecast if no data
            return [
                {
                    "day": i + 1,
                    "predicted_beds": 200,  # Default prediction
                    "confidence": 30,  # Low confidence
                    "reasoning": "No historical data available, using default values"
                }
                for i in range(days_ahead)
            ]
        
        # Calculate recent average
        recent_data = data[-14:] if len(data) > 14 else data
        avg_beds = sum(r.beds_occupied for r in recent_data) / len(recent_data)
        
        # Add some variation based on day of week patterns
        forecast = []
        for i in range(days_ahead):
            # Simple pattern: slightly higher on weekdays
            day_of_week = (datetime.now().date() + timedelta(days=i+1)).weekday()
            multiplier = 1.1 if day_of_week < 5 else 0.9  # Higher on weekdays
            
            predicted_beds = int(avg_beds * multiplier)
            
            forecast.append({
                "day": i + 1,
                "predicted_beds": predicted_beds,
                "confidence": 60,  # Moderate confidence for fallback
                "reasoning": f"Based on {len(recent_data)}-day average with day-of-week adjustment"
            })
        
        return forecast
    
    def _calculate_bed_stress(self, predicted_beds: int) -> float:
        """Calculate bed stress percentage"""
        if self.total_bed_capacity <= 0:
            return 0.0
        
        stress = (predicted_beds / self.total_bed_capacity) * 100
        return max(0.0, min(100.0, stress))  # Clamp between 0-100
    
    def _assess_data_quality(self, data: List[HospitalRecord]) -> float:
        """Assess the quality of historical data"""
        if not data:
            return 0.0
        
        quality_score = 100.0
        
        # Check for reasonable values
        for record in data:
            if record.admissions < 0 or record.beds_occupied < 0 or record.staff_on_duty < 0:
                quality_score -= 5.0
            
            # Check for unrealistic values
            if record.beds_occupied > self.total_bed_capacity * 1.5:  # 150% capacity seems unrealistic
                quality_score -= 2.0
            
            if record.admissions > 500:  # Very high admission count
                quality_score -= 1.0
        
        return max(0.0, min(100.0, quality_score))
    
    def _assess_data_completeness(self, data: List[HospitalRecord]) -> float:
        """Assess the completeness of historical data"""
        if not data:
            return 0.0
        
        # Check if we have enough data points
        days_of_data = len(data)
        
        if days_of_data >= 180:  # 6 months
            return 100.0
        elif days_of_data >= 90:  # 3 months
            return 80.0
        elif days_of_data >= 30:  # 1 month
            return 60.0
        elif days_of_data >= 7:  # 1 week
            return 40.0
        else:
            return 20.0
    
    def calculate_staff_risk(
        self,
        predicted_admissions: int,
        current_staff: int,
        historical_overloads: Optional[List[HospitalRecord]] = None
    ) -> StaffRiskScore:
        """
        Calculates staff overload risk (0-100) based on admissions and staffing
        
        Args:
            predicted_admissions: Predicted number of admissions
            current_staff: Current number of staff on duty
            historical_overloads: Optional list of historical overload events
            
        Returns:
            StaffRiskScore with score, confidence, and contributing factors
        """
        # Check cache first
        cache_key = self._generate_cache_key("staff_risk", predicted_admissions, current_staff)
        cached_result = self.redis_client.get(cache_key)
        if cached_result:
            return StaffRiskScore(**cached_result)
        
        # Get historical overload data if not provided
        if historical_overloads is None:
            historical_overloads = self._get_historical_overloads()
        
        # Calculate base risk score using staff-to-admission ratio
        base_risk = self._calculate_base_staff_risk(predicted_admissions, current_staff)
        
        # Learn from historical overload patterns
        pattern_risk = self._analyze_overload_patterns(
            predicted_admissions, current_staff, historical_overloads
        )
        
        # Combine base risk with pattern-based risk
        combined_risk = (base_risk * 0.6) + (pattern_risk * 0.4)
        
        # Ensure risk score is within bounds
        risk_score = max(0.0, min(100.0, combined_risk))
        
        # Determine if critical (> 75)
        is_critical = risk_score > 75.0
        
        # Identify contributing factors
        contributing_factors = self._identify_risk_factors(
            predicted_admissions, current_staff, risk_score, historical_overloads
        )
        
        # Calculate confidence based on data quality
        confidence = self._calculate_staff_risk_confidence(historical_overloads)
        
        # Create staff risk score object
        staff_risk = StaffRiskScore(
            risk_score=risk_score,
            confidence=confidence,
            is_critical=is_critical,
            contributing_factors=contributing_factors,
            generated_at=datetime.now()
        )
        
        # Cache the result
        self.redis_client.set(
            cache_key,
            staff_risk.__dict__,
            settings.staff_risk_cache_ttl  # 10-minute TTL for staff risk
        )
        
        return staff_risk
    
    def _get_historical_overloads(self, days_back: int = 365) -> List[HospitalRecord]:
        """Retrieve historical overload events from BigQuery"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_back)
            sql = f"""
            SELECT date, admissions, beds_occupied, staff_on_duty, overload_flag
            FROM `{self.bigquery_client.get_table_ref('logs')}`
            WHERE date >= '{cutoff_date.date()}' AND overload_flag = true
            ORDER BY date ASC
            """
            
            results = self.bigquery_client.query(sql)
            
            records = []
            for row in results:
                record = HospitalRecord(
                    date=datetime.combine(row['date'], datetime.min.time()),
                    admissions=row['admissions'],
                    beds_occupied=row['beds_occupied'],
                    staff_on_duty=row['staff_on_duty'],
                    overload_flag=row['overload_flag']
                )
                records.append(record)
            
            return records
            
        except Exception as e:
            print(f"Error retrieving historical overload data: {e}")
            return []
    
    def _calculate_base_staff_risk(self, predicted_admissions: int, current_staff: int) -> float:
        """Calculate base staff risk using staff-to-admission ratio"""
        if current_staff <= 0:
            return 100.0  # Maximum risk if no staff
        
        # Calculate staff-to-admission ratio
        staff_per_admission = current_staff / max(1, predicted_admissions)
        
        # Define risk thresholds based on typical hospital ratios
        # These are configurable thresholds that could be hospital-specific
        optimal_ratio = 0.5  # 1 staff per 2 admissions (optimal)
        warning_ratio = 0.3  # 1 staff per 3.3 admissions (warning)
        critical_ratio = 0.2  # 1 staff per 5 admissions (critical)
        
        if staff_per_admission >= optimal_ratio:
            # Low risk - adequate staffing
            risk = 20.0 * (1 - (staff_per_admission - optimal_ratio) / optimal_ratio)
            return max(0.0, risk)
        elif staff_per_admission >= warning_ratio:
            # Medium risk - staffing getting tight
            ratio_range = optimal_ratio - warning_ratio
            position_in_range = (optimal_ratio - staff_per_admission) / ratio_range
            return 20.0 + (position_in_range * 30.0)  # 20-50 range
        elif staff_per_admission >= critical_ratio:
            # High risk - understaffed
            ratio_range = warning_ratio - critical_ratio
            position_in_range = (warning_ratio - staff_per_admission) / ratio_range
            return 50.0 + (position_in_range * 30.0)  # 50-80 range
        else:
            # Critical risk - severely understaffed
            return 80.0 + min(20.0, (critical_ratio - staff_per_admission) * 100)
    
    def _analyze_overload_patterns(
        self, 
        predicted_admissions: int, 
        current_staff: int, 
        historical_overloads: List[HospitalRecord]
    ) -> float:
        """Analyze historical overload patterns to predict risk"""
        if not historical_overloads:
            return 50.0  # Default moderate risk if no historical data
        
        # Find similar conditions in historical data
        similar_conditions = []
        admission_tolerance = 20  # +/- 20 admissions
        staff_tolerance = 5      # +/- 5 staff
        
        for record in historical_overloads:
            admission_diff = abs(record.admissions - predicted_admissions)
            staff_diff = abs(record.staff_on_duty - current_staff)
            
            if admission_diff <= admission_tolerance and staff_diff <= staff_tolerance:
                similar_conditions.append(record)
        
        if not similar_conditions:
            # No similar conditions found, use broader analysis
            return self._analyze_general_overload_trends(
                predicted_admissions, current_staff, historical_overloads
            )
        
        # Calculate risk based on frequency of overloads in similar conditions
        total_similar = len(similar_conditions)
        overload_frequency = total_similar / max(1, len(historical_overloads))
        
        # Convert frequency to risk score
        pattern_risk = min(90.0, overload_frequency * 100.0)
        
        return pattern_risk
    
    def _analyze_general_overload_trends(
        self, 
        predicted_admissions: int, 
        current_staff: int, 
        historical_overloads: List[HospitalRecord]
    ) -> float:
        """Analyze general trends when no similar conditions are found"""
        if not historical_overloads:
            return 50.0
        
        # Calculate average conditions during overloads
        avg_overload_admissions = sum(r.admissions for r in historical_overloads) / len(historical_overloads)
        avg_overload_staff = sum(r.staff_on_duty for r in historical_overloads) / len(historical_overloads)
        
        # Compare current conditions to average overload conditions
        admission_ratio = predicted_admissions / max(1, avg_overload_admissions)
        staff_ratio = current_staff / max(1, avg_overload_staff)
        
        # Higher admissions and lower staff = higher risk
        risk_multiplier = admission_ratio / max(0.1, staff_ratio)
        
        # Convert to risk score
        base_risk = 40.0  # Base risk when no specific patterns found
        pattern_risk = base_risk * min(2.0, risk_multiplier)  # Cap at 2x multiplier
        
        return min(90.0, pattern_risk)
    
    def _identify_risk_factors(
        self, 
        predicted_admissions: int, 
        current_staff: int, 
        risk_score: float,
        historical_overloads: List[HospitalRecord]
    ) -> List[str]:
        """Identify contributing factors to staff risk"""
        factors = []
        
        # Staff-to-admission ratio analysis
        staff_per_admission = current_staff / max(1, predicted_admissions)
        
        if staff_per_admission < 0.2:
            factors.append("Severely understaffed for predicted admission volume")
        elif staff_per_admission < 0.3:
            factors.append("Below optimal staffing levels")
        
        if predicted_admissions > 300:
            factors.append("High admission volume predicted")
        
        if current_staff < 20:
            factors.append("Low absolute staff count")
        
        # Historical pattern analysis
        if historical_overloads:
            recent_overloads = [r for r in historical_overloads 
                              if (datetime.now() - r.date).days <= 30]
            if len(recent_overloads) > 3:
                factors.append("Recent history of frequent overload events")
            
            avg_overload_admissions = sum(r.admissions for r in historical_overloads) / len(historical_overloads)
            if predicted_admissions > avg_overload_admissions * 0.9:
                factors.append("Admission volume approaching historical overload levels")
        
        # Risk level factors
        if risk_score > 90:
            factors.append("Critical risk level - immediate action required")
        elif risk_score > 75:
            factors.append("High risk level - proactive measures recommended")
        
        # Ensure we always have at least one factor
        if not factors:
            if risk_score > 50:
                factors.append("Moderate risk based on current staffing and admission predictions")
            else:
                factors.append("Low risk - adequate staffing for predicted volume")
        
        return factors
    
    def _calculate_staff_risk_confidence(self, historical_overloads: List[HospitalRecord]) -> float:
        """Calculate confidence score for staff risk assessment"""
        base_confidence = 70.0
        
        # More historical data = higher confidence
        if len(historical_overloads) >= 50:
            data_confidence = 100.0
        elif len(historical_overloads) >= 20:
            data_confidence = 85.0
        elif len(historical_overloads) >= 10:
            data_confidence = 70.0
        elif len(historical_overloads) >= 5:
            data_confidence = 55.0
        else:
            data_confidence = 40.0
        
        # Recent data is more valuable
        recent_overloads = [r for r in historical_overloads 
                           if (datetime.now() - r.date).days <= 90]
        recency_bonus = min(20.0, len(recent_overloads) * 2.0)
        
        confidence = min(100.0, (base_confidence + data_confidence + recency_bonus) / 2)
        return confidence

    def generate_recommendations(
        self,
        bed_stress: float,
        staff_risk: float,
        historical_context: Optional[List[HospitalRecord]] = None
    ) -> List[Recommendation]:
        """
        Generates 3 prioritized recommendations with cost estimates using chain-of-thought reasoning
        
        Args:
            bed_stress: Current bed stress level (0-100)
            staff_risk: Current staff risk level (0-100)
            historical_context: Optional historical data for context
            
        Returns:
            List of exactly 3 Recommendation objects ranked by impact-to-cost ratio
        """
        # Check cache first
        cache_key = self._generate_cache_key("recommendations", bed_stress, staff_risk)
        cached_result = self.redis_client.get(cache_key)
        if cached_result:
            return [Recommendation(**rec) for rec in cached_result]
        
        # Get historical context if not provided
        if historical_context is None:
            historical_context = self._get_historical_data(days_back=90)
        
        # Generate base recommendations using chain-of-thought prompting
        recommendations = self._generate_ai_recommendations(bed_stress, staff_risk, historical_context)
        
        # Ensure we have exactly 3 recommendations
        if len(recommendations) != 3:
            recommendations = self._ensure_three_recommendations(recommendations, bed_stress, staff_risk)
        
        # Sort by impact-to-cost ratio (priority 1, 2, 3)
        recommendations = self._rank_recommendations_by_impact_cost_ratio(recommendations)
        
        # Enhance recommendations with RAG system (historical crisis lessons)
        recommendations = self._enhance_with_rag(recommendations, bed_stress, staff_risk, historical_context)
        
        # Cache the result
        self.redis_client.set(
            cache_key,
            [rec.__dict__ for rec in recommendations],
            settings.prediction_cache_ttl  # 15-minute TTL for recommendations
        )
        
        return recommendations
    
    def _generate_ai_recommendations(
        self, 
        bed_stress: float, 
        staff_risk: float, 
        historical_context: List[HospitalRecord]
    ) -> List[Recommendation]:
        """Generate recommendations using Vertex AI with chain-of-thought prompting"""
        
        # Prepare context data
        context_summary = self._prepare_recommendation_context(bed_stress, staff_risk, historical_context)
        
        prompt = f"""
You are a hospital operations expert providing actionable recommendations for capacity management.

Current Situation:
- Bed Stress Level: {bed_stress:.1f}% (85%+ is high risk)
- Staff Risk Level: {staff_risk:.1f}% (75%+ is critical)

Historical Context:
{context_summary}

Using chain-of-thought reasoning, generate exactly 3 prioritized recommendations to address the current situation.

For each recommendation, think through:
1. What is the specific problem this addresses?
2. What is the proposed solution?
3. Why is this solution effective?
4. What will it cost (in dollars)?
5. What impact will it have (0-100 scale)?
6. How long will it take to implement?

Format your response as JSON with this exact structure:
[
  {{
    "title": "Brief action-oriented title",
    "description": "Detailed description of what to do",
    "rationale": "Chain-of-thought explanation: Problem -> Solution -> Why it works -> Expected outcome",
    "cost_estimate": 15000.0,
    "impact_score": 85.0,
    "priority": 1,
    "implementation_time": "24 hours"
  }},
  {{
    "title": "Second recommendation title",
    "description": "Second recommendation description",
    "rationale": "Second recommendation rationale with reasoning",
    "cost_estimate": 8000.0,
    "impact_score": 70.0,
    "priority": 2,
    "implementation_time": "3 days"
  }},
  {{
    "title": "Third recommendation title",
    "description": "Third recommendation description", 
    "rationale": "Third recommendation rationale with reasoning",
    "cost_estimate": 25000.0,
    "impact_score": 60.0,
    "priority": 3,
    "implementation_time": "1 week"
  }}
]

Ensure recommendations are:
- Specific and actionable
- Appropriate for the current stress levels
- Ranked by impact-to-cost ratio (priority 1 = highest ratio)
- Realistic in cost and timeline
"""
        
        try:
            response = self.vertex_client.generate_content(
                prompt=prompt,
                temperature=0.7,  # Higher temperature for creative recommendations
                max_tokens=2048
            )
            
            if response:
                # Parse JSON response
                recommendations_data = json.loads(response)
                
                # Convert to Recommendation objects
                recommendations = []
                for i, rec_data in enumerate(recommendations_data[:3]):  # Ensure only 3
                    recommendation = Recommendation(
                        title=rec_data.get('title', f'Recommendation {i+1}'),
                        description=rec_data.get('description', 'No description provided'),
                        rationale=rec_data.get('rationale', 'No rationale provided'),
                        cost_estimate=float(rec_data.get('cost_estimate', 10000.0)),
                        impact_score=float(rec_data.get('impact_score', 50.0)),
                        priority=int(rec_data.get('priority', i+1)),
                        implementation_time=rec_data.get('implementation_time', '1 week')
                    )
                    recommendations.append(recommendation)
                
                return recommendations
                
        except Exception as e:
            print(f"Error generating AI recommendations: {e}")
        
        # Fallback: generate default recommendations
        return self._generate_fallback_recommendations(bed_stress, staff_risk)
    
    def _prepare_recommendation_context(
        self, 
        bed_stress: float, 
        staff_risk: float, 
        historical_context: List[HospitalRecord]
    ) -> str:
        """Prepare context summary for recommendation generation"""
        
        context_lines = []
        
        # Current situation analysis
        if bed_stress > 85 or staff_risk > 75:
            context_lines.append("CRITICAL SITUATION: Immediate action required")
        elif bed_stress > 70 or staff_risk > 60:
            context_lines.append("HIGH STRESS: Proactive measures recommended")
        else:
            context_lines.append("MODERATE STRESS: Preventive measures advisable")
        
        # Historical patterns
        if historical_context:
            recent_data = historical_context[-30:] if len(historical_context) > 30 else historical_context
            
            # Calculate averages
            avg_beds = sum(r.beds_occupied for r in recent_data) / len(recent_data)
            avg_admissions = sum(r.admissions for r in recent_data) / len(recent_data)
            avg_staff = sum(r.staff_on_duty for r in recent_data) / len(recent_data)
            overload_count = sum(1 for r in recent_data if r.overload_flag)
            
            context_lines.append(f"Recent 30-day averages:")
            context_lines.append(f"- Average beds occupied: {avg_beds:.1f}")
            context_lines.append(f"- Average daily admissions: {avg_admissions:.1f}")
            context_lines.append(f"- Average staff on duty: {avg_staff:.1f}")
            context_lines.append(f"- Overload events: {overload_count}")
            
            # Identify trends
            if len(recent_data) >= 14:
                first_week = recent_data[:7]
                last_week = recent_data[-7:]
                
                first_week_avg_beds = sum(r.beds_occupied for r in first_week) / 7
                last_week_avg_beds = sum(r.beds_occupied for r in last_week) / 7
                
                if last_week_avg_beds > first_week_avg_beds * 1.1:
                    context_lines.append("- Trend: Bed occupancy increasing")
                elif last_week_avg_beds < first_week_avg_beds * 0.9:
                    context_lines.append("- Trend: Bed occupancy decreasing")
                else:
                    context_lines.append("- Trend: Bed occupancy stable")
        else:
            context_lines.append("Limited historical data available")
        
        return "\n".join(context_lines)
    
    def _generate_fallback_recommendations(
        self, 
        bed_stress: float, 
        staff_risk: float
    ) -> List[Recommendation]:
        """Generate fallback recommendations when AI fails"""
        
        recommendations = []
        
        # Recommendation 1: Always relevant - staff optimization
        if staff_risk > 75:
            rec1 = Recommendation(
                title="Emergency Staff Augmentation",
                description="Immediately call in additional nursing staff and activate on-call physicians to handle increased patient load",
                rationale="High staff risk detected. Adding staff directly reduces patient-to-staff ratios, improving care quality and reducing overload risk. Emergency staffing protocols can be activated within hours.",
                cost_estimate=12000.0,  # Overtime and agency staff costs
                impact_score=90.0,
                priority=1,
                implementation_time="4 hours"
            )
        else:
            rec1 = Recommendation(
                title="Optimize Staff Scheduling",
                description="Review and adjust staff schedules to better align with predicted patient volumes and peak admission times",
                rationale="Current staffing appears adequate but could be optimized. Better schedule alignment prevents future overload situations and improves efficiency without major cost increases.",
                cost_estimate=2000.0,  # Administrative time and scheduling software
                impact_score=65.0,
                priority=1,
                implementation_time="24 hours"
            )
        
        # Recommendation 2: Bed management
        if bed_stress > 85:
            rec2 = Recommendation(
                title="Activate Surge Capacity Protocol",
                description="Open additional beds in overflow areas and expedite discharge planning for stable patients",
                rationale="High bed stress requires immediate capacity expansion. Surge protocols can quickly add 10-15% capacity while discharge acceleration frees existing beds. Combined approach maximizes available capacity.",
                cost_estimate=8000.0,  # Additional equipment and staffing for overflow areas
                impact_score=85.0,
                priority=2,
                implementation_time="6 hours"
            )
        else:
            rec2 = Recommendation(
                title="Enhance Discharge Planning",
                description="Implement early discharge planning rounds and coordinate with post-acute care facilities to reduce length of stay",
                rationale="Proactive discharge planning prevents bed shortages before they occur. Early identification of discharge candidates and coordination with external facilities reduces average length of stay by 0.5-1 days.",
                cost_estimate=5000.0,  # Care coordinator time and system improvements
                impact_score=70.0,
                priority=2,
                implementation_time="2 days"
            )
        
        # Recommendation 3: System improvements
        if bed_stress > 80 or staff_risk > 70:
            rec3 = Recommendation(
                title="Implement Real-time Capacity Dashboard",
                description="Deploy hospital-wide capacity monitoring system with automated alerts for department heads and administrators",
                rationale="High stress levels indicate need for better situational awareness. Real-time dashboards enable faster decision-making and proactive resource allocation. Automated alerts ensure key personnel are notified immediately when thresholds are exceeded.",
                cost_estimate=25000.0,  # Software licensing and implementation
                impact_score=75.0,
                priority=3,
                implementation_time="2 weeks"
            )
        else:
            rec3 = Recommendation(
                title="Preventive Maintenance Review",
                description="Conduct comprehensive review of equipment and facility maintenance to prevent unexpected capacity reductions",
                rationale="Moderate stress levels provide opportunity for preventive measures. Equipment failures can suddenly reduce capacity during critical times. Proactive maintenance prevents emergency situations and ensures all resources remain available.",
                cost_estimate=15000.0,  # Maintenance team time and replacement parts
                impact_score=55.0,
                priority=3,
                implementation_time="1 week"
            )
        
        recommendations = [rec1, rec2, rec3]
        
        # Ensure proper ranking by impact-to-cost ratio
        return self._rank_recommendations_by_impact_cost_ratio(recommendations)
    
    def _ensure_three_recommendations(
        self, 
        recommendations: List[Recommendation], 
        bed_stress: float, 
        staff_risk: float
    ) -> List[Recommendation]:
        """Ensure we have exactly 3 recommendations"""
        
        if len(recommendations) == 3:
            return recommendations
        elif len(recommendations) > 3:
            # Take the top 3 by impact score
            sorted_recs = sorted(recommendations, key=lambda r: r.impact_score, reverse=True)
            return sorted_recs[:3]
        else:
            # Need to add more recommendations
            fallback_recs = self._generate_fallback_recommendations(bed_stress, staff_risk)
            
            # Combine existing with fallback, avoiding duplicates
            combined = list(recommendations)
            existing_titles = {rec.title.lower() for rec in recommendations}
            
            for fallback_rec in fallback_recs:
                if len(combined) >= 3:
                    break
                if fallback_rec.title.lower() not in existing_titles:
                    combined.append(fallback_rec)
            
            # If still not enough, add generic recommendations
            while len(combined) < 3:
                generic_rec = Recommendation(
                    title=f"Additional Capacity Measure {len(combined)}",
                    description="Implement additional capacity management measures based on current situation",
                    rationale="Generic recommendation to ensure minimum of 3 recommendations are provided",
                    cost_estimate=10000.0,
                    impact_score=50.0,
                    priority=len(combined) + 1,
                    implementation_time="1 week"
                )
                combined.append(generic_rec)
            
            return combined[:3]
    
    def _rank_recommendations_by_impact_cost_ratio(
        self, 
        recommendations: List[Recommendation]
    ) -> List[Recommendation]:
        """Rank recommendations by impact-to-cost ratio and assign priorities"""
        
        # Calculate impact-to-cost ratio for each recommendation
        for rec in recommendations:
            # Avoid division by zero
            if rec.cost_estimate <= 0:
                rec.cost_estimate = 1000.0  # Minimum cost
            
            # Calculate ratio (higher is better)
            ratio = rec.impact_score / rec.cost_estimate
            rec._ratio = ratio  # Store temporarily for sorting
        
        # Sort by ratio (descending - higher ratio = better)
        sorted_recs = sorted(recommendations, key=lambda r: r._ratio, reverse=True)
        
        # Assign priorities (1 = highest ratio, 3 = lowest ratio)
        for i, rec in enumerate(sorted_recs):
            rec.priority = i + 1
            # Remove temporary ratio attribute
            if hasattr(rec, '_ratio'):
                delattr(rec, '_ratio')
        
        return sorted_recs

    def _generate_cache_key(self, operation: str, *args) -> str:
        """Generate cache key for predictions"""
        # Create a hash of the arguments
        key_data = f"{operation}:{':'.join(str(arg) for arg in args)}"
        hash_obj = hashlib.md5(key_data.encode())
        return f"prediction:{hash_obj.hexdigest()}"
    
    def invalidate_cache(self) -> bool:
        """
        Invalidate all prediction caches
        Should be called when new data is uploaded
        
        Returns:
            True if cache invalidation succeeded, False otherwise
        """
        try:
            # Invalidate all prediction-related caches
            return self.redis_client.invalidate_pattern("prediction:*")
        except Exception as e:
            print(f"Error invalidating cache: {e}")
            return False
    
    def get_dashboard_data(self) -> 'DashboardData':
        """
        Get comprehensive dashboard data with caching
        
        Returns:
            DashboardData with all metrics for the dashboard
        """
        from ..models import DashboardData
        
        # Check cache first
        cache_key = "dashboard:data"
        cached_result = self.redis_client.get(cache_key)
        if cached_result:
            # Reconstruct nested objects
            cached_result['seven_day_forecast'] = BedForecast(**cached_result['seven_day_forecast'])
            cached_result['seven_day_forecast'].predictions = [
                DailyPrediction(**p) for p in cached_result['seven_day_forecast'].predictions
            ]
            cached_result['seven_day_staff_risk'] = [
                StaffRiskScore(**s) for s in cached_result['seven_day_staff_risk']
            ]
            return DashboardData(**cached_result)
        
        # Get historical data
        historical_data = self._get_historical_data()
        
        # Generate 7-day forecast
        seven_day_forecast = self.forecast_bed_demand(
            days_ahead=7,
            historical_data=historical_data
        )
        
        # Calculate current bed stress (from most recent prediction)
        bed_stress_current = seven_day_forecast.predictions[0].bed_stress if seven_day_forecast.predictions else 0.0
        
        # Calculate staff risk for each of the next 7 days
        seven_day_staff_risk = []
        
        if historical_data:
            recent_data = historical_data[-7:] if len(historical_data) >= 7 else historical_data
            avg_staff = sum(r.staff_on_duty for r in recent_data) / len(recent_data)
        else:
            avg_staff = 30
        
        for prediction in seven_day_forecast.predictions:
            # Estimate admissions based on bed occupancy
            estimated_admissions = int(prediction.predicted_beds * 0.3)  # Rough estimate
            
            staff_risk = self.calculate_staff_risk(
                predicted_admissions=estimated_admissions,
                current_staff=int(avg_staff),
                historical_overloads=self._get_historical_overloads()
            )
            seven_day_staff_risk.append(staff_risk)
        
        # Get current staff risk (from first day)
        staff_risk_current = seven_day_staff_risk[0].risk_score if seven_day_staff_risk else 0.0
        
        # Count active alerts (high risk days)
        active_alerts_count = sum(1 for p in seven_day_forecast.predictions if p.is_high_risk)
        active_alerts_count += sum(1 for s in seven_day_staff_risk if s.is_critical)
        
        # Generate recommendations if needed
        recommendations = []
        recommendations_count = 0
        if bed_stress_current > 85 or staff_risk_current > 75:
            recommendations = self.generate_recommendations(
                bed_stress=bed_stress_current,
                staff_risk=staff_risk_current,
                historical_context=historical_data
            )
            recommendations_count = len(recommendations)
        
        # Calculate trend indicators
        trend_indicators = self._calculate_trend_indicators(
            seven_day_forecast,
            seven_day_staff_risk
        )
        
        # Create dashboard data
        dashboard_data = DashboardData(
            bed_stress_current=bed_stress_current,
            staff_risk_current=staff_risk_current,
            active_alerts_count=active_alerts_count,
            recommendations_count=recommendations_count,
            seven_day_forecast=seven_day_forecast,
            seven_day_staff_risk=seven_day_staff_risk,
            trend_indicators=trend_indicators
        )
        
        # Cache the result with 30-second TTL
        # Need to serialize nested objects for caching
        cache_data = {
            'bed_stress_current': dashboard_data.bed_stress_current,
            'staff_risk_current': dashboard_data.staff_risk_current,
            'active_alerts_count': dashboard_data.active_alerts_count,
            'recommendations_count': dashboard_data.recommendations_count,
            'seven_day_forecast': {
                'predictions': [p.__dict__ for p in dashboard_data.seven_day_forecast.predictions],
                'overall_confidence': dashboard_data.seven_day_forecast.overall_confidence,
                'generated_at': dashboard_data.seven_day_forecast.generated_at.isoformat()
            },
            'seven_day_staff_risk': [s.__dict__ for s in dashboard_data.seven_day_staff_risk],
            'trend_indicators': dashboard_data.trend_indicators
        }
        
        self.redis_client.set(
            cache_key,
            cache_data,
            settings.dashboard_cache_ttl
        )
        
        return dashboard_data
    
    def _calculate_trend_indicators(
        self,
        forecast: BedForecast,
        staff_risks: List[StaffRiskScore]
    ) -> Dict[str, str]:
        """
        Calculate trend indicators for dashboard metrics
        
        Args:
            forecast: 7-day bed forecast
            staff_risks: 7-day staff risk scores
            
        Returns:
            Dictionary with trend indicators ("up", "down", "stable")
        """
        trends = {}
        
        # Bed stress trend (compare first 3 days to last 3 days)
        if len(forecast.predictions) >= 6:
            first_half_bed_stress = sum(p.bed_stress for p in forecast.predictions[:3]) / 3
            second_half_bed_stress = sum(p.bed_stress for p in forecast.predictions[-3:]) / 3
            
            if second_half_bed_stress > first_half_bed_stress * 1.05:  # 5% threshold
                trends['bed_stress'] = 'up'
            elif second_half_bed_stress < first_half_bed_stress * 0.95:
                trends['bed_stress'] = 'down'
            else:
                trends['bed_stress'] = 'stable'
        else:
            trends['bed_stress'] = 'stable'
        
        # Staff risk trend
        if len(staff_risks) >= 6:
            first_half_staff_risk = sum(s.risk_score for s in staff_risks[:3]) / 3
            second_half_staff_risk = sum(s.risk_score for s in staff_risks[-3:]) / 3
            
            if second_half_staff_risk > first_half_staff_risk * 1.05:
                trends['staff_risk'] = 'up'
            elif second_half_staff_risk < first_half_staff_risk * 0.95:
                trends['staff_risk'] = 'down'
            else:
                trends['staff_risk'] = 'stable'
        else:
            trends['staff_risk'] = 'stable'
        
        return trends
    
    def simulate_scenario(
        self,
        sick_rate: float,
        admission_surge: float,
        baseline_date: Optional[datetime] = None
    ) -> ScenarioResult:
        """
        Simulates what-if scenario with adjusted parameters
        
        Args:
            sick_rate: Staff sick rate (0.0 to 0.5, representing 0% to 50%)
            admission_surge: Admission surge percentage (-0.3 to 1.0, representing -30% to +100%)
            baseline_date: Optional baseline date for comparison (defaults to now)
            
        Returns:
            ScenarioResult with baseline vs scenario comparison
        """
        # Validate parameters
        if not (0.0 <= sick_rate <= 0.5):
            raise ValueError(f"sick_rate must be between 0.0 and 0.5, got {sick_rate}")
        if not (-0.3 <= admission_surge <= 1.0):
            raise ValueError(f"admission_surge must be between -0.3 and 1.0, got {admission_surge}")
        
        if baseline_date is None:
            baseline_date = datetime.now()
        
        # Get historical data for baseline
        historical_data = self._get_historical_data()
        
        # Generate baseline forecast (without scenario adjustments)
        baseline_forecast = self.forecast_bed_demand(
            days_ahead=7,
            historical_data=historical_data
        )
        
        # Calculate baseline staff risk
        if historical_data:
            recent_data = historical_data[-7:] if len(historical_data) >= 7 else historical_data
            avg_admissions = sum(r.admissions for r in recent_data) / len(recent_data)
            avg_staff = sum(r.staff_on_duty for r in recent_data) / len(recent_data)
        else:
            avg_admissions = 100
            avg_staff = 30
        
        baseline_staff_risk = self.calculate_staff_risk(
            predicted_admissions=int(avg_admissions),
            current_staff=int(avg_staff),
            historical_overloads=self._get_historical_overloads()
        )
        
        # Apply scenario adjustments to create modified forecast
        scenario_forecast = self._apply_scenario_adjustments(
            baseline_forecast,
            sick_rate,
            admission_surge
        )
        
        # Calculate scenario staff risk with adjustments
        # Reduce staff by sick_rate and increase admissions by admission_surge
        scenario_staff = int(avg_staff * (1 - sick_rate))
        scenario_admissions = int(avg_admissions * (1 + admission_surge))
        
        scenario_staff_risk = self.calculate_staff_risk(
            predicted_admissions=scenario_admissions,
            current_staff=max(1, scenario_staff),  # Ensure at least 1 staff
            historical_overloads=self._get_historical_overloads()
        )
        
        # Generate impact summary
        impact_summary = self._generate_impact_summary(
            baseline_forecast,
            scenario_forecast,
            baseline_staff_risk,
            scenario_staff_risk,
            sick_rate,
            admission_surge
        )
        
        # Create scenario result
        scenario_result = ScenarioResult(
            baseline_forecast=baseline_forecast,
            scenario_forecast=scenario_forecast,
            baseline_staff_risk=baseline_staff_risk,
            scenario_staff_risk=scenario_staff_risk,
            impact_summary=impact_summary
        )
        
        return scenario_result
    
    def _apply_scenario_adjustments(
        self,
        baseline_forecast: BedForecast,
        sick_rate: float,
        admission_surge: float
    ) -> BedForecast:
        """
        Apply scenario adjustments to baseline forecast
        
        Args:
            baseline_forecast: Baseline forecast to adjust
            sick_rate: Staff sick rate (0.0 to 0.5)
            admission_surge: Admission surge percentage (-0.3 to 1.0)
            
        Returns:
            Adjusted BedForecast with scenario parameters applied
        """
        adjusted_predictions = []
        
        for prediction in baseline_forecast.predictions:
            # Adjust predicted beds based on admission surge
            # More admissions typically lead to more beds occupied
            adjusted_beds = int(prediction.predicted_beds * (1 + admission_surge * 0.8))
            adjusted_beds = max(0, adjusted_beds)  # Ensure non-negative
            
            # Recalculate bed stress with adjusted beds
            adjusted_bed_stress = self._calculate_bed_stress(adjusted_beds)
            
            # Adjust confidence - scenarios have lower confidence
            adjusted_confidence = prediction.confidence * 0.85  # 15% confidence reduction for scenarios
            
            # Recalculate high risk flag
            is_high_risk = adjusted_bed_stress > 85.0
            
            adjusted_prediction = DailyPrediction(
                date=prediction.date,
                predicted_beds=adjusted_beds,
                bed_stress=adjusted_bed_stress,
                confidence=adjusted_confidence,
                is_high_risk=is_high_risk
            )
            adjusted_predictions.append(adjusted_prediction)
        
        # Create adjusted forecast
        adjusted_forecast = BedForecast(
            predictions=adjusted_predictions,
            overall_confidence=baseline_forecast.overall_confidence * 0.85,
            generated_at=datetime.now()
        )
        
        return adjusted_forecast
    
    def _generate_impact_summary(
        self,
        baseline_forecast: BedForecast,
        scenario_forecast: BedForecast,
        baseline_staff_risk: StaffRiskScore,
        scenario_staff_risk: StaffRiskScore,
        sick_rate: float,
        admission_surge: float
    ) -> str:
        """
        Generate human-readable impact summary comparing baseline to scenario
        
        Args:
            baseline_forecast: Baseline bed forecast
            scenario_forecast: Scenario bed forecast
            baseline_staff_risk: Baseline staff risk
            scenario_staff_risk: Scenario staff risk
            sick_rate: Applied sick rate
            admission_surge: Applied admission surge
            
        Returns:
            Impact summary string
        """
        summary_lines = []
        
        # Scenario parameters
        summary_lines.append(f"Scenario Parameters:")
        summary_lines.append(f"- Staff sick rate: {sick_rate*100:.1f}%")
        summary_lines.append(f"- Admission surge: {admission_surge*100:+.1f}%")
        summary_lines.append("")
        
        # Bed stress comparison
        baseline_avg_stress = sum(p.bed_stress for p in baseline_forecast.predictions) / len(baseline_forecast.predictions)
        scenario_avg_stress = sum(p.bed_stress for p in scenario_forecast.predictions) / len(scenario_forecast.predictions)
        stress_change = scenario_avg_stress - baseline_avg_stress
        
        summary_lines.append(f"Bed Stress Impact:")
        summary_lines.append(f"- Baseline average: {baseline_avg_stress:.1f}%")
        summary_lines.append(f"- Scenario average: {scenario_avg_stress:.1f}%")
        summary_lines.append(f"- Change: {stress_change:+.1f}%")
        
        if scenario_avg_stress > 85:
            summary_lines.append("- WARNING: Scenario results in HIGH RISK bed stress levels")
        summary_lines.append("")
        
        # Staff risk comparison
        risk_change = scenario_staff_risk.risk_score - baseline_staff_risk.risk_score
        summary_lines.append(f"Staff Risk Impact:")
        summary_lines.append(f"- Baseline risk: {baseline_staff_risk.risk_score:.1f}")
        summary_lines.append(f"- Scenario risk: {scenario_staff_risk.risk_score:.1f}")
        summary_lines.append(f"- Change: {risk_change:+.1f}")
        
        if scenario_staff_risk.is_critical:
            summary_lines.append("- WARNING: Scenario results in CRITICAL staff risk levels")
        summary_lines.append("")
        
        # High-risk days comparison
        baseline_high_risk_days = sum(1 for p in baseline_forecast.predictions if p.is_high_risk)
        scenario_high_risk_days = sum(1 for p in scenario_forecast.predictions if p.is_high_risk)
        
        summary_lines.append(f"High-Risk Days:")
        summary_lines.append(f"- Baseline: {baseline_high_risk_days} out of 7 days")
        summary_lines.append(f"- Scenario: {scenario_high_risk_days} out of 7 days")
        
        if scenario_high_risk_days > baseline_high_risk_days:
            summary_lines.append(f"- Scenario adds {scenario_high_risk_days - baseline_high_risk_days} additional high-risk days")
        elif scenario_high_risk_days < baseline_high_risk_days:
            summary_lines.append(f"- Scenario reduces high-risk days by {baseline_high_risk_days - scenario_high_risk_days}")
        else:
            summary_lines.append("- No change in high-risk days")
        
        summary_lines.append("")
        
        # Overall assessment
        if stress_change > 10 or risk_change > 10:
            summary_lines.append("Overall Assessment: SIGNIFICANT NEGATIVE IMPACT - Immediate mitigation required")
        elif stress_change > 5 or risk_change > 5:
            summary_lines.append("Overall Assessment: MODERATE NEGATIVE IMPACT - Proactive measures recommended")
        elif stress_change < -5 or risk_change < -5:
            summary_lines.append("Overall Assessment: POSITIVE IMPACT - Scenario improves hospital capacity")
        else:
            summary_lines.append("Overall Assessment: MINIMAL IMPACT - Scenario has limited effect on operations")
        
        return "\n".join(summary_lines)

    def _enhance_with_rag(
        self,
        recommendations: List[Recommendation],
        bed_stress: float,
        staff_risk: float,
        historical_context: List[HospitalRecord]
    ) -> List[Recommendation]:
        """
        Enhance recommendations with historical crisis lessons using RAG system
        
        Args:
            recommendations: Base recommendations to enhance
            bed_stress: Current bed stress level
            staff_risk: Current staff risk level
            historical_context: Historical hospital data
            
        Returns:
            Enhanced recommendations with historical insights
        """
        try:
            # Create current hospital context
            recent_data = historical_context[-7:] if len(historical_context) >= 7 else historical_context
            
            if recent_data:
                avg_admissions = sum(r.admissions for r in recent_data) / len(recent_data)
                avg_staff = sum(r.staff_on_duty for r in recent_data) / len(recent_data)
                
                # Determine trend
                if len(recent_data) >= 3:
                    first_half = recent_data[:len(recent_data)//2]
                    second_half = recent_data[len(recent_data)//2:]
                    first_avg = sum(r.beds_occupied for r in first_half) / len(first_half)
                    second_avg = sum(r.beds_occupied for r in second_half) / len(second_half)
                    
                    if second_avg > first_avg * 1.1:
                        trend = "Increasing bed occupancy"
                    elif second_avg < first_avg * 0.9:
                        trend = "Decreasing bed occupancy"
                    else:
                        trend = "Stable bed occupancy"
                else:
                    trend = "Insufficient data for trend analysis"
            else:
                avg_admissions = 100
                avg_staff = 30
                trend = "No historical data available"
            
            context = HospitalContext(
                current_bed_stress=bed_stress,
                current_staff_risk=staff_risk,
                recent_trends=trend,
                predicted_admissions=int(avg_admissions),
                current_staff=int(avg_staff)
            )
            
            # Retrieve similar historical crises
            similar_crises = rag_system.retrieve_similar_crises(context, top_k=5)
            
            # Enhance recommendations with historical lessons
            if similar_crises:
                enhanced_recommendations = rag_system.enhance_recommendations(
                    recommendations,
                    similar_crises
                )
                return enhanced_recommendations
            else:
                # No similar crises found, return original recommendations
                return recommendations
                
        except Exception as e:
            print(f"Error enhancing recommendations with RAG: {e}")
            # Return original recommendations if RAG enhancement fails
            return recommendations