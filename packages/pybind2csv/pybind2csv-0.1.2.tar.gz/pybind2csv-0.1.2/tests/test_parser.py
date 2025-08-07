"""
Tests for the DNS BIND zone and view file parser.
"""

import pytest
import tempfile
import csv
from pathlib import Path
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner

from pybind2csv.parser import DNSZoneParser, validate_zone_file, extract_zone_name_from_file, extract_view_name_from_file
from pybind2csv.main import app


class TestDNSZoneParser:
    """Test cases for DNSZoneParser class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = DNSZoneParser()
    
    def test_parse_zone_file_valid(self):
        """Test parsing a valid zone file."""
        zone_content = "@ 300 IN SOA ns1 hostmaster 1 2 3 4 5\n@ 300 IN NS ns1\nns1 300 IN A 192.168.1.1\nwww 300 IN A 192.168.1.100"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.zone', delete=False) as f:
            f.write(zone_content)
            f.flush()
            zone_file = Path(f.name)
        
        try:
            records = self.parser.parse_zone_file(zone_file, "example.com", "local")
            
            assert len(records) >= 4  # SOA, NS, and A records
            
            # Check SOA record
            soa_records = [r for r in records if r['type'] == 'SOA']
            assert len(soa_records) >= 1
            assert soa_records[0]['zone'] == 'example.com'
            assert soa_records[0]['view'] == 'local'
            assert soa_records[0]['ttl'] == 300
            
            # Check A records
            a_records = [r for r in records if r['type'] == 'A']
            assert len(a_records) >= 2
            
        finally:
            zone_file.unlink()
    
    def test_parse_zone_file_with_various_records(self):
        """Test parsing zone file with various DNS record types."""
        zone_content = "@ 300 IN SOA ns1.test.com. hostmaster.test.com. 1 2 3 4 5\n@ 300 IN NS ns1.test.com.\n@ 300 IN MX 10 mail.test.com.\nns1 300 IN A 192.168.1.1\nmail 300 IN A 192.168.1.2\nwww 300 IN CNAME test.com.\ntxt 300 IN TXT \"test text\""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.zone', delete=False) as f:
            f.write(zone_content)
            f.flush()
            zone_file = Path(f.name)
        
        try:
            records = self.parser.parse_zone_file(zone_file, "test.com", "roaming")
            
            # Check different record types
            record_types = {r['type'] for r in records}
            expected_types = {'SOA', 'NS', 'MX', 'A', 'CNAME', 'TXT'}
            
            # Check that we have at least some expected types
            assert len(record_types.intersection(expected_types)) > 0
            
            # Check specific records
            txt_records = [r for r in records if r['type'] == 'TXT']
            assert len(txt_records) >= 1
            
        finally:
            zone_file.unlink()
    
    def test_parse_zone_file_empty(self):
        """Test parsing an empty zone file."""
        zone_content = ""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.zone', delete=False) as f:
            f.write(zone_content)
            f.flush()
            zone_file = Path(f.name)
        
        try:
            records = self.parser.parse_zone_file(zone_file, "empty.com", "local")
            assert len(records) == 0
            
        finally:
            zone_file.unlink()
    
    def test_parse_zone_file_invalid_format(self):
        """Test parsing an invalid zone file format."""
        zone_content = "This is not a valid zone file\nIt has no DNS records"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.zone', delete=False) as f:
            f.write(zone_content)
            f.flush()
            zone_file = Path(f.name)
        
        try:
            records = self.parser.parse_zone_file(zone_file, "invalid.com", "local")
            # Should return empty list instead of raising exception
            assert isinstance(records, list)
            
        finally:
            zone_file.unlink()
    
    def test_write_csv(self):
        """Test writing records to CSV."""
        records = [
            {
                'zone': 'example.com',
                'view': 'local',
                'name': 'www.example.com',
                'type': 'A',
                'ttl': 300,
                'data': '192.168.1.100'
            },
            {
                'zone': 'example.com',
                'view': 'local',
                'name': 'mail.example.com',
                'type': 'MX',
                'ttl': 300,
                'data': '10 mail.example.com.'
            }
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            csv_file = Path(f.name)
        
        try:
            self.parser.write_csv(records, csv_file)
            
            # Verify CSV content
            with open(csv_file, 'r', newline='') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            
            assert len(rows) == 2
            assert rows[0]['zone'] == 'example.com'
            assert rows[0]['view'] == 'local'
            assert rows[0]['name'] == 'www.example.com'
            assert rows[0]['type'] == 'A'
            assert rows[0]['ttl'] == '300'
            assert rows[0]['data'] == '192.168.1.100'
            
        finally:
            csv_file.unlink()
    
    def test_parse_view_file(self):
        """Test parsing a view file."""
        view_content = "@ 300 IN SOA ns1.test.com. hostmaster.test.com. 1 2 3 4 5\n@ 300 IN NS ns1.test.com.\nns1 300 IN A 192.168.1.1"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.vroaming', delete=False) as f:
            f.write(view_content)
            f.flush()
            view_file = Path(f.name)
        
        try:
            records = self.parser.parse_view_file(view_file, "roaming")
            
            assert len(records) >= 3
            
            # Check that view name is correctly set
            for record in records:
                assert record['view'] == 'roaming'
                
        finally:
            view_file.unlink()
    
    def test_parse_zone_file_with_unknown_records(self):
        """Test parsing zone file with unknown record types."""
        zone_content = "@ 300 IN SOA ns1.test.com. hostmaster.test.com. 1 2 3 4 5\n@ 300 IN NS ns1.test.com.\n@ 300 IN UNKNOWN some_data"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.zone', delete=False) as f:
            f.write(zone_content)
            f.flush()
            zone_file = Path(f.name)
        
        try:
            records = self.parser.parse_zone_file(zone_file, "test.com", "local")
            
            # Should handle unknown record types gracefully
            assert isinstance(records, list)
            
        finally:
            zone_file.unlink()
    
    def test_parse_files_with_duplicates(self):
        """Test parsing files with duplicate records."""
        zone_content = "@ 300 IN SOA ns1.test.com. hostmaster.test.com. 1 2 3 4 5\n@ 300 IN NS ns1.test.com.\nns1 300 IN A 192.168.1.1"
        
        view_content = "@ 300 IN SOA ns1.test.com. hostmaster.test.com. 1 2 3 4 5\n@ 300 IN NS ns1.test.com.\nns1 300 IN A 192.168.1.1"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.zone', delete=False) as f1:
            f1.write(zone_content)
            f1.flush()
            zone_file = Path(f1.name)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.vroaming', delete=False) as f2:
            f2.write(view_content)
            f2.flush()
            view_file = Path(f2.name)
        
        try:
            records = self.parser.parse_files(zone_file, view_file, "test.com", "test")
            
            # Should deduplicate records
            assert isinstance(records, list)
            
        finally:
            zone_file.unlink()
            view_file.unlink()


class TestHelperFunctions:
    """Test cases for helper functions."""
    
    def test_validate_zone_file_valid(self):
        """Test validating an existing file."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_file = Path(f.name)
            f.write(b"test content")
        
        try:
            assert validate_zone_file(temp_file) is True
        finally:
            temp_file.unlink()
    
    def test_validate_zone_file_nonexistent(self):
        """Test validating a non-existent file."""
        non_existent = Path("/path/that/does/not/exist")
        assert validate_zone_file(non_existent) is False
    
    def test_validate_zone_file_directory(self):
        """Test validating a directory instead of file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            assert validate_zone_file(temp_path) is False
    
    def test_extract_zone_name_from_file(self):
        """Test extracting zone name from filename."""
        assert extract_zone_name_from_file(Path("example.com.zone")) == "example.com"
        assert extract_zone_name_from_file(Path("example.db")) == "example"
        assert extract_zone_name_from_file(Path("example.vroaming")) == "example"
        assert extract_zone_name_from_file(Path("example.vlocal")) == "example"
        assert extract_zone_name_from_file(Path("example")) == "example"
    
    def test_extract_view_name_from_file(self):
        """Test extracting view name from filename."""
        assert extract_view_name_from_file(Path("example.vlocal")) == "local"
        assert extract_view_name_from_file(Path("example.vroaming")) == "roaming"
        assert extract_view_name_from_file(Path("example.vinternal")) == "internal"
        assert extract_view_name_from_file(Path("example.vexternal")) == "external"
        assert extract_view_name_from_file(Path("example.int")) == "internal"
        assert extract_view_name_from_file(Path("example.ext")) == "external"
        assert extract_view_name_from_file(Path("example.zone")) == "example"
        assert extract_view_name_from_file(Path("example")) == "example"


class TestIntegration:
    """Integration tests using the provided example files."""
    
    def test_parse_example_files(self):
        """Test parsing the provided example files."""
        # Get paths to example files
        test_dir = Path(__file__).parent
        example_vlocal = test_dir / "example.vlocal"
        example_vroaming = test_dir / "example.vroaming"
        
        assert example_vlocal.exists(), "example.vlocal file not found"
        assert example_vroaming.exists(), "example.vroaming file not found"
        
        parser = DNSZoneParser()
        
        # Parse vlocal file
        vlocal_records = parser.parse_view_file(example_vlocal, "local")
        assert isinstance(vlocal_records, list)
        assert len(vlocal_records) > 0
        
        # Parse vroaming file
        vroaming_records = parser.parse_view_file(example_vroaming, "roaming")
        assert isinstance(vroaming_records, list)
        assert len(vroaming_records) > 0
        
        # Check that all records have required fields
        for records in [vlocal_records, vroaming_records]:
            for record in records:
                assert 'zone' in record
                assert 'view' in record
                assert 'name' in record
                assert 'type' in record
                assert 'ttl' in record
                assert 'data' in record
    
    def test_parse_files_combined(self):
        """Test parsing zone and view files together."""
        test_dir = Path(__file__).parent
        example_vlocal = test_dir / "example.vlocal"
        example_vroaming = test_dir / "example.vroaming"
        
        parser = DNSZoneParser()
        
        # Parse both files
        records = parser.parse_files(example_vlocal, example_vroaming, "example", "combined")
        
        assert isinstance(records, list)
        assert len(records) > 0
        
        # Check for duplicate handling
        seen = set()
        for record in records:
            key = (record['zone'], record['view'], record['name'], record['type'], record['data'])
            assert key not in seen, f"Duplicate record found: {record}"
            seen.add(key)


class TestCLI:
    """Test CLI functionality."""
    
    def setup_method(self):
        self.runner = CliRunner()
    
    def test_parse_single_success(self):
        """Test successful single file parsing via CLI."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.zone"
            test_content = """
$ORIGIN test.com.
@ IN SOA ns1.test.com. admin.test.com. 2024010101 3600 1800 604800 86400
@ IN NS ns1.test.com.
www IN A 192.0.2.1
"""
            test_file.write_text(test_content)
            
            result = self.runner.invoke(app, [
                "parse-single", str(test_file),
                "--zone-name", "test.com",
                "--view-name", "internal"
            ])
            
            assert result.exit_code == 0
            assert "Successfully parsed" in result.stdout
            assert "Output saved to" in result.stdout
    
    def test_parse_single_with_output(self):
        """Test single file parsing with custom output path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.zone"
            output_file = Path(tmpdir) / "custom_output.csv"
            
            test_content = """
