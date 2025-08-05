"""
Output formatter for different output formats
"""

import json
from typing import Any, Dict, List, Union

from bs4 import BeautifulSoup, Tag


class OutputFormatter:
    """Formatter for different output formats"""

    def __init__(
        self, color: bool = True, compact: bool = False, raw: bool = False
    ) -> None:
        self.color = color
        self.compact = compact
        self.raw = raw

    def format(self, data: Any, output_format: str = "json") -> str:
        """
        Format data according to the specified output format

        Args:
            data: Data to format
            output_format: Output format ('json', 'text', 'html')

        Returns:
            Formatted string
        """
        if self.raw:
            return self._format_raw(data)

        if output_format == "json":
            return self._format_json(data)
        elif output_format == "text":
            return self._format_text(data)
        elif output_format == "html":
            return self._format_html(data)
        else:
            return self._format_json(data)

    def _format_raw(self, data: Any) -> str:
        """Format as raw output"""
        if isinstance(data, str):
            return data
        elif isinstance(data, list):
            return "\n".join(str(item) for item in data)
        else:
            return str(data)

    def _format_json(self, data: Any) -> str:
        """Format as JSON"""
        # Convert BeautifulSoup objects to serializable format
        serializable_data = self._make_serializable(data)

        if self.compact:
            return json.dumps(
                serializable_data, ensure_ascii=False, separators=(",", ":")
            )
        else:
            return json.dumps(serializable_data, ensure_ascii=False, indent=2)

    def _format_text(self, data: Any) -> str:
        """Format as plain text"""
        if isinstance(data, str):
            return data
        elif isinstance(data, list):
            results = []
            for item in data:
                if isinstance(item, (Tag, BeautifulSoup)):
                    results.append(item.get_text(strip=True))
                else:
                    results.append(str(item))
            return "\n".join(results)
        elif isinstance(data, (Tag, BeautifulSoup)):
            return data.get_text(strip=True)
        else:
            # Ensure we always return a string
            return str(data) if data is not None else ""

    def _format_html(self, data: Any) -> str:
        """Format as HTML"""
        if isinstance(data, str):
            return data
        elif isinstance(data, list):
            results = []
            for item in data:
                if isinstance(item, (Tag, BeautifulSoup)):
                    # Use prettify for nice formatting
                    formatted = (
                        str(item.prettify()) if hasattr(item, "prettify") else str(item)
                    )
                    results.append(formatted.strip())
                else:
                    results.append(str(item))
            return "\n\n".join(results)  # Double newline between elements
        elif isinstance(data, (Tag, BeautifulSoup)):
            # Use prettify for nice formatting
            return str(data.prettify()) if hasattr(data, "prettify") else str(data)
        else:
            return str(data)

    def _make_serializable(
        self, data: Any
    ) -> Union[Dict[str, Any], List[Any], str, int, float, bool, None]:
        """Convert data to JSON-serializable format"""
        if isinstance(data, (str, int, float, bool, type(None))):
            return data
        elif isinstance(data, dict):
            return {key: self._make_serializable(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self._make_serializable(item) for item in data]
        elif isinstance(data, Tag):
            # Handle attrs properly - data.attrs can be None or a dict
            attrs_dict = {}
            if data.attrs:
                # Convert attribute values to strings to avoid type issues
                attrs_dict = {
                    k: str(v) if not isinstance(v, list) else v
                    for k, v in data.attrs.items()
                }

            result: Dict[str, Any] = {
                "tag": data.name,
                "attrs": attrs_dict,
                "text": (
                    data.get_text(strip=True) if data.get_text(strip=True) else None
                ),
            }

            # Add children if they exist
            children = [child for child in data.children if isinstance(child, Tag)]
            if children:
                result["children"] = [
                    self._make_serializable(child) for child in children
                ]

            return result
        elif isinstance(data, BeautifulSoup):
            # For BeautifulSoup, return all top-level tags
            children = [child for child in data.children if isinstance(child, Tag)]
            return [self._make_serializable(child) for child in children]
        else:
            return str(data)
