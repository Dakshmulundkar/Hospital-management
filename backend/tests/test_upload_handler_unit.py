"""Unit tests for upload handler
Feature: hospital-stress-warning
"""
import pytest
from app.services.upload_handler import UploadHandler
from app.config import settings


class TestFileSizeValidation:
    """Unit tests for file size validation"""
    
    def test_file_size_49mb_accepted(self):
        """Test that files at 49MB are accepted"""
        handler = UploadHandler()
        
        # Create a file that's 49MB (just under the limit)
        file_size = 49 * 1024 * 1024  # 49MB in bytes
        file_content = b'a' * file_size
        
        # Should pass size check
        assert handler.check_file_size(file_content) is True
    
    def test_file_size_50mb_accepted(self):
        """Test that files at exactly 50MB are accepted"""
        handler = UploadHandler()
        
        # Create a file that's exactly 50MB (at the limit)
        file_size = 50 * 1024 * 1024  # 50MB in bytes
        file_content = b'a' * file_size
        
        # Should pass size check
        assert handler.check_file_size(file_content) is True
    
    def test_file_size_51mb_rejected(self):
        """Test that files at 51MB are rejected"""
        handler = UploadHandler()
        
        # Create a file that's 51MB (over the limit)
        file_size = 51 * 1024 * 1024  # 51MB in bytes
        file_content = b'a' * file_size
        
        # Should fail size check
        assert handler.check_file_size(file_content) is False
    
    def test_validate_csv_rejects_oversized_file(self):
        """Test that validate_csv rejects files over 50MB"""
        handler = UploadHandler()
        
        # Create a file that's 51MB (over the limit)
        file_size = 51 * 1024 * 1024  # 51MB in bytes
        file_content = b'a' * file_size
        
        # Validate should fail
        result = handler.validate_csv(file_content)
        
        assert result.is_valid is False
        assert len(result.errors) > 0
        assert any('50MB' in error or 'size' in error.lower() for error in result.errors)
    
    def test_validate_csv_accepts_valid_sized_file(self):
        """Test that validate_csv accepts files under 50MB with valid content"""
        handler = UploadHandler()
        
        # Create a valid CSV file under 50MB
        csv_content = 'date,admissions,beds_occupied,staff_on_duty,overload_flag\n'
        csv_content += '2024-01-01,10,20,5,true\n'
        csv_content += '2024-01-02,15,25,6,false\n'
        file_content = csv_content.encode('utf-8')
        
        # Validate should pass
        result = handler.validate_csv(file_content)
        
        assert result.is_valid is True
        assert len(result.errors) == 0


class TestCSVParsing:
    """Unit tests for CSV parsing functionality"""
    
    def test_parse_valid_csv(self):
        """Test parsing a valid CSV file"""
        handler = UploadHandler()
        
        csv_content = 'date,admissions,beds_occupied,staff_on_duty,overload_flag\n'
        csv_content += '2024-01-01,10,20,5,true\n'
        csv_content += '2024-01-02,15,25,6,false\n'
        file_content = csv_content.encode('utf-8')
        
        records = handler.parse_csv(file_content)
        
        assert len(records) == 2
        assert records[0].admissions == 10
        assert records[0].beds_occupied == 20
        assert records[0].staff_on_duty == 5
        assert records[0].overload_flag is True
        
        assert records[1].admissions == 15
        assert records[1].beds_occupied == 25
        assert records[1].staff_on_duty == 6
        assert records[1].overload_flag is False
    
    def test_parse_csv_with_duplicates_keeps_last(self):
        """Test that duplicate dates keep the last entry"""
        handler = UploadHandler()
        
        csv_content = 'date,admissions,beds_occupied,staff_on_duty,overload_flag\n'
        csv_content += '2024-01-01,10,20,5,true\n'
        csv_content += '2024-01-01,99,88,7,false\n'  # Duplicate date, different values
        csv_content += '2024-01-02,15,25,6,false\n'
        file_content = csv_content.encode('utf-8')
        
        records = handler.parse_csv(file_content)
        
        # Should only have 2 records (duplicate removed)
        assert len(records) == 2
        
        # First record should have the values from the LAST occurrence
        assert records[0].date.strftime('%Y-%m-%d') == '2024-01-01'
        assert records[0].admissions == 99
        assert records[0].beds_occupied == 88
        assert records[0].staff_on_duty == 7
        assert records[0].overload_flag is False
    
    def test_validate_csv_with_missing_column(self):
        """Test validation fails when required column is missing"""
        handler = UploadHandler()
        
        # Missing 'admissions' column
        csv_content = 'date,beds_occupied,staff_on_duty,overload_flag\n'
        csv_content += '2024-01-01,20,5,true\n'
        file_content = csv_content.encode('utf-8')
        
        result = handler.validate_csv(file_content)
        
        assert result.is_valid is False
        assert any('admissions' in error.lower() for error in result.errors)
    
    def test_validate_csv_with_invalid_date(self):
        """Test validation fails with invalid date format"""
        handler = UploadHandler()
        
        csv_content = 'date,admissions,beds_occupied,staff_on_duty,overload_flag\n'
        csv_content += 'not-a-date,10,20,5,true\n'
        file_content = csv_content.encode('utf-8')
        
        result = handler.validate_csv(file_content)
        
        assert result.is_valid is False
        assert any('date' in error.lower() for error in result.errors)
    
    def test_validate_csv_with_invalid_integer(self):
        """Test validation fails with non-integer values"""
        handler = UploadHandler()
        
        csv_content = 'date,admissions,beds_occupied,staff_on_duty,overload_flag\n'
        csv_content += '2024-01-01,not-a-number,20,5,true\n'
        file_content = csv_content.encode('utf-8')
        
        result = handler.validate_csv(file_content)
        
        assert result.is_valid is False
        assert any('admissions' in error.lower() for error in result.errors)
    
    def test_validate_csv_with_negative_values_warning(self):
        """Test that negative values generate warnings"""
        handler = UploadHandler()
        
        csv_content = 'date,admissions,beds_occupied,staff_on_duty,overload_flag\n'
        csv_content += '2024-01-01,-10,20,5,true\n'
        file_content = csv_content.encode('utf-8')
        
        result = handler.validate_csv(file_content)
        
        # Should be valid but with warnings
        assert result.is_valid is True
        assert len(result.warnings) > 0
        assert any('negative' in warning.lower() for warning in result.warnings)
