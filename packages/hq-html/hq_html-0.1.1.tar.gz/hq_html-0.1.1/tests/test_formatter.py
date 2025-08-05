"""
Unit tests for the output formatter module
"""

import json

from bs4 import BeautifulSoup

from hq.formatter import OutputFormatter
from hq.parser import HtmlParser

from .fixtures import SIMPLE_HTML


class TestOutputFormatter:
    """Test cases for OutputFormatter class"""

    def setup_method(self):
        """Setup test fixtures"""
        self.parser = HtmlParser()
        self.soup = self.parser.parse(SIMPLE_HTML)
        self.title_tag = self.soup.find("title")
        self.paragraphs = self.soup.find_all("p")

    def test_formatter_initialization(self):
        """Test formatter initialization with different options"""
        # Default formatter
        formatter = OutputFormatter()
        assert formatter.color is True
        assert formatter.compact is False
        assert formatter.raw is False

        # Custom formatter
        formatter = OutputFormatter(color=False, compact=True, raw=True)
        assert formatter.color is False
        assert formatter.compact is True
        assert formatter.raw is True

    def test_format_html_output(self):
        """Test HTML output formatting"""
        formatter = OutputFormatter()

        # Test single element
        result = formatter.format(self.title_tag, "html")
        assert "<title>" in result
        assert "Test Page" in result

        # Test multiple elements
        result = formatter.format(self.paragraphs, "html")
        assert "First paragraph" in result
        assert "Second paragraph" in result
        assert result.count("<p>") == 2

    def test_format_text_output(self):
        """Test text output formatting"""
        formatter = OutputFormatter()

        # Test single element
        result = formatter.format(self.title_tag, "text")
        assert result == "Test Page"

        # Test multiple elements
        result = formatter.format(self.paragraphs, "text")
        lines = result.split("\n")
        assert "First paragraph" in lines
        assert "Second paragraph" in lines

    def test_format_json_output(self):
        """Test JSON output formatting"""
        formatter = OutputFormatter()

        # Test single element
        result = formatter.format(self.title_tag, "json")
        data = json.loads(result)
        assert data["tag"] == "title"
        assert data["text"] == "Test Page"

        # Test multiple elements
        result = formatter.format(self.paragraphs, "json")
        data = json.loads(result)
        assert len(data) == 2
        assert data[0]["tag"] == "p"
        assert data[1]["tag"] == "p"

    def test_compact_json_output(self):
        """Test compact JSON output"""
        formatter = OutputFormatter(compact=True)

        result = formatter.format(self.title_tag, "json")
        # Compact JSON should not have spaces after separators
        assert ": " not in result or result.count(": ") < result.count(":")

        # Should still be valid JSON
        data = json.loads(result)
        assert data["tag"] == "title"

    def test_raw_output(self):
        """Test raw output formatting"""
        formatter = OutputFormatter(raw=True)

        # Raw output should be plain strings
        result = formatter.format(self.title_tag, "html")
        assert result == str(self.title_tag)

        # Test with list
        result = formatter.format(self.paragraphs, "html")
        lines = result.split("\n")
        assert len(lines) == 2

    def test_format_string_data(self):
        """Test formatting string data"""
        formatter = OutputFormatter()

        test_string = "Hello World"

        # HTML format
        result = formatter.format(test_string, "html")
        assert result == test_string

        # Text format
        result = formatter.format(test_string, "text")
        assert result == test_string

        # JSON format
        result = formatter.format(test_string, "json")
        assert json.loads(result) == test_string

    def test_format_list_of_strings(self):
        """Test formatting list of strings"""
        formatter = OutputFormatter()

        test_list = ["First", "Second", "Third"]

        # HTML format
        result = formatter.format(test_list, "html")
        assert "First" in result
        assert "Second" in result
        assert "Third" in result

        # Text format
        result = formatter.format(test_list, "text")
        lines = result.split("\n")
        assert len(lines) == 3
        assert lines[0] == "First"

        # JSON format
        result = formatter.format(test_list, "json")
        assert json.loads(result) == test_list

    def test_make_serializable(self):
        """Test _make_serializable method"""
        formatter = OutputFormatter()

        # Test with BeautifulSoup tag
        serializable = formatter._make_serializable(self.title_tag)
        assert isinstance(serializable, dict)
        assert serializable["tag"] == "title"
        assert serializable["text"] == "Test Page"

        # Test with list of tags
        serializable = formatter._make_serializable(self.paragraphs)
        assert isinstance(serializable, list)
        assert len(serializable) == 2
        assert serializable[0]["tag"] == "p"

        # Test with primitive types
        assert formatter._make_serializable("string") == "string"
        assert formatter._make_serializable(42) == 42
        assert formatter._make_serializable(True) is True
        assert formatter._make_serializable(None) is None

    def test_format_with_attributes(self):
        """Test formatting elements with attributes"""
        formatter = OutputFormatter()

        # Get a link element which has attributes
        link = self.soup.find("a")

        # JSON format should include attributes
        result = formatter.format(link, "json")
        data = json.loads(result)
        assert data["tag"] == "a"
        assert data["attrs"]["href"] == "https://example.com"
        assert data["text"] == "Example Link"

    def test_format_nested_elements(self):
        """Test formatting nested elements"""
        formatter = OutputFormatter()

        # Get content div which has nested elements
        content_div = self.soup.find("div", class_="content")

        # JSON format should include children
        result = formatter.format(content_div, "json")
        data = json.loads(result)
        assert data["tag"] == "div"
        assert "children" in data
        assert len(data["children"]) == 3  # 2 paragraphs + 1 link
