# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a MySQL Model Context Protocol (MCP) server implementation that enables secure interaction between AI applications and MySQL databases. The project is a Python package designed to be used as a bridge between AI clients (like Claude Desktop) and MySQL databases, providing controlled access through the MCP specification.

## Development Commands

### Testing
```bash
# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src/mysql_mcp_server

# Run specific test file
uv run pytest tests/test_server.py

# Run tests in verbose mode
uv run pytest -v
```

### Code Quality
```bash
# Format code with black
uv run black src/ tests/

# Sort imports with isort
uv run isort src/ tests/

# Type checking with mypy
uv run mypy src/
```

### Installation & Setup
```bash
# Install all dependencies including development dependencies
uv sync --dev

# Install only production dependencies
uv sync

# Add new dependencies
uv add package_name

# Add development dependencies
uv add --dev package_name
```

### Running the Server
The server is not meant to be run standalone but through MCP clients. For debugging:
```bash
# Run server with uv
uv run mysql_mcp_server

# Or run the module directly
uv run python -m mysql_mcp_server

# For development/debugging
uv run --dev mysql_mcp_server
```

## Architecture

### Core Components

**`src/mysql_mcp_server/server.py`** - Main server implementation containing:
- MCP server initialization and configuration
- Database connection management with environment-based config
- Resource handlers (`list_resources`, `read_resource`) for table discovery and data access
- Tool handlers (`list_tools`, `call_tool`) for SQL query execution
- Error handling and logging throughout all operations

**`src/mysql_mcp_server/__init__.py`** - Package entry point that exposes the main async entry function

### MCP Protocol Implementation

The server implements three core MCP capabilities:

1. **Resources**: Exposes MySQL tables as resources with URI format `mysql://{table_name}/data`
2. **Tools**: Provides `execute_sql` tool for running arbitrary SQL queries
3. **Server Management**: Handles MCP protocol communication via stdio

### Database Integration

- Uses `mysql-connector-python` for database connectivity
- Supports configurable charset/collation for MySQL version compatibility
- Implements proper connection pooling and error handling
- Provides transaction control with autocommit enabled by default

### Security Architecture

The codebase emphasizes security through:
- Environment variable-based configuration (never hardcoded credentials)
- Structured error handling that doesn't expose internal details
- Support for restricted database users with minimal permissions
- Comprehensive logging for audit trails

## Configuration

### Required Environment Variables
```bash
MYSQL_HOST=localhost          # Database host
MYSQL_PORT=3306              # Database port (optional, defaults to 3306)
MYSQL_USER=your_username     # Database user
MYSQL_PASSWORD=your_password # Database password
MYSQL_DATABASE=your_database # Target database
```

### Optional Environment Variables
```bash
MYSQL_CHARSET=utf8mb4                    # Character set (defaults to utf8mb4)
MYSQL_COLLATION=utf8mb4_unicode_ci      # Collation (defaults to utf8mb4_unicode_ci)
MYSQL_SQL_MODE=TRADITIONAL              # SQL mode (defaults to TRADITIONAL)
```

## Testing Strategy

Tests use pytest with async support and include:
- Unit tests for server initialization and tool validation
- Integration tests that gracefully skip when database connection unavailable
- Error handling validation for invalid inputs
- Mock-friendly architecture for testing without live database

The test suite is designed to run in CI/CD environments where database connections may not be available, using skipif decorators appropriately.

## Security Considerations

When working with this codebase:
- Always use dedicated MySQL users with minimal required permissions
- Never commit database credentials or configuration files with sensitive data
- Follow the principle of least privilege for database access
- Test with restricted users to ensure the server works with limited permissions
- Review SECURITY.md for detailed MySQL user configuration guidelines

## Package Structure

This follows Python package best practices:
- `pyproject.toml` defines package metadata and dependencies
- Entry point defined as `mysql_mcp_server = "mysql_mcp_server:main"`
- Minimal dependencies focused on core functionality (mcp, mysql-connector-python)
- Development dependencies separated in requirements-dev.txt
