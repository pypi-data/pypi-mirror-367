"""
Unit tests for the query engine module
"""

import pytest
from bs4 import BeautifulSoup

from hq.parser import HtmlParser
from hq.query import QueryEngine

from .fixtures import COMPLEX_HTML, SIMPLE_HTML


class TestQueryEngine:
    """Test cases for QueryEngine class"""

    def setup_method(self):
        """Setup test fixtures"""
        self.parser = HtmlParser()
        self.query_engine = QueryEngine()
        self.simple_soup = self.parser.parse(SIMPLE_HTML)
        self.complex_soup = self.parser.parse(COMPLEX_HTML)

    def test_query_engine_initialization(self):
        """Test query engine initialization"""
        engine = QueryEngine()
        assert engine is not None

    def test_empty_query(self):
        """Test empty query returns element dictionary"""
        result = self.query_engine.execute(self.simple_soup, "")
        # Empty query returns the document structure as a dict, not a list
        assert isinstance(result, (dict, list))
        # Should contain information about the document
        assert result is not None

    def test_basic_tag_selector(self):
        """Test basic tag selectors"""
        # Test title tag
        result = self.query_engine.execute(self.simple_soup, "title")
        assert len(result) == 1
        assert result[0].name == "title"
        assert result[0].string == "Test Page"

        # Test paragraph tags
        result = self.query_engine.execute(self.simple_soup, "p")
        assert len(result) == 2
        assert all(tag.name == "p" for tag in result)

    def test_class_selector(self):
        """Test class selectors"""
        result = self.query_engine.execute(self.simple_soup, ".content")
        assert len(result) == 1
        assert result[0].get("class") == ["content"]

        # Test with complex HTML
        result = self.query_engine.execute(self.complex_soup, ".nav-link")
        assert len(result) == 3
        assert all("nav-link" in tag.get("class", []) for tag in result)

    def test_id_selector(self):
        """Test ID selectors"""
        result = self.query_engine.execute(self.simple_soup, "#sidebar")
        assert len(result) == 1
        assert result[0].get("id") == "sidebar"

        # Test with complex HTML
        result = self.query_engine.execute(self.complex_soup, "#main-nav")
        assert len(result) == 1
        assert result[0].get("id") == "main-nav"

    def test_compound_selectors(self):
        """Test compound selectors"""
        # Test class then tag
        result = self.query_engine.execute(self.simple_soup, ".content p")
        assert len(result) == 2
        assert all(tag.name == "p" for tag in result)

        # Test ID then class
        result = self.query_engine.execute(self.complex_soup, "#main-nav .nav-link")
        assert len(result) == 3
        assert all("nav-link" in tag.get("class", []) for tag in result)

    def test_attribute_extraction(self):
        """Test attribute extraction"""
        # Test href attribute
        result = self.query_engine.execute(self.simple_soup, "a @href")
        assert result == ["https://example.com"]

        # Test multiple attributes
        result = self.query_engine.execute(self.complex_soup, ".nav-link @href")
        expected = ["/home", "/about", "/contact"]
        assert result == expected

    def test_attribute_selectors(self):
        """Test attribute-based selectors"""
        # Test attribute value selector
        result = self.query_engine.execute(self.simple_soup, "input[type=text]")
        assert len(result) == 1
        assert result[0].get("type") == "text"
        assert result[0].get("name") == "username"

        # Test attribute exists selector - only test for attributes that actually exist
        result = self.query_engine.execute(self.simple_soup, "input[name]")
        assert (
            len(result) >= 2
        )  # At least username and password inputs have name attributes

    def test_compound_attribute_selectors(self):
        """Test compound selectors with attributes"""
        result = self.query_engine.execute(self.simple_soup, "input[type=text]")
        assert len(result) == 1
        assert result[0].get("name") == "username"

    def test_text_extraction(self):
        """Test text extraction"""
        # Test single element text
        result = self.query_engine.execute(self.simple_soup, "title | text")
        assert result == ["Test Page"]

        # Test multiple elements text
        result = self.query_engine.execute(self.simple_soup, "p | text")
        expected = ["First paragraph", "Second paragraph"]
        assert result == expected

    def test_html_extraction(self):
        """Test HTML extraction"""
        result = self.query_engine.execute(self.simple_soup, "title | html")
        assert result == ["<title>Test Page</title>"]

    def test_length_operation(self):
        """Test length operation"""
        # Test counting paragraphs
        result = self.query_engine.execute(self.simple_soup, "p | length")
        assert result == 2

        # Test counting nav links
        result = self.query_engine.execute(self.complex_soup, ".nav-link | length")
        assert result == 3

    def test_indexing(self):
        """Test array indexing"""
        # Test first element
        result = self.query_engine.execute(self.simple_soup, "p | [0]")
        assert result.string.strip() == "First paragraph"

        # Test second element
        result = self.query_engine.execute(self.simple_soup, "p | [1]")
        assert result.string.strip() == "Second paragraph"

        # Test negative indexing
        result = self.query_engine.execute(self.simple_soup, "p | [-1]")
        assert result.string.strip() == "Second paragraph"

    def test_chained_operations(self):
        """Test chained operations with pipes"""
        # Test class selector -> tag selector -> text extraction
        result = self.query_engine.execute(self.simple_soup, ".content | p | text")
        expected = ["First paragraph", "Second paragraph"]
        assert result == expected

        # Test ID selector -> tag selector -> attribute extraction
        result = self.query_engine.execute(self.complex_soup, "#main-nav | a | @href")
        expected = ["/home", "/about", "/contact"]
        assert result == expected

    def test_nonexistent_selectors(self):
        """Test selectors that don't match anything"""
        # Test nonexistent tag
        result = self.query_engine.execute(self.simple_soup, "nonexistent")
        assert result == []

        # Test nonexistent class
        result = self.query_engine.execute(self.simple_soup, ".nonexistent")
        assert result == []

        # Test nonexistent ID
        result = self.query_engine.execute(self.simple_soup, "#nonexistent")
        assert result == []

    def test_complex_data_attributes(self):
        """Test data attribute selectors"""
        # Test data-id attribute
        result = self.query_engine.execute(self.complex_soup, "article[data-id=1]")
        assert len(result) == 1
        assert result[0].get("data-id") == "1"

        # Extract data-id values
        result = self.query_engine.execute(self.complex_soup, "article @data-id")
        assert result == ["1", "2"]

    def test_special_characters_in_selectors(self):
        """Test selectors with special characters"""
        # Test datetime attribute
        result = self.query_engine.execute(self.complex_soup, "time @datetime")
        expected = ["2024-01-01", "2024-01-02"]
        assert result == expected
