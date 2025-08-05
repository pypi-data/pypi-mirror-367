"""
HTML parser using BeautifulSoup
"""

from bs4 import BeautifulSoup


class HtmlParser:
    """Parser to convert HTML into a manipulable structure"""

    def __init__(self) -> None:
        self.parser = "lxml"

    def parse(self, html_content: str) -> BeautifulSoup:
        """
        Parse HTML content and return a BeautifulSoup object

        Args:
            html_content: The HTML content to parse

        Returns:
            BeautifulSoup object
        """
        try:
            soup = BeautifulSoup(html_content, self.parser)
            return soup
        except Exception as e:
            # Fallback to built-in HTML parser
            try:
                soup = BeautifulSoup(html_content, "html.parser")
                return soup
            except Exception:
                raise ValueError(f"Unable to parse HTML: {e}")

    def is_valid_html(self, html_content: str) -> bool:
        """
        Check if content is valid HTML

        Args:
            html_content: The content to verify

        Returns:
            True if HTML is valid
        """
        try:
            soup = self.parse(html_content)
            return len(soup.find_all()) > 0
        except Exception:
            return False
