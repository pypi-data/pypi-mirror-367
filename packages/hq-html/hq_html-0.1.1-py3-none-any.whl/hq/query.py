"""
Query engine for executing jq-like queries on HTML
"""

from typing import Any, Dict, List, Union

from bs4 import BeautifulSoup, Tag


class QueryEngine:
    """Engine to execute jq-like queries on HTML structures"""

    def __init__(self) -> None:
        pass

    def execute(self, soup: BeautifulSoup, query: str) -> Any:
        """
        Execute a query on the HTML structure

        Args:
            soup: BeautifulSoup object
            query: Query string in jq-like syntax

        Returns:
            Query results
        """
        if not query.strip():
            return self._element_to_dict(soup)

        # Handle compound selectors like ".content p"
        if " " in query and not query.startswith("@") and "|" not in query:
            parts = query.split()
            result = soup
            for part in parts:
                result = self._execute_single_query(result, part)
                if result is None or (isinstance(result, list) and len(result) == 0):
                    break
            return result

        # Handle special case of "tag @attr" syntax
        if " @" in query and "|" not in query:
            parts = query.split(" @", 1)
            tag_part = parts[0].strip()
            attr_part = "@" + parts[1].strip()
            result = self._execute_single_query(soup, tag_part)
            return self._execute_single_query(result, attr_part)

        # Split query by pipes to handle chaining
        parts = [part.strip() for part in query.split("|")]
        result = soup

        for part in parts:
            result = self._execute_single_query(result, part)
            # If result is None, stop processing
            if result is None:
                break

        return result

    def _execute_single_query(self, element: Any, query: str) -> Any:  # noqa: C901
        """Execute a single query part"""
        query = query.strip()

        # Handle selectors with attributes like "input[type=text]"
        if "[" in query and "]" in query and not query.startswith("["):
            # Split tag and attribute parts
            tag_part = query[: query.index("[")]
            attr_part = query[query.index("[") :]
            result = self._execute_single_query(element, tag_part)
            return self._execute_single_query(result, attr_part)

        # Handle special functions
        if query == "text":
            return self._get_text(element)
        elif query == "html":
            return self._get_html(element)
        elif query == "length":
            return self._get_length(element)
        elif query.startswith("@"):
            return self._get_attribute(element, query[1:])
        elif query.startswith("."):
            return self._get_by_class(element, query[1:])
        elif query.startswith("#"):
            return self._get_by_id(element, query[1:])
        elif query.startswith("[") and query.endswith("]"):
            inner = query[1:-1]
            if inner.isdigit() or (inner.startswith("-") and inner[1:].isdigit()):
                return self._get_by_index(element, inner)
            elif "=" in inner:
                return self._get_by_attribute_value(element, inner)
            else:
                # Attribute exists check
                return self._get_by_attribute_exists(element, inner)
        elif query.startswith("#") and " " in query:
            # Handle compound selectors starting with ID
            parts = query.split(" ", 1)
            id_part = parts[0]
            rest = parts[1]
            result = self._execute_single_query(element, id_part)
            return self._execute_single_query(result, rest)
        elif query.startswith(".") and " " in query:
            # Handle compound selectors starting with class
            parts = query.split(" ", 1)
            class_part = parts[0]
            rest = parts[1]
            result = self._execute_single_query(element, class_part)
            return self._execute_single_query(result, rest)
        else:
            # Tag selector
            return self._get_by_tag(element, query)

    def _get_text(self, element: Any) -> Union[str, List[str]]:
        """Get text content"""
        if isinstance(element, list):
            result: List[str] = []
            for el in element:
                text = self._get_text(el)
                if isinstance(text, str):
                    result.append(text)
                elif isinstance(text, list):
                    result.extend(text)
            return result
        elif isinstance(element, (Tag, BeautifulSoup)):
            return element.get_text(strip=True)
        else:
            return str(element)

    def _get_html(self, element: Any) -> Union[str, List[str]]:
        """Get HTML content"""
        if isinstance(element, list):
            result = []
            for el in element:
                html = self._get_html(el)
                if isinstance(html, str):
                    result.append(html)
                elif isinstance(html, list):
                    result.extend(html)
            return result
        elif isinstance(element, (Tag, BeautifulSoup)):
            return str(element)
        else:
            return str(element)

    def _get_length(self, element: Any) -> int:
        """Get length of element or list"""
        if isinstance(element, list):
            return len(element)
        elif isinstance(element, (Tag, BeautifulSoup)):
            return len(element.find_all())
        else:
            return 1

    def _get_attribute(self, element: Any, attr: str) -> Any:
        """Get attribute value"""
        if isinstance(element, list):
            return [self._get_attribute(el, attr) for el in element]
        elif isinstance(element, Tag):
            return element.get(attr)
        else:
            return None

    def _get_by_class(self, element: Any, class_name: str) -> List[Tag]:
        """Get elements by class name"""
        if isinstance(element, list):
            results = []
            for el in element:
                results.extend(self._get_by_class(el, class_name))
            return results
        elif isinstance(element, (Tag, BeautifulSoup)):
            found = element.find_all(class_=class_name)
            return [tag for tag in found if isinstance(tag, Tag)]
        else:
            return []

    def _get_by_id(self, element: Any, id_name: str) -> List[Tag]:
        """Get element by ID"""
        if isinstance(element, list):
            results = []
            for el in element:
                sub_results = self._get_by_id(el, id_name)
                results.extend(sub_results)
            return results
        elif isinstance(element, (Tag, BeautifulSoup)):
            found = element.find(id=id_name)
            return [found] if found and isinstance(found, Tag) else []
        else:
            return []

    def _get_by_tag(self, element: Any, tag_name: str) -> List[Tag]:
        """Get elements by tag name"""
        if isinstance(element, list):
            results = []
            for el in element:
                results.extend(self._get_by_tag(el, tag_name))
            return results
        elif isinstance(element, (Tag, BeautifulSoup)):
            found = element.find_all(tag_name)
            return [tag for tag in found if isinstance(tag, Tag)]
        else:
            return []

    def _get_by_index(self, element: Any, index_str: str) -> Any:
        """Get element by index"""
        try:
            index = int(index_str)
            if isinstance(element, list):
                if -len(element) <= index < len(element):
                    return element[index]
                return None
            elif isinstance(element, (Tag, BeautifulSoup)):
                children = list(element.children)
                if -len(children) <= index < len(children):
                    return children[index]
                return None
            else:
                return None
        except ValueError:
            return None

    def _get_by_attribute_value(self, element: Any, attr_query: str) -> List[Tag]:
        """Get elements by attribute value"""
        if "=" not in attr_query:
            return []

        attr_name, attr_value = attr_query.split("=", 1)
        attr_name = attr_name.strip()
        attr_value = attr_value.strip().strip("\"'")

        if isinstance(element, list):
            results = []
            for el in element:
                if isinstance(el, Tag) and el.get(attr_name) == attr_value:
                    results.append(el)
            return results
        elif isinstance(element, (Tag, BeautifulSoup)):
            found = element.find_all(lambda tag: tag.get(attr_name) == attr_value)
            return [tag for tag in found if isinstance(tag, Tag)]
        else:
            return []

    def _get_by_attribute_exists(self, element: Any, attr_name: str) -> List[Tag]:
        """Get elements that have a specific attribute"""
        if isinstance(element, list):
            results = []
            for el in element:
                if isinstance(el, Tag) and el.has_attr(attr_name):
                    results.append(el)
            return results
        elif isinstance(element, (Tag, BeautifulSoup)):
            found = element.find_all(
                lambda tag: (
                    tag.has_attr(attr_name) if hasattr(tag, "has_attr") else False
                )
            )
            return [tag for tag in found if isinstance(tag, Tag)]
        else:
            return []

    def _element_to_dict(self, element: Any) -> Union[Dict[str, Any], List[Any], str]:
        """Convert element to dictionary representation"""
        if isinstance(element, list):
            return [self._element_to_dict(el) for el in element]
        elif isinstance(element, Tag):
            # Handle attrs properly - element.attrs can be None or a dict
            attrs_dict = {}
            if element.attrs:
                # Convert attribute values to strings to avoid type issues
                attrs_dict = {
                    k: str(v) if not isinstance(v, list) else v
                    for k, v in element.attrs.items()
                }

            result: Dict[str, Any] = {
                "tag": element.name,
                "attrs": attrs_dict,
                "text": (
                    element.get_text(strip=True)
                    if element.get_text(strip=True)
                    else None
                ),
            }

            children = [child for child in element.children if isinstance(child, Tag)]
            if children:
                result["children"] = [
                    self._element_to_dict(child) for child in children
                ]

            return result
        elif isinstance(element, BeautifulSoup):
            # For the root document, return all top-level tags
            children = [child for child in element.children if isinstance(child, Tag)]
            return [self._element_to_dict(child) for child in children]
        else:
            return str(element)
