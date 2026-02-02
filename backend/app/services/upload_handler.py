"""CSV upload handler for hospital data"""
import pandas as pd
from typing import List, BinaryIO, Optional
from datetime import datetime
from io import BytesIO
from ..models import HospitalRecord, ValidationResult
from ..config import settings


class UploadHandler:
    """Handles CSV file uploads and data storage"""
    
    REQUIRED_COLUMNS = ['date', 'admissions', 'beds_occupied', 'staff_on_duty', 'overload_flag']
    MAX_FILE_SIZE_BYTES = settings.max_upload_size_mb * 1024 * 1024  # Convert MB to bytes
    
    def check_file_size(self, file_content: bytes) -> bool:
        """
        Validates file size is under 50MB
        Returns: True if valid, False otherwise
        """
        return len(file_content) <= self.MAX_FILE_SIZE_BYTES
    
    def validate_csv(self, file_content: bytes) -> ValidationResult:
        """
        Validates CSV schema and data types
        Returns: ValidationResult with errors or success
        """
        errors = []
        warnings = []
        
        # Check file size first
        if not self.check_file_size(file_content):
            errors.append(f"File size exceeds {settings.max_upload_size_mb}MB limit")
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings)
        
        try:
            # Try to read CSV
            df = pd.read_csv(BytesIO(file_content))
        except Exception as e:
            errors.append(f"Failed to parse CSV file: {str(e)}")
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings)
        
        # Check for required columns
        missing_columns = [col for col in self.REQUIRED_COLUMNS if col not in df.columns]
        if missing_columns:
            errors.append(f"Missing required columns: {', '.join(missing_columns)}")
        
        # Check for empty dataframe
        if df.empty:
            errors.append("CSV file contains no data rows")
        
        if errors:
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings)
        
        # Validate data types for each column
        # Check date column
        try:
            pd.to_datetime(df['date'])
        except Exception as e:
            errors.append(f"Column 'date' contains invalid date values: {str(e)}")
        
        # Check integer columns
        for col in ['admissions', 'beds_occupied', 'staff_on_duty']:
            if col in df.columns:
                # Check if values can be converted to integers
                try:
                    int_values = pd.to_numeric(df[col], errors='coerce')
                    invalid_rows = df[int_values.isna()].index.tolist()
                    if invalid_rows:
                        errors.append(f"Column '{col}' contains non-integer values at rows {invalid_rows}")
                    # Check for negative values
                    elif (int_values < 0).any():
                        negative_rows = df[int_values < 0].index.tolist()
                        warnings.append(f"Column '{col}' contains negative values at rows {negative_rows}")
                except Exception as e:
                    errors.append(f"Column '{col}' validation failed: {str(e)}")
        
        # Check boolean column
        if 'overload_flag' in df.columns:
            # Accept various boolean representations
            valid_bool_values = {True, False, 'true', 'false', 'True', 'False', 'TRUE', 'FALSE', 
                                '1', '0', 1, 0, 1.0, 0.0}
            invalid_bool_rows = []
            for idx, val in enumerate(df['overload_flag']):
                if val not in valid_bool_values:
                    invalid_bool_rows.append(idx)
            if invalid_bool_rows:
                errors.append(f"Column 'overload_flag' contains invalid boolean values at rows {invalid_bool_rows}")
        
        # Check for duplicate dates
        if 'date' in df.columns:
            try:
                date_series = pd.to_datetime(df['date'])
                duplicates = date_series[date_series.duplicated()].unique()
                if len(duplicates) > 0:
                    warnings.append(f"Duplicate date entries found: {len(duplicates)} dates. Most recent entries will be used.")
            except:
                pass  # Already caught in date validation above
        
        is_valid = len(errors) == 0
        return ValidationResult(is_valid=is_valid, errors=errors, warnings=warnings)
    
    def parse_csv(self, file_content: bytes) -> List[HospitalRecord]:
        """
        Parses CSV into structured records
        Returns: List of HospitalRecord objects
        """
        df = pd.read_csv(BytesIO(file_content))
        
        # Convert date column to datetime
        df['date'] = pd.to_datetime(df['date'])
        
        # Convert numeric columns
        df['admissions'] = pd.to_numeric(df['admissions'], errors='coerce').fillna(0).astype(int)
        df['beds_occupied'] = pd.to_numeric(df['beds_occupied'], errors='coerce').fillna(0).astype(int)
        df['staff_on_duty'] = pd.to_numeric(df['staff_on_duty'], errors='coerce').fillna(0).astype(int)
        
        # Convert boolean column
        df['overload_flag'] = df['overload_flag'].map({
            True: True, False: False,
            'true': True, 'false': False,
            'True': True, 'False': False,
            'TRUE': True, 'FALSE': False,
            '1': True, '0': False,
            1: True, 0: False,
            1.0: True, 0.0: False
        }).fillna(False)
        
        # Handle duplicate dates - keep most recent (last occurrence)
        df = df.drop_duplicates(subset=['date'], keep='last')
        
        # Sort by date
        df = df.sort_values('date')
        
        # Convert to HospitalRecord objects
        records = []
        for _, row in df.iterrows():
            record = HospitalRecord(
                date=row['date'].to_pydatetime(),
                admissions=int(row['admissions']),
                beds_occupied=int(row['beds_occupied']),
                staff_on_duty=int(row['staff_on_duty']),
                overload_flag=bool(row['overload_flag'])
            )
            records.append(record)
        
        return records
    
    def store_records(self, records: List[HospitalRecord], bq_client=None, prediction_engine=None) -> dict:
        """
        Stores records in BigQuery, handling duplicates
        Invalidates prediction cache after successful storage
        Returns: Dictionary with count and warnings
        """
        if not records:
            return {'count': 0, 'warnings': ['No records to store']}
        
        # Import here to avoid module-level instantiation
        if bq_client is None:
            from ..db.bigquery_client import bigquery_client
            bq_client = bigquery_client
        
        # Convert records to BigQuery-compatible format
        rows = []
        for record in records:
            row = {
                'date': record.date.strftime('%Y-%m-%d'),
                'admissions': record.admissions,
                'beds_occupied': record.beds_occupied,
                'staff_on_duty': record.staff_on_duty,
                'overload_flag': record.overload_flag,
                'uploaded_at': datetime.utcnow().isoformat()
            }
            rows.append(row)
        
        # Insert into BigQuery
        success = bq_client.insert_rows('logs', rows)
        
        if success:
            # Invalidate prediction cache since new data was uploaded
            if prediction_engine is None:
                from .prediction_engine import PredictionEngine
                prediction_engine = PredictionEngine()
            
            prediction_engine.invalidate_cache()
            
            return {'count': len(rows), 'warnings': []}
        else:
            raise Exception("Failed to insert rows into BigQuery")
