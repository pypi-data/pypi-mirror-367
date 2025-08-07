#!/usr/bin/env python3

"""Basic tests for Loki CLI"""

import pytest
import sys
from io import StringIO
from loki.cli import app
from typer.testing import CliRunner

runner = CliRunner()


def test_cli_help():
    """Test that the main CLI shows help"""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Loki CLI" in result.stdout
    assert "jwt" in result.stdout
    assert "saml" in result.stdout
    assert "json" in result.stdout
    assert "xml" in result.stdout
    assert "yaml" in result.stdout
    assert "csv" in result.stdout


def test_jwt_help():
    """Test that the JWT command shows help"""
    result = runner.invoke(app, ["jwt", "--help"])
    assert result.exit_code == 0
    assert "JWT" in result.stdout
    assert "decode" in result.stdout


def test_saml_help():
    """Test that the SAML command shows help"""
    result = runner.invoke(app, ["saml", "--help"])
    assert result.exit_code == 0
    assert "SAML" in result.stdout
    assert "decode" in result.stdout


def test_json_help():
    """Test that the JSON command shows help"""
    result = runner.invoke(app, ["json", "--help"])
    assert result.exit_code == 0
    assert "JSON" in result.stdout
    assert "format" in result.stdout


def test_xml_help():
    """Test that the XML command shows help"""
    result = runner.invoke(app, ["xml", "--help"])
    assert result.exit_code == 0
    assert "XML" in result.stdout
    assert "format" in result.stdout


def test_yaml_help():
    """Test that the YAML command shows help"""
    result = runner.invoke(app, ["yaml", "--help"])
    assert result.exit_code == 0
    assert "YAML" in result.stdout
    assert "format" in result.stdout


def test_csv_help():
    """Test that the CSV command shows help"""
    result = runner.invoke(app, ["csv", "--help"])
    assert result.exit_code == 0
    assert "CSV" in result.stdout
    assert "to-json" in result.stdout
    assert "to-csv" in result.stdout
