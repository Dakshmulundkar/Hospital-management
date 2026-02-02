"""Property-based tests for upload handler
Feature: hospital-stress-warning
"""
import pytest
from hypothesis import given, settings, strategies as st
from datetime import datetime, timedelta
from app.services.upload_handler import UploadHandler
from app.models import HospitalRecord
import io


# Custom strategies for generating test data
@st.composite
def invalid_csv_strategy(draw):
    """Generate invalid CSV files with various issues"""
    issue_type = draw(st.sampled_from([
        'missing_column',
        'invalid_date',
        'invalid_integer',
        'invalid_boolean',
        'empty_file',
        'no_data_rows'
    ]))
    
    if issue_type == 'missing_column':
        # Missing required column
        missing_col = draw(st.sampled_from(['date', 'admissions', 'beds_occupied', 'staff_on_duty', 'overload_flag']))
        columns = ['date', 'admissions', 'beds_occupied', 'staff_on_duty', 'overload_flag']
        columns.remove(missing_col)
        
        csv_content = ','.join(columns) + '\n'
        csv_content += '2024-01-01,10,20,5,true\n'
        return csv_content.encode('utf-8')
    
    elif issue_type == 'invalid_date':
        # Invalid date format
        csv_content = 'date,admissions,beds_occupied,staff_on_duty,overload_flag\n'
        csv_content += 'not-a-date,10,20,5,true\n'
        return csv_content.encode('utf-8')
    
    elif issue_type == 'invalid_integer':
        # Invalid integer value
        invalid_col = draw(st.sampled_from(['admissions', 'beds_occupied', 'staff_on_duty']))
        csv_content = 'date,admissions,beds_occupied,staff_on_duty,overload_flag\n'
        
        if invalid_col == 'admissions':
            csv_content += '2024-01-01,not-a-number,20,5,true\n'
        elif invalid_col == 'beds_occupied':
            csv_content += '2024-01-01,10,not-a-number,5,true\n'
        else:
            csv_content += '2024-01-01,10,20,not-a-number,true\n'
        
        return csv_content.encode('utf-8')
    
    elif issue_type == 'invalid_boolean':
        # Invalid boolean value
        csv_content = 'date,admissions,beds_occupied,staff_on_duty,overload_flag\n'
        csv_content += '2024-01-01,10,20,5,not-a-boolean\n'
        return csv_content.encode('utf-8')
    
    elif issue_type == 'empty_file':
        # Empty file
        return b''
    
    else:  # no_data_rows
        # Header only, no data
        csv_content = 'date,admissions,beds_occupied,staff_on_duty,overload_flag\n'
        return csv_content.encode('utf-8')


@st.composite
def csv_with_duplicates_strategy(draw):
    """Generate CSV files with duplicate date entries"""
    base_date = datetime(2024, 1, 1)
    num_records = draw(st.integers(min_value=5, max_value=20))
    
    # Generate records
    records = []
    for i in range(num_records):
        date = base_date + timedelta(days=i)
        records.append({
            'date': date.strftime('%Y-%m-%d'),
            'admissions': draw(st.integers(min_value=0, max_value=100)),
            'beds_occupied': draw(st.integers(min_value=0, max_value=100)),
            'staff_on_duty': draw(st.integers(min_value=1, max_value=20)),
            'overload_flag': draw(st.booleans())
        })
    
    # Introduce duplicates - pick 2-5 random dates to duplicate
    num_duplicates = draw(st.integers(min_value=2, max_value=min(5, num_records)))
    duplicate_indices = draw(st.lists(
        st.integers(min_value=0, max_value=num_records-1),
        min_size=num_duplicates,
        max_size=num_duplicates,
        unique=True
    ))
    
    # Create duplicates with different values
    for idx in duplicate_indices:
        duplicate_record = records[idx].copy()
        duplicate_record['admissions'] = draw(st.integers(min_value=0, max_value=100))
        duplicate_record['beds_occupied'] = draw(st.integers(min_value=0, max_value=100))
        records.append(duplicate_record)
    
    # Convert to CSV
    csv_content = 'date,admissions,beds_occupied,staff_on_duty,overload_flag\n'
    for record in records:
        csv_content += f"{record['date']},{record['admissions']},{record['beds_occupied']},{record['staff_on_duty']},{str(record['overload_flag']).lower()}\n"
    
    return csv_content.encode('utf-8'), duplicate_indices


@settings(max_examples=100)
@given(invalid_csv=invalid_csv_strategy())
def test_property_2_invalid_csv_rejection(invalid_csv):
    """
    Feature: hospital-stress-warning, Property 2: Invalid CSV Rejection
    
    For any CSV file with invalid data types or missing required columns,
    the Upload_Handler should reject the upload and return a descriptive error message.
    
    Validates: Requirements 1.2
    """
    handler = UploadHandler()
    
    # Validate the invalid CSV
    result = handler.validate_csv(invalid_csv)
    
    # Should be marked as invalid
    assert not result.is_valid, "Invalid CSV was incorrectly marked as valid"
    
    # Should have at least one error message
    assert len(result.errors) > 0, "No error messages provided for invalid CSV"
    
    # Error messages should be descriptive (non-empty strings)
    for error in result.errors:
        assert isinstance(error, str), "Error message is not a string"
        assert len(error) > 0, "Error message is empty"
    
    # Verify result structure is valid
    assert result.validate(), "ValidationResult structure is invalid"


@settings(max_examples=100)
@given(csv_data=csv_with_duplicates_strategy())
def test_property_3_duplicate_date_deduplication(csv_data):
    """
    Feature: hospital-stress-warning, Property 3: Duplicate Date Deduplication
    
    For any CSV file containing duplicate date entries, the Upload_Handler should
    store only the most recent entry for each date and log a warning.
    
    Validates: Requirements 1.4
    """
    csv_content, duplicate_indices = csv_data
    handler = UploadHandler()
    
    # Validate CSV - should succeed with warnings
    validation_result = handler.validate_csv(csv_content)
    
    # Should be valid (duplicates are a warning, not an error)
    assert validation_result.is_valid, f"CSV with duplicates should be valid, got errors: {validation_result.errors}"
    
    # Should have a warning about duplicates
    assert len(validation_result.warnings) > 0, "No warning provided for duplicate dates"
    
    # Check that warning mentions duplicates
    has_duplicate_warning = any('duplicate' in warning.lower() for warning in validation_result.warnings)
    assert has_duplicate_warning, f"Warning should mention duplicates, got: {validation_result.warnings}"
    
    # Parse the CSV
    records = handler.parse_csv(csv_content)
    
    # Check that dates are unique in the result
    dates = [record.date.date() for record in records]
    unique_dates = set(dates)
    assert len(dates) == len(unique_dates), "Duplicate dates were not removed during parsing"
    
    # Verify all records are valid
    for record in records:
        assert record.validate(), f"Parsed record failed validation: {record}"
