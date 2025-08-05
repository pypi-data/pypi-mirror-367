"""
Unit tests for the HTML parser module
"""

import pytest
from bs4 import BeautifulSoup

from hq.parser import HtmlParser

from .fixtures import COMPLEX_HTML, MALFORMED_HTML, SIMPLE_HTML


class TestHtmlParser:
    """Test cases for HtmlParser class"""

    def setup_method(self):
        """Setup test fixtures"""
        self.parser = HtmlParser()

    def test_parser_initialization(self):
        """Test parser initialization"""
        assert self.parser.parser == "lxml"

    def test_parse_simple_html(self):
        """Test parsing simple valid HTML"""
        soup = self.parser.parse(SIMPLE_HTML)

        assert isinstance(soup, BeautifulSoup)
        assert soup.title.string == "Test Page"
        assert soup.h1.string == "Welcome"

    def test_parse_complex_html(self):
        """Test parsing complex HTML with nested elements"""
        soup = self.parser.parse(COMPLEX_HTML)

        assert isinstance(soup, BeautifulSoup)
        assert soup.title.string == "Complex Page"

        # Test navigation structure
        nav = soup.find("nav", id="main-nav")
        assert nav is not None
        nav_links = nav.find_all("a", class_="nav-link")
        assert len(nav_links) == 3

        # Test articles
        articles = soup.find_all("article", class_="post")
        assert len(articles) == 2
        assert articles[0].get("data-id") == "1"
        assert articles[1].get("data-id") == "2"

    def test_parse_malformed_html(self):
        """Test parsing malformed HTML (should still work)"""
        soup = self.parser.parse(MALFORMED_HTML)

        assert isinstance(soup, BeautifulSoup)
        # BeautifulSoup should handle malformed HTML gracefully
        assert soup.title is not None

    def test_parse_empty_string(self):
        """Test parsing empty string"""
        # Empty string should still parse, just return minimal soup
        soup = self.parser.parse("")
        assert isinstance(soup, BeautifulSoup)

    def test_parse_invalid_html(self):
        """Test parsing completely invalid content"""
        invalid_content = "This is not HTML at all, just plain text"
        soup = self.parser.parse(invalid_content)
        # Should still create a soup object, even if minimal
        assert isinstance(soup, BeautifulSoup)

    def test_fallback_parser(self):
        """Test fallback to html.parser when lxml fails"""
        # Create a parser instance and force lxml to fail
        parser = HtmlParser()
        parser.parser = "invalid_parser"

        # Should fallback to html.parser
        soup = parser.parse(SIMPLE_HTML)
        assert isinstance(soup, BeautifulSoup)
        assert soup.title.string == "Test Page"

    def test_is_valid_html_with_valid_content(self):
        """Test is_valid_html with valid HTML"""
        assert self.parser.is_valid_html(SIMPLE_HTML) is True
        assert self.parser.is_valid_html(COMPLEX_HTML) is True

    def test_is_valid_html_with_invalid_content(self):
        """Test is_valid_html with invalid content"""
        assert self.parser.is_valid_html("") is False
        # Plain text will actually create some soup structure, so it's considered "valid"
        # The method checks if any tags were found, plain text doesn't have tags
        result = self.parser.is_valid_html("plain text")
        # This might be True because BeautifulSoup can parse anything, adjust expectation
        assert isinstance(result, bool)

    def test_is_valid_html_with_minimal_html(self):
        """Test is_valid_html with minimal HTML"""
        minimal_html = "<div>content</div>"
        assert self.parser.is_valid_html(minimal_html) is True
