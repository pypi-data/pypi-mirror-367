---
inclusion: always
---

# Ebook-MCP Project Development Guide

## Project Overview

Ebook-MCP is a Model Context Protocol (MCP) based e-book processing server that supports EPUB and PDF format e-book processing. The project is developed in Python using the FastMCP framework to build the MCP server.

## Core Architecture

```
Agent Layer
├── Translation Strategy
├── Style Consistency Check
└── LLM Call & Interaction

MCP Tool Layer
├── EPUB Tools
│   ├── get_all_epub_files
│   ├── get_epub_metadata
│   ├── get_epub_toc
│   ├── get_epub_chapter_markdown
│   └── get_epub_chapter_markdown_fixed
└── PDF Tools
    ├── get_all_pdf_files
    ├── get_pdf_metadata
    ├── get_pdf_toc
    ├── get_pdf_page_text
    ├── get_pdf_page_markdown
    └── get_pdf_chapter_content

System Base Layer
├── File Reading
├── ebooklib Parsing (EPUB)
├── PyMuPDF Parsing (PDF)
└── File Path Storage/Check
```

## Development Standards

### Code Style
- Use Python 3.10+ syntax features
- Follow PEP 8 code style guidelines
- Use type annotations (Type Hints)
- Functions and classes must include detailed docstrings
- Error handling should use specific exception types
- **All code comments and docstrings must be written in English**
- **All description in README.md must be written in English**

### Project Structure
```
src/ebook_mcp/
├── __init__.py
├── main.py              # MCP server main entry point
├── tools/               # Tool modules
│   ├── epub_helper.py   # EPUB processing tools
│   ├── pdf_helper.py    # PDF processing tools
│   └── logger_config.py # Logging configuration
└── tests/               # Test files
```

### Dependency Management
- Use `uv` as package manager
- Core dependencies: ebooklib, PyMuPDF, beautifulsoup4, html2text, fastmcp
- Development dependencies: pytest, uvicorn, starlette

## MCP Tool Development Guide

### Tool Function Standards
1. All tool functions must use the `@mcp.tool()` decorator
2. Function parameters and return values must have clear type annotations
3. Must include detailed docstrings with parameter descriptions, return value descriptions, and exception descriptions
4. Error handling should be specific, distinguishing FileNotFoundError from other exceptions

### Example Tool Function Template
```python
@mcp.tool()
def tool_function_name(param: str) -> ReturnType:
    """Brief description of the tool function.

    Args:
        param: Parameter description, including example format

    Returns:
        ReturnType: Return value description

    Raises:
        FileNotFoundError: Raised when file does not exist
        Exception: Raised for other parsing errors
    """
    logger.debug(f"Calling tool_function_name: {param}")
    try:
        # Implementation logic
        return result
    except FileNotFoundError as e:
        raise FileNotFoundError(str(e))
    except Exception as e:
        raise Exception(str(e))
```

## File Processing Best Practices

### EPUB Processing
- Use `ebooklib` library for EPUB file parsing
- Support metadata extraction, table of contents retrieval, and chapter content extraction
- Convert chapter content to Markdown format output
- Handle subchapter truncation issues, recommend using `get_epub_chapter_markdown_fixed`

### PDF Processing
- Use `PyMuPDF` (fitz) as the primary PDF processing library
- Support content extraction by page number and chapter title
- Provide both plain text and Markdown format output

### Error Handling
- File not found: Raise `FileNotFoundError`
- File format errors: Raise specific `Exception`
- Log detailed debug information

## Logging Configuration

The project uses Python's standard logging module:
- Log files stored in `logs/` directory
- Filename format: `ebook-mcp_server_YYYYMMDD_HHMMSS.log`
- Output to both file and console
- Debug level: DEBUG

## Testing Guide

### Running Tests
```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest src/ebook_mcp/tests/test_epub_helper.py
```

### Development Mode Startup
```bash
# Start MCP server in development mode
uv run mcp dev src/ebook_mcp/main.py

# Use inspector for debugging
npx @modelcontextprotocol/inspector uv --directory . run src/ebook_mcp/main.py
```

## Common Issue Resolution

### EPUB Subchapter Truncation Issue
- Problem: Content truncation may occur when using `get_epub_chapter_markdown`
- Solution: Use `get_epub_chapter_markdown_fixed` as replacement

### PDF Table of Contents Parsing Issue
- Problem: Some PDF files lack table of contents information
- Solution: Provide page-based extraction as fallback option

### Dependency Import Issues
- Use try-except blocks to wrap optional dependency imports
- Provide clear error messages

