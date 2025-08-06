#!/usr/bin/env python3
"""
Comprehensive test suite for PREFLIGHT system.
"""

import pytest
import tempfile
import json
import os
import gzip
import zipfile
from pathlib import Path
from click.testing import CliRunner
from unittest.mock import patch

from funimpute.preflight import (
    run_preflight, 
    format_preflight_report,
    _check_path_and_size,
    _detect_format_and_compression,
    _probe_encoding
)
from funimpute.simple_cli import cli


class TestPreflightBasics:
    """Test basic preflight functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def create_test_csv(self, content: str, filename: str = "test.csv") -> str:
        """Create a temporary CSV file with given content."""
        filepath = os.path.join(self.temp_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return filepath

    def test_file_exists_and_readable(self):
        """Test valid file detection."""
        content = "name,age\nAlice,25\nBob,30"
        filepath = self.create_test_csv(content)
        result = _check_path_and_size(filepath)
        
        assert result["error"] is None
        assert result["size_bytes"] > 0
        assert "test.csv" in result["path"]

    def test_file_not_found(self):
        """Test non-existent file handling."""
        result = _check_path_and_size("/nonexistent/file.csv")
        assert "File not found" in result["error"]

    def test_empty_file(self):
        """Test empty file detection."""
        filepath = self.create_test_csv("")
        result = _check_path_and_size(filepath)
        assert "Empty file" in result["error"]

    def test_csv_format_detection(self):
        """Test CSV format detection."""
        content = "name,age\nAlice,25"
        filepath = self.create_test_csv(content, "data.csv")
        result = _detect_format_and_compression(filepath, 1024)
        
        assert result["format"] == "csv"
        assert result["compression"] == "none"

    def test_encoding_detection(self):
        """Test UTF-8 encoding detection."""
        content = "name,age\nAlice,25\nBob,30"
        filepath = self.create_test_csv(content)
        result = _probe_encoding(filepath)
        
        assert result["selected"] == "utf-8"
        assert "utf-8" in result["tried"]

    def test_successful_preflight_run(self):
        """Test complete successful preflight run."""
        content = "name,age,active\nAlice,25,true\nBob,30,false\nCharlie,,true"
        filepath = self.create_test_csv(content)
        
        report = run_preflight(filepath, sample_rows=100)
        
        assert report["status"] in ["ok", "ok_with_warnings"]
        assert report["file"]["error"] is None
        assert report["file"]["format"] == "csv"
        assert report["structure"]["num_columns"] == 3
        assert len(report["columns"]) == 3
        assert report["recommendation"] in ["analyze_infer_only", "generate_metadata"]

    def test_preflight_nonexistent_file(self):
        """Test preflight with non-existent file."""
        report = run_preflight("/nonexistent/file.csv")
        
        assert report["status"] == "hard_error"
        assert "not found" in report["file"]["error"].lower()

    def test_preflight_report_formatting(self):
        """Test preflight report formatting."""
        content = "name,age\nAlice,25"
        filepath = self.create_test_csv(content)
        
        report = run_preflight(filepath)
        formatted = format_preflight_report(report)
        
        assert "PREFLIGHT REPORT" in formatted
        assert "Status:" in formatted
        assert "File:" in formatted
        assert "Recommendation:" in formatted

    def test_preflight_command_basic(self):
        """Test basic preflight CLI command."""
        content = "name,age\nAlice,25\nBob,30"
        filepath = self.create_test_csv(content)
        
        result = self.runner.invoke(cli, ["preflight", "-d", filepath])
        
        assert result.exit_code in [0, 2]  # OK or OK with warnings
        assert "PREFLIGHT REPORT" in result.output
        assert "Status:" in result.output

    def test_preflight_command_hard_error(self):
        """Test preflight CLI with hard error."""
        result = self.runner.invoke(cli, ["preflight", "-d", "/nonexistent/file.csv"])
        
        assert result.exit_code == 10  # Hard error
        assert "HARD_ERROR" in result.output

    def test_preflight_advisory_mode(self):
        """Test preflight running in advisory mode before init."""
        content = "name,age\nAlice,25"
        filepath = self.create_test_csv(content)
        output_path = os.path.join(self.temp_dir, "metadata.csv")
        
        result = self.runner.invoke(cli, ["init", "-d", filepath, "-o", output_path])
        
        # Should run preflight first, then succeed
        assert result.exit_code == 0
        assert "Preflight Check" in result.output
        assert "Metadata template created" in result.output
        assert os.path.exists(output_path)

    def test_empty_csv_handling(self):
        """Test handling of empty CSV files."""
        filepath = os.path.join(self.temp_dir, "empty.csv")
        Path(filepath).touch()  # Create empty file
        
        report = run_preflight(filepath)
        
        assert report["status"] == "hard_error"
        assert "empty file" in report["file"]["error"].lower()

    def test_gzipped_csv_detection(self):
        """Test gzipped CSV detection."""
        csv_content = "name,age\nAlice,25\nBob,30"
        filepath = os.path.join(self.temp_dir, "test.csv.gz")
        
        with gzip.open(filepath, 'wt', encoding='utf-8') as f:
            f.write(csv_content)
            
        result = _detect_format_and_compression(filepath, 1024)
        
        assert result["format"] == "csv"
        assert result["compression"] == "gz"

    def test_unicode_content(self):
        """Test with Unicode content."""
        content = "name,description\nAlice,Café ☕\nBob,Résumé 📄\nCharlie,数据 🔢"
        filepath = self.create_test_csv(content)
        
        report = run_preflight(filepath)
        
        assert report["status"] in ["ok", "ok_with_warnings"]
        assert report["encoding"]["selected"] == "utf-8"


if __name__ == "__main__":
    pytest.main([__file__])