"""
Integration tests for the CLI module
"""

import json

from click.testing import CliRunner

from hq.cli import main

from .fixtures import COMPLEX_HTML, SIMPLE_HTML


class TestCLI:
    """Test cases for CLI interface"""

    def setup_method(self):
        """Setup test fixtures"""
        self.runner = CliRunner()

    def test_cli_no_input(self):
        """Test CLI with no input (should show error)"""
        result = self.runner.invoke(main, [])
        assert result.exit_code == 1
        assert "Error: Empty HTML content" in result.output

    def test_cli_with_empty_query(self):
        """Test CLI with empty query (should format HTML)"""
        result = self.runner.invoke(main, ["--no-color"], input=SIMPLE_HTML)
        assert result.exit_code == 0
        assert "<title>" in result.output
        assert "Test Page" in result.output

    def test_cli_basic_selector(self):
        """Test CLI with basic selectors"""
        # Test title selector
        result = self.runner.invoke(main, ["title"], input=SIMPLE_HTML)
        assert result.exit_code == 0
        assert "Test Page" in result.output

        # Test paragraph selector
        result = self.runner.invoke(main, ["p"], input=SIMPLE_HTML)
        assert result.exit_code == 0
        assert "First paragraph" in result.output
        assert "Second paragraph" in result.output

    def test_cli_class_selector(self):
        """Test CLI with class selectors"""
        result = self.runner.invoke(main, [".content"], input=SIMPLE_HTML)
        assert result.exit_code == 0
        assert "content" in result.output

    def test_cli_id_selector(self):
        """Test CLI with ID selectors"""
        result = self.runner.invoke(main, ["--no-color", "#sidebar"], input=SIMPLE_HTML)
        assert result.exit_code == 0
        assert "sidebar" in result.output
        assert "<ul>" in result.output

    def test_cli_compound_selector(self):
        """Test CLI with compound selectors"""
        result = self.runner.invoke(
            main, ["--no-color", ".content p"], input=SIMPLE_HTML
        )
        assert result.exit_code == 0
        assert "First paragraph" in result.output
        assert "Second paragraph" in result.output

    def test_cli_attribute_extraction(self):
        """Test CLI with attribute extraction"""
        result = self.runner.invoke(main, ["a @href"], input=SIMPLE_HTML)
        assert result.exit_code == 0
        assert "https://example.com" in result.output

    def test_cli_text_extraction(self):
        """Test CLI with text extraction"""
        result = self.runner.invoke(main, ["--raw", "title | text"], input=SIMPLE_HTML)
        assert result.exit_code == 0
        assert result.output.strip() == "Test Page"

    def test_cli_chained_operations(self):
        """Test CLI with chained operations"""
        result = self.runner.invoke(
            main, ["--no-color", ".content | p | text"], input=SIMPLE_HTML
        )
        assert result.exit_code == 0
        assert "First paragraph" in result.output
        assert "Second paragraph" in result.output

    def test_cli_json_output(self):
        """Test CLI with JSON output format"""
        result = self.runner.invoke(
            main, ["--no-color", "--output", "json", "title"], input=SIMPLE_HTML
        )
        assert result.exit_code == 0

        # Should be valid JSON
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["tag"] == "title"
        assert data[0]["text"] == "Test Page"

    def test_cli_text_output(self):
        """Test CLI with text output format"""
        result = self.runner.invoke(main, ["--output", "text", "p"], input=SIMPLE_HTML)
        assert result.exit_code == 0

        lines = result.output.strip().split("\n")
        assert "First paragraph" in lines
        assert "Second paragraph" in lines

    def test_cli_raw_output(self):
        """Test CLI with raw output"""
        result = self.runner.invoke(main, ["--raw", "title | text"], input=SIMPLE_HTML)
        assert result.exit_code == 0
        assert result.output.strip() == "Test Page"

    def test_cli_compact_output(self):
        """Test CLI with compact JSON output"""
        result = self.runner.invoke(
            main,
            ["--no-color", "--compact", "--output", "json", "title"],
            input=SIMPLE_HTML,
        )
        assert result.exit_code == 0

        # Compact JSON should have no extra whitespace
        assert ": " not in result.output or result.output.count(
            ": "
        ) < result.output.count(":")

        # Should still be valid JSON
        data = json.loads(result.output)
        assert data[0]["tag"] == "title"

    def test_cli_no_color(self):
        """Test CLI with color disabled"""
        result = self.runner.invoke(main, ["--no-color", "title"], input=SIMPLE_HTML)
        assert result.exit_code == 0
        # Hard to test color output in unit tests, but should succeed

    def test_cli_attribute_selector(self):
        """Test CLI with attribute selectors"""
        result = self.runner.invoke(
            main, ["--no-color", "input[type=text]"], input=SIMPLE_HTML
        )
        assert result.exit_code == 0
        assert 'type="text"' in result.output
        assert 'name="username"' in result.output

    def test_cli_indexing(self):
        """Test CLI with array indexing"""
        result = self.runner.invoke(
            main, ["--raw", "p | [0] | text"], input=SIMPLE_HTML
        )
        assert result.exit_code == 0
        assert result.output.strip() == "First paragraph"

    def test_cli_length_operation(self):
        """Test CLI with length operation"""
        result = self.runner.invoke(main, ["--raw", "p | length"], input=SIMPLE_HTML)
        assert result.exit_code == 0
        assert result.output.strip() == "2"

    def test_cli_complex_html(self):
        """Test CLI with complex HTML structure"""
        result = self.runner.invoke(main, [".nav-link @href"], input=COMPLEX_HTML)
        assert result.exit_code == 0
        assert "/home" in result.output
        assert "/about" in result.output
        assert "/contact" in result.output

    def test_cli_nonexistent_selector(self):
        """Test CLI with nonexistent selectors"""
        result = self.runner.invoke(main, ["--raw", "nonexistent"], input=SIMPLE_HTML)
        assert result.exit_code == 0
        assert result.output.strip() == ""

    def test_cli_empty_html(self):
        """Test CLI with empty HTML"""
        result = self.runner.invoke(main, ["title"], input="")
        assert result.exit_code == 1
        assert "Error: Empty HTML content" in result.output

    def test_cli_malformed_html(self):
        """Test CLI with malformed HTML"""
        malformed = "<html><head><title>Test</title></head><body><p>Test"
        result = self.runner.invoke(main, ["title | text"], input=malformed)
        assert result.exit_code == 0
        assert "Test" in result.output

    def test_cli_help(self):
        """Test CLI help output"""
        result = self.runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "HTML Query Tool" in result.output
        assert "Examples:" in result.output

    def test_cli_version(self):
        """Test CLI version output"""
        result = self.runner.invoke(main, ["--version"])
        assert result.exit_code == 0
