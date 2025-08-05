# hq - HTML Query Tool

A command-line HTML processor inspired by `jq`. Parse and extract data from HTML with jq-like syntax.

## Features

- **jq-like syntax**: Familiar query syntax for HTML processing
- **CSS selectors**: Support for class (`.class`) and ID (`#id`) selectors  
- **Attribute extraction**: Get attributes or filter by attribute values
- **Syntax highlighting**: Colored output for better readability
- **Multiple output formats**: HTML, text, JSON, and raw formats
- **Pipe operations**: Chain multiple operations together
- **Pretty formatting**: Nicely formatted HTML output

## Installation

```bash
pip install hq-html
```

## Usage

```bash
# Basic: parse HTML from stdin
curl http://example.com | hq

# Extract specific elements
curl http://example.com | hq 'title'
curl http://example.com | hq 'h1 | text'
```

## Examples

### Basic Selectors
```bash
# Get title elements
curl http://example.com | hq 'title'

# Get all paragraphs
curl http://example.com | hq 'p'

# Get elements by class
curl http://example.com | hq '.content'

# Get elements by ID
curl http://example.com | hq '#main'
```

### Compound Selectors
```bash
# Get paragraphs inside content class
curl http://example.com | hq '.content p'

# Get links inside navigation
curl http://example.com | hq '#nav a'

# Complex nested selection
curl http://example.com | hq '#main .content p'
```

### Attribute Selectors
```bash
# Get href attributes from links
curl http://example.com | hq 'a @href'

# Get input elements by type
curl http://example.com | hq 'input[type=text]'

# Get elements with specific attributes
curl http://example.com | hq 'img[alt]'

# Get image sources
curl http://example.com | hq 'img @src'
```

### Text Extraction
```bash
# Get text content only
curl http://example.com | hq 'title | text'

# Get text from multiple elements
curl http://example.com | hq 'p | text'

# Get text from headings
curl http://example.com | hq 'h1 | text'
```

### Output Formats
```bash
# HTML output (default)
curl http://example.com | hq 'title'

# Text output
curl http://example.com | hq --output text 'p'

# JSON output
curl http://example.com | hq --output json 'title'

# Raw output (no formatting)
curl http://example.com | hq --raw 'title | text'

# Compact output
curl http://example.com | hq --compact 'title'
```

### Chaining Operations
```bash
# Chain operations with pipes
curl http://example.com | hq '.content | p | text'

# Get first element
curl http://example.com | hq 'li | [0]'

# Get specific attribute
curl http://example.com | hq 'a | @href'

# Count elements
curl http://example.com | hq 'div | length'
```

## Syntax Reference

- **Tag selectors**: `div`, `p`, `a`, `img`, etc.
- **Class selectors**: `.className`
- **ID selectors**: `#idName`
- **Attribute selectors**: `[attr=value]`, `[attr]`
- **Compound selectors**: `.class tag`, `#id .class`
- **Attribute extraction**: `@href`, `@src`, `@alt`
- **Text extraction**: `| text`
- **HTML extraction**: `| html`
- **Array indexing**: `| [0]`, `| [1]`
- **Length**: `| length`
- **Piping**: `selector | operation | filter`

## Options

- `--output, -o`: Output format (html, text, json)
- `--raw, -r`: Raw output without formatting
- `--compact, -c`: Compact JSON output
- `--color/--no-color`: Enable/disable syntax highlighting
- `--help`: Show help message with examples

## Real-world Examples

```bash
# Extract all article titles from Hacker News
curl -s https://news.ycombinator.com | hq '.titleline a | text'

# Get all external links from a page
curl -s http://example.com | hq 'a @href'

# Extract meta description
curl -s http://example.com | hq 'meta[name=description] @content'

# Get all image URLs
curl -s http://example.com | hq 'img @src'

# Extract form input names
curl -s http://example.com | hq 'input @name'

# Get navigation menu items
curl -s http://example.com | hq 'nav a | text'
```

## Why hq?

While `jq` is excellent for JSON, there wasn't a similar tool for HTML. `hq` fills this gap by providing:

- **Intuitive syntax**: If you know CSS selectors and jq, you already know hq
- **HTML-first design**: Built specifically for HTML parsing and extraction
- **Beautiful output**: Syntax-highlighted, properly formatted results
- **Flexible querying**: From simple tag extraction to complex nested selections

## Development

### Setting up the development environment

```bash
# Clone the repository
git clone https://github.com/Julestblt/hq.git
cd hq

# Install in development mode
pip install -e .[dev]

# Run tests
pytest

# Run quality checks
black --check .
flake8 .
mypy hq/
isort --check-only .
```

### Versioning and Releases

This project uses automated versioning and publishing:

- **Automatic releases**: Every push to `main` automatically bumps the patch version, creates a git tag, and publishes to PyPI
- **Manual releases**: Use the "Manual Version Bump" GitHub Action to bump major/minor versions
- **Version management**: Uses `bump2version` to keep version numbers in sync across files

The version is automatically updated in:
- `pyproject.toml`
- `hq/__init__.py`
- `.bumpversion.cfg`

### CI/CD Pipeline

- **Tests**: Run on Python 3.9, 3.10, 3.11, and 3.12
- **Quality checks**: Black, Flake8, MyPy, and isort
- **Automated publishing**: On successful tests, packages are built and published to PyPI

## License

MIT