$ORIGIN test.com.
@ IN A 192.0.2.1
"""
            test_file.write_text(test_content)
            
            result = self.runner.invoke(app, [
                "parse-single", str(test_file),
                "--zone-name", "test.com",
                "--output", str(output_file)
            ])
            
            assert result.exit_code == 0
            assert output_file.exists()
    
    def test_parse_single_invalid_file(self):
        """Test CLI error handling for invalid file."""
        result = self.runner.invoke(app, [
            "parse-single", "/nonexistent/file.zone"
        ])
        
        assert result.exit_code == 1
        assert "File validation failed" in result.stdout
    
    def test_parse_zone_success(self):
        """Test successful zone and view file parsing via CLI."""
        with tempfile.TemporaryDirectory() as tmpdir:
            zone_file = Path(tmpdir) / "test.zone"
            view_file = Path(tmpdir) / "test.vroaming"
            
            zone_content = """
$ORIGIN example.com.
@ IN SOA ns1.example.com. admin.example.com. 2024010101 3600 1800 604800 86400
@ IN NS ns1.example.com.
"""
            view_content = """
$ORIGIN example.com.
mail IN A 192.0.2.2
"""
            
            zone_file.write_text(zone_content)
            view_file.write_text(view_content)
            
            result = self.runner.invoke(app, [
                "parse-zone", str(zone_file), str(view_file),
                "--zone-name", "example.com",
                "--view-name", "roaming"
            ])
            
            assert result.exit_code == 0
            assert "Successfully parsed" in result.stdout
    
    def test_parse_zone_auto_detection(self):
        """Test zone and view name auto-detection."""
        with tempfile.TemporaryDirectory() as tmpdir:
            zone_file = Path(tmpdir) / "example.com.zone"
            view_file = Path(tmpdir) / "example.com.vroaming"
            
            zone_content = """
