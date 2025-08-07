#!/usr/bin/env python3

"""Functionality tests for Loki CLI commands"""

import pytest
import json
import yaml
import tempfile
import os
from io import StringIO
from loki.cli import app
from typer.testing import CliRunner

runner = CliRunner()


def test_json_format():
    """Test JSON formatting functionality"""
    # Test with inline JSON
    input_json = '{"name":"John","age":30}'
    result = runner.invoke(app, ["json", "format", input_json])
    assert result.exit_code == 0
    
    # Verify it's valid JSON and properly formatted
    parsed = json.loads(result.stdout)
    assert parsed["name"] == "John"
    assert parsed["age"] == 30
    
    # Test with custom indentation
    result = runner.invoke(app, ["json", "format", input_json, "--indent", "4"])
    assert result.exit_code == 0
    assert "    " in result.stdout  # Should have 4 spaces indentation


def test_yaml_format():
    """Test YAML formatting functionality"""
    # Test with inline YAML
    input_yaml = "name: John\nage: 30"
    result = runner.invoke(app, ["yaml", "format", input_yaml])
    assert result.exit_code == 0
    
    # Verify it's valid YAML and properly formatted
    parsed = yaml.safe_load(result.stdout)
    assert parsed["name"] == "John"
    assert parsed["age"] == 30


def test_csv_to_json():
    """Test CSV to JSON conversion functionality"""
    # Create a temporary CSV file
    csv_content = "name,age\nJohn,30\nJane,25"
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(csv_content)
        csv_file = f.name
    
    try:
        # Test conversion
        result = runner.invoke(app, ["csv", "to-json", "--infile", csv_file])
        assert result.exit_code == 0
        
        # Verify it's valid JSON
        parsed = json.loads(result.stdout)
        assert len(parsed) == 2
        assert parsed[0]["name"] == "John"
        assert parsed[0]["age"] == 30  # pandas converts to int
        assert parsed[1]["name"] == "Jane"
        assert parsed[1]["age"] == 25
    finally:
        # Clean up
        os.unlink(csv_file)


def test_json_to_csv():
    """Test JSON to CSV conversion functionality"""
    # Create a temporary JSON file
    json_content = '[{"name":"John","age":30},{"name":"Jane","age":25}]'
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write(json_content)
        json_file = f.name
    
    try:
        # Test conversion
        result = runner.invoke(app, ["csv", "to-csv", "--infile", json_file])
        assert result.exit_code == 0
        
        # Verify it's valid CSV (handle Windows line endings)
        output = result.stdout.strip()
        lines = output.splitlines()  # This handles both \n and \r\n
        assert len(lines) == 3  # header + 2 data rows
        assert lines[0] == "name,age"
        assert "John" in lines[1]
        assert "Jane" in lines[2]
    finally:
        # Clean up
        os.unlink(json_file)


def test_file_input_output():
    """Test file input and output functionality"""
    # Create a temporary input file
    input_content = '{"test":"value"}'
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write(input_content)
        input_file = f.name
    
    # Create a temporary output file path
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
        output_file = f.name
    
    try:
        # Test JSON formatting with file input and output
        result = runner.invoke(app, ["json", "format", "--infile", input_file, "--outfile", output_file])
        assert result.exit_code == 0
        
        # Verify output file content
        with open(output_file, 'r') as f:
            output_content = f.read()
        parsed = json.loads(output_content)
        assert parsed["test"] == "value"
    finally:
        # Clean up
        os.unlink(input_file)
        os.unlink(output_file)
