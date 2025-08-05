"""
Main CLI interface for hq
"""

import sys

import click
from rich.console import Console
from rich.syntax import Syntax

from .formatter import OutputFormatter
from .parser import HtmlParser
from .query import QueryEngine


@click.command()
@click.argument("query", required=False, default="")
@click.option("--raw", "-r", is_flag=True, help="Raw output without formatting")
@click.option("--compact", "-c", is_flag=True, help="Compact JSON output")
@click.option(
    "--color/--no-color", default=True, help="Enable/disable syntax highlighting"
)
@click.option(
    "--output",
    "-o",
    type=click.Choice(["json", "text", "html"]),
    default="html",
    help="Output format",
)
@click.version_option()
def main(query: str, raw: bool, compact: bool, color: bool, output: str) -> None:
    """
    hq - HTML Query Tool

    Parse and extract data from HTML with jq-like syntax.

    Examples:
        curl http://example.com | hq 'title'              # Get title tags
        curl http://example.com | hq 'title | text'       # Get title text only
        curl http://example.com | hq 'a @href'            # Get href attributes
        curl http://example.com | hq '.container p'       # Get paragraphs in container
        curl http://example.com | hq '#main .content'     # Get elements by ID and class
        curl http://example.com | hq 'div[id=content]'    # Get div with specific attr
        curl http://example.com | hq 'li [0]'             # Get first list item
        curl http://example.com | hq --output text 'p'    # Output as plain text
        curl http://example.com | hq --output json 'title'  # Output as JSON
    """
    console = Console(force_terminal=color)

    try:
        # Read from stdin
        if sys.stdin.isatty():
            click.echo(
                "Error: No data provided. Use a pipe or redirect input.", err=True
            )
            sys.exit(1)

        html_content = sys.stdin.read()

        if not html_content.strip():
            click.echo("Error: Empty HTML content", err=True)
            sys.exit(1)

        # Parse the HTML
        parser = HtmlParser()
        soup = parser.parse(html_content)

        # Execute the query
        query_engine = QueryEngine()

        if not query:
            # If no query, display formatted HTML
            result = str(soup.prettify())
            if color and not raw:
                syntax = Syntax(result, "html", theme="monokai", line_numbers=False)
                console.print(syntax)
            else:
                click.echo(result)
        else:
            result = query_engine.execute(soup, query)

            # Format the output
            formatter = OutputFormatter(color=color, compact=compact, raw=raw)
            formatted_output = formatter.format(result, output_format=output)

            if color and not raw and output == "html":
                syntax = Syntax(
                    formatted_output, "html", theme="monokai", line_numbers=False
                )
                console.print(syntax)
            elif color and not raw and output == "json":
                syntax = Syntax(
                    formatted_output, "json", theme="monokai", line_numbers=False
                )
                console.print(syntax)
            else:
                click.echo(formatted_output)

    except KeyboardInterrupt:
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