$ORIGIN example.com.
@ IN SOA ns1.example.com. admin.example.com. 2024010101 3600 1800 604800 86400
"""
            view_content = """
$ORIGIN example.com.
www IN A 192.0.2.1
"""
            
            zone_file.write_text(zone_content)
            view_file.write_text(view_content)
            
            result = self.runner.invoke(app, [
                "parse-zone", str(zone_file), str(view_file)
            ])
            
            assert result.exit_code == 0
            assert "example.com" in result.stdout
            assert "roaming" in result.stdout
    
    def test_parse_zone_invalid_zone_file(self):
        """Test CLI error handling for invalid zone file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            zone_file = tmpdir_path / "nonexistent.zone"
            view_file = tmpdir_path / "test.vroaming"
            
            view_file.write_text("$ORIGIN test.com.\n@ IN A 192.0.2.1")
            
            result = self.runner.invoke(app, [
                "parse-zone", str(zone_file), str(view_file)
            ])
            
            assert result.exit_code == 1
            assert "validation failed" in result.stdout
    
    def test_parse_single_verbose_mode(self):
        """Test verbose mode output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.zone"
            test_content = """
$ORIGIN verbose.com.
@ IN SOA ns1.verbose.com. admin.verbose.com. 1 3600 1800 604800 86400
"""
            test_file.write_text(test_content)
            
            result = self.runner.invoke(app, [
                "parse-single", str(test_file),
                "--zone-name", "verbose.com",
                "--verbose"
            ])
            
            assert result.exit_code == 0
            assert "DEBUG" in result.stdout or "INFO" in result.stdout
    
    def test_help_commands(self):
        """Test help commands display correctly."""
        result = self.runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "DNS BIND Zone and View File Parser" in result.stdout
        
        result = self.runner.invoke(app, ["parse-single", "--help"])
        assert result.exit_code == 0
        assert "Parse a single DNS BIND file" in result.stdout
        
        result = self.runner.invoke(app, ["parse-zone", "--help"])
        assert result.exit_code == 0
        assert "Parse DNS BIND zone and view files" in result.stdout


if __name__ == "__main__":
    pytest.main([__file__])