"""Synthetic data generator for hospital records"""
import random
from datetime import datetime, timedelta
from typing import List, Optional
from ..models import HospitalRecord


class SyntheticDataGenerator:
    """Generates realistic synthetic hospital data"""
    
    def __init__(self, seed: Optional[int] = None):
        """Initialize generator with optional seed for reproducibility"""
        self.seed = seed
        self._rng = random.Random(seed)
    
    def generate_six_months(self, end_date: datetime = None) -> List[HospitalRecord]:
        """
        Generate 6 months of realistic hospital data
        
        Args:
            end_date: The end date for the data range (defaults to today)
        
        Returns:
            List of HospitalRecord objects covering 6 months
        """
        if end_date is None:
            end_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Calculate start date (6 months = ~180 days)
        start_date = end_date - timedelta(days=180)
        
        records = []
        current_date = start_date
        
        # Base values for realistic hospital data
        base_admissions = 50
        base_beds_occupied = 200
        base_staff = 30
        
        while current_date <= end_date:
            # Generate realistic data with patterns
            admissions = self._generate_admissions(current_date, base_admissions)
            beds_occupied = self._generate_beds_occupied(current_date, base_beds_occupied, admissions)
            staff_on_duty = self._generate_staff(current_date, base_staff)
            overload_flag = self._determine_overload(beds_occupied, staff_on_duty, admissions)
            
            record = HospitalRecord(
                date=current_date,
                admissions=admissions,
                beds_occupied=beds_occupied,
                staff_on_duty=staff_on_duty,
                overload_flag=overload_flag
            )
            records.append(record)
            
            current_date += timedelta(days=1)
        
        return records
    
    def _generate_admissions(self, date: datetime, base: int) -> int:
        """Generate admissions with weekday/weekend and seasonal patterns"""
        # Weekday/weekend pattern (weekends have fewer admissions)
        weekday = date.weekday()
        if weekday >= 5:  # Saturday or Sunday
            weekday_factor = 0.7
        else:
            weekday_factor = 1.0
        
        # Seasonal variation (winter months have more admissions)
        month = date.month
        if month in [12, 1, 2]:  # Winter
            seasonal_factor = 1.3
        elif month in [6, 7, 8]:  # Summer
            seasonal_factor = 0.9
        else:
            seasonal_factor = 1.0
        
        # Random variation (+/- 30%)
        random_factor = self._rng.uniform(0.7, 1.3)
        
        admissions = int(base * weekday_factor * seasonal_factor * random_factor)
        
        # Occasional surge events (5% chance)
        if self._rng.random() < 0.05:
            admissions = int(admissions * self._rng.uniform(1.5, 2.0))
        
        return max(0, admissions)
    
    def _generate_beds_occupied(self, date: datetime, base: int, admissions: int) -> int:
        """Generate beds occupied based on admissions and patterns"""
        # Beds occupied correlates with admissions
        admission_influence = int(admissions * 2.5)
        
        # Weekday/weekend pattern
        weekday = date.weekday()
        if weekday >= 5:
            weekday_factor = 0.85
        else:
            weekday_factor = 1.0
        
        # Seasonal variation
        month = date.month
        if month in [12, 1, 2]:  # Winter
            seasonal_factor = 1.2
        else:
            seasonal_factor = 1.0
        
        # Random variation
        random_factor = self._rng.uniform(0.8, 1.2)
        
        beds = int((base + admission_influence * 0.3) * weekday_factor * seasonal_factor * random_factor)
        
        return max(0, beds)
    
    def _generate_staff(self, date: datetime, base: int) -> int:
        """Generate staff on duty with weekday/weekend patterns"""
        # Weekday/weekend pattern (fewer staff on weekends)
        weekday = date.weekday()
        if weekday >= 5:
            weekday_factor = 0.75
        else:
            weekday_factor = 1.0
        
        # Random variation (+/- 20%)
        random_factor = self._rng.uniform(0.8, 1.2)
        
        staff = int(base * weekday_factor * random_factor)
        
        # Occasional staff shortage (3% chance)
        if self._rng.random() < 0.03:
            staff = int(staff * self._rng.uniform(0.5, 0.7))
        
        return max(1, staff)
    
    def _determine_overload(self, beds_occupied: int, staff_on_duty: int, admissions: int) -> bool:
        """Determine if hospital is in overload state"""
        # Calculate patient-to-staff ratio
        patient_per_staff = beds_occupied / max(staff_on_duty, 1)
        
        # Overload if:
        # - Patient-to-staff ratio > 10
        # - Beds occupied > 300 (assuming capacity around 350)
        # - High admissions (> 80) with low staff (< 20)
        
        if patient_per_staff > 10:
            return True
        if beds_occupied > 300:
            return True
        if admissions > 80 and staff_on_duty < 20:
            return True
        
        return False
