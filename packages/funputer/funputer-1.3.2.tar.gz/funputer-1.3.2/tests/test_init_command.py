"""
Tests for the new init command functionality.
"""

import pytest
import os
import tempfile
import csv
import pandas as pd
from click.testing import CliRunner
from unittest.mock import patch

from funimpute.simple_cli import cli
from funimpute.metadata_inference import infer_metadata_from_dataframe


class TestInitCommand:
    """Test the init command functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
    
    def create_sample_data_file(self, temp_dir, filename='test_data.csv'):
        """Create a sample data file for testing init command."""
        data_content = """customer_id,age,income,category,is_active,registration_date,rating,notes
1001,25,50000.50,Premium,TRUE,2023-01-15,4.2,Good customer
1002,34,,Standard,FALSE,2023-02-20,3.8,Needs follow-up
1003,,89000.25,Premium,TRUE,,4.5,
1004,42,78000.00,Basic,TRUE,2023-01-08,,VIP
1005,28,52000.75,,FALSE,2023-03-10,3.9,Regular customer
1006,35,,Standard,TRUE,2023-01-25,4.1,
1007,,95000.50,Premium,TRUE,2023-02-14,4.7,New signup
1008,39,125000.00,Basic,FALSE,2023-03-05,,Loyal customer"""
        
        data_path = os.path.join(temp_dir, filename)
        with open(data_path, 'w') as f:
            f.write(data_content)
        return data_path
    
    def test_init_basic_execution(self):
        """Test basic init command execution."""
        temp_dir = tempfile.mkdtemp()
        
        try:
            data_path = self.create_sample_data_file(temp_dir)
            
            with self.runner.isolated_filesystem():
                result = self.runner.invoke(cli, [
                    'init',
                    '-d', data_path
                ])
                
                assert result.exit_code == 0
                assert '✅ Metadata template created: metadata.csv' in result.output
                assert '📊 Analyzed 8 columns' in result.output
                assert 'Next steps:' in result.output
                assert 'funimputer analyze -m metadata.csv' in result.output
                
                # Check that metadata.csv was created
                assert os.path.exists('metadata.csv')
                
                # Verify CSV structure
                with open('metadata.csv', 'r') as f:
                    reader = csv.DictReader(f)
                    rows = list(reader)
                    
                    assert len(rows) == 8  # 8 columns
                    
                    # Check required headers
                    expected_headers = ['column_name', 'data_type', 'min_value', 'max_value', 
                                      'max_length', 'unique_flag', 'nullable', 'allowed_values', 
                                      'dependent_column', 'dependency_rule', 'business_rule', 'description']
                    assert set(reader.fieldnames) == set(expected_headers)
                    
                    # Check some specific inferences
                    column_types = {row['column_name']: row['data_type'] for row in rows}
                    assert column_types['customer_id'] == 'integer'
                    assert column_types['age'] == 'integer'
                    assert column_types['income'] == 'float'
                    assert column_types['category'] == 'categorical'
                    assert column_types['is_active'] == 'boolean'
                    assert column_types['registration_date'] == 'datetime'
                    assert column_types['rating'] == 'float'
                    
        finally:
            import shutil
            shutil.rmtree(temp_dir)
    
    def test_init_with_custom_output(self):
        """Test init command with custom output file."""
        temp_dir = tempfile.mkdtemp()
        
        try:
            data_path = self.create_sample_data_file(temp_dir)
            
            with self.runner.isolated_filesystem():
                result = self.runner.invoke(cli, [
                    'init',
                    '-d', data_path,
                    '-o', 'custom_metadata.csv'
                ])
                
                assert result.exit_code == 0
                assert '✅ Metadata template created: custom_metadata.csv' in result.output
                assert os.path.exists('custom_metadata.csv')
                assert not os.path.exists('metadata.csv')  # Default shouldn't exist
                
        finally:
            import shutil
            shutil.rmtree(temp_dir)
    
    def test_init_verbose_mode(self):
        """Test init command with verbose output."""
        temp_dir = tempfile.mkdtemp()
        
        try:
            data_path = self.create_sample_data_file(temp_dir)
            
            with self.runner.isolated_filesystem():
                result = self.runner.invoke(cli, [
                    'init',
                    '-d', data_path,
                    '--verbose'
                ])
                
                assert result.exit_code == 0
                assert 'INFO: Analyzing data file:' in result.output
                assert 'INFO: Loaded 8 rows and 8 columns' in result.output
                assert 'INFO: Inferring metadata and data types...' in result.output
                assert 'INFO: Writing metadata template to:' in result.output
                assert '🔍 Column summary:' in result.output
                assert 'customer_id: integer' in result.output
                
        finally:
            import shutil
            shutil.rmtree(temp_dir)
    
    def test_init_file_not_found(self):
        """Test init command with non-existent data file."""
        result = self.runner.invoke(cli, [
            'init',
            '-d', 'nonexistent_file.csv'
        ])
        
        assert result.exit_code == 1
        assert '❌ Error: Data file not found: nonexistent_file.csv' in result.output
    
    def test_init_with_minimal_data(self):
        """Test init command with minimal data (edge case)."""
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Create minimal data file
            minimal_data = "id\n1\n2\n3"
            data_path = os.path.join(temp_dir, 'minimal.csv')
            with open(data_path, 'w') as f:
                f.write(minimal_data)
            
            with self.runner.isolated_filesystem():
                result = self.runner.invoke(cli, [
                    'init',
                    '-d', data_path
                ])
                
                assert result.exit_code == 0
                assert '📊 Analyzed 1 columns' in result.output
                assert os.path.exists('metadata.csv')
                
                # Verify the single column was processed
                with open('metadata.csv', 'r') as f:
                    reader = csv.DictReader(f)
                    rows = list(reader)
                    assert len(rows) == 1
                    assert rows[0]['column_name'] == 'id'
                    assert rows[0]['data_type'] == 'integer'
                
        finally:
            import shutil
            shutil.rmtree(temp_dir)
    
    def test_init_with_all_missing_data(self):
        """Test init command with data containing all missing values."""
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Create data with all missing values
            missing_data = "col1,col2,col3\n,,\n,,\n,,"
            data_path = os.path.join(temp_dir, 'missing.csv')
            with open(data_path, 'w') as f:
                f.write(missing_data)
            
            with self.runner.isolated_filesystem():
                result = self.runner.invoke(cli, [
                    'init',
                    '-d', data_path
                ])
                
                # Should still work, might infer as string/categorical
                assert result.exit_code == 0
                assert '📊 Analyzed 3 columns' in result.output
                
        finally:
            import shutil
            shutil.rmtree(temp_dir)
    
    def test_init_help_output(self):
        """Test init command help output."""
        result = self.runner.invoke(cli, ['init', '--help'])
        
        assert result.exit_code == 0
        assert 'Generate a metadata template CSV by analyzing your data file' in result.output
        assert '--data' in result.output
        assert '--output' in result.output
        assert '--verbose' in result.output
        assert 'Examples:' in result.output
        assert 'funimputer init -d data.csv' in result.output
    
    def test_init_integration_with_analyze(self):
        """Test that init-generated metadata works with analyze command."""
        temp_dir = tempfile.mkdtemp()
        
        try:
            data_path = self.create_sample_data_file(temp_dir)
            
            with self.runner.isolated_filesystem():
                # Step 1: Generate metadata template
                init_result = self.runner.invoke(cli, [
                    'init',
                    '-d', data_path
                ])
                assert init_result.exit_code == 0
                assert os.path.exists('metadata.csv')
                
                # Step 2: Use generated metadata with analyze command
                analyze_result = self.runner.invoke(cli, [
                    'analyze',
                    '-m', 'metadata.csv',
                    '-d', data_path
                ])
                
                assert analyze_result.exit_code == 0
                assert '✓ Analysis complete!' in analyze_result.output
                assert os.path.exists('suggestions.csv')
                
        finally:
            import shutil
            shutil.rmtree(temp_dir)
    
    def test_init_error_handling_with_corrupted_csv(self):
        """Test init command error handling with corrupted CSV."""
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Create corrupted CSV file
            corrupted_data = "col1,col2\n\"unclosed quote,value\nmore,data"
            data_path = os.path.join(temp_dir, 'corrupted.csv')
            with open(data_path, 'w') as f:
                f.write(corrupted_data)
            
            with self.runner.isolated_filesystem():
                result = self.runner.invoke(cli, [
                    'init',
                    '-d', data_path
                ])
                
                # Should handle the error gracefully
                assert result.exit_code == 1
                assert '❌ Error generating metadata template:' in result.output
                
        finally:
            import shutil
            shutil.rmtree(temp_dir)
    
    def test_init_with_permission_error(self):
        """Test init command handling of permission errors."""
        temp_dir = tempfile.mkdtemp()
        
        try:
            data_path = self.create_sample_data_file(temp_dir)
            
            with self.runner.isolated_filesystem():
                # Mock a permission error when writing output
                with patch('builtins.open', side_effect=PermissionError("Permission denied")):
                    result = self.runner.invoke(cli, [
                        'init',
                        '-d', data_path
                    ])
                    
                    assert result.exit_code == 1
                    assert '❌ Error generating metadata template:' in result.output
                    
        finally:
            import shutil
            shutil.rmtree(temp_dir)
    
    def test_init_metadata_content_validation(self):
        """Test that generated metadata contains expected content and structure."""
        temp_dir = tempfile.mkdtemp()
        
        try:
            data_path = self.create_sample_data_file(temp_dir)
            
            with self.runner.isolated_filesystem():
                result = self.runner.invoke(cli, [
                    'init',
                    '-d', data_path
                ])
                
                assert result.exit_code == 0
                
                # Read and validate the generated metadata
                with open('metadata.csv', 'r') as f:
                    reader = csv.DictReader(f)
                    rows = list(reader)
                
                # Find specific columns and validate their metadata
                customer_id_row = next(row for row in rows if row['column_name'] == 'customer_id')
                assert customer_id_row['data_type'] == 'integer'
                assert customer_id_row['unique_flag'] == 'TRUE'  # Should detect as unique
                assert customer_id_row['min_value'] == '1001.0'
                assert customer_id_row['max_value'] == '1008.0'
                
                income_row = next(row for row in rows if row['column_name'] == 'income')
                assert income_row['data_type'] == 'float'
                assert income_row['unique_flag'] == 'FALSE'
                assert float(income_row['min_value']) > 0
                
                # Check that placeholders are empty (ready for user customization)
                for row in rows:
                    # Still placeholder fields (require manual input)
                    assert row['dependency_rule'] == ''
                    assert row['business_rule'] == ''
                    
                    # Enhanced: allowed_values now auto-inferred for categorical data
                    if row['data_type'] == 'categorical':
                        assert row['allowed_values'] != ''  # Should be auto-inferred for categorical
                    
                    # nullable should have default value, not be empty
                    assert row['nullable'] in ['TRUE', 'FALSE']  # Should have inferred default value
                    # Description should contain auto-inferred info
                    assert 'Auto-inferred' in row['description']
                
        finally:
            import shutil
            shutil.rmtree(temp_dir)


class TestInitCommandEdgeCases:
    """Test edge cases for the init command."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
    
    def test_init_with_unicode_data(self):
        """Test init command with Unicode characters in data."""
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Create data with Unicode characters
            unicode_data = """name,description,price
José,Café especial,€15.50
María,Niño pequeño,¥1000
François,Crème brûlée,£8.75"""
            
            data_path = os.path.join(temp_dir, 'unicode.csv')
            with open(data_path, 'w', encoding='utf-8') as f:
                f.write(unicode_data)
            
            with self.runner.isolated_filesystem():
                result = self.runner.invoke(cli, [
                    'init',
                    '-d', data_path
                ])
                
                assert result.exit_code == 0
                assert os.path.exists('metadata.csv')
                
        finally:
            import shutil
            shutil.rmtree(temp_dir)
    
    def test_init_with_large_dataset(self):
        """Test init command with larger dataset."""
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Create a larger dataset
            import pandas as pd
            large_df = pd.DataFrame({
                'id': range(1000),
                'value': [i * 1.5 for i in range(1000)],
                'category': (['A', 'B', 'C'] * 334)[:1000],  # Ensure exactly 1000 items
                'flag': ([True, False] * 500)[:1000]  # Ensure exactly 1000 items
            })
            
            data_path = os.path.join(temp_dir, 'large.csv')
            large_df.to_csv(data_path, index=False)
            
            with self.runner.isolated_filesystem():
                result = self.runner.invoke(cli, [
                    'init',
                    '-d', data_path
                ])
                
                assert result.exit_code == 0
                assert '📊 Analyzed 4 columns' in result.output
                
        finally:
            import shutil
            shutil.rmtree(temp_dir)


if __name__ == '__main__':
    pytest.main([__file__])
