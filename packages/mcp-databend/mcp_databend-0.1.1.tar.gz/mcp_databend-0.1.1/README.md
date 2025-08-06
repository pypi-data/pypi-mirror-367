# MCP Server for Databend

[![PyPI - Version](https://img.shields.io/pypi/v/mcp-databend)](https://pypi.org/project/mcp-databend)

An MCP server for Databend database interactions.

## What You Can Do

- **execute_sql** - Execute SQL queries with timeout protection
- **show_databases** - List all databases
- **show_tables** - List tables in a database (with optional filter)
- **describe_table** - Get table schema information

## How to Use

### Step 1: Get Databend Connection

**Recommended**: Sign up for [Databend Cloud](https://databend.com) (free tier available)

Or use your own Databend instance:

| Deployment | Connection String Example |
|------------|---------------------------|
| **Databend Cloud** | `databend://cloudapp:pass@host:443/database?warehouse=wh` |
| **Self-hosted** | `databend://user:pass@localhost:8000/database?sslmode=disable` |

### Step 2: Install

The package is available on [PyPI](https://pypi.org/project/mcp-databend/):

```bash
# Install with uv (recommended)
uv add mcp-databend

# Or install with pip
pip install mcp-databend

# Test the installation
mcp-databend --help
```

### Step 3: Configure Your MCP Client

#### Standard MCP Configuration

**Using uv (Recommended)**

```json
{
  "mcpServers": {
    "mcp-databend": {
      "command": "uv",
      "args": [
        "run",
        "--with",
        "mcp-databend",
        "mcp-databend"
      ],
      "env": {
        "DATABEND_DSN": "your-connection-string-here"
      }
    }
  }
}
```



#### Popular MCP Clients

- **Continue.dev** (VS Code Extension):
  - Add to `~/.continue/config.json`
  - Provides AI coding assistance with database access

- **Zed Editor**:
  - Configure in Settings → Extensions → MCP
  - Modern code editor with built-in AI features

- **Cursor IDE**:
  - Add to MCP configuration in settings
  - AI-powered code editor

- **Open WebUI**:
  - Self-hosted ChatGPT-like interface
  - Configure in MCP settings

- **MCP Inspector**:
  - Development tool for testing MCP servers
  - Run: `npx @modelcontextprotocol/inspector`

### Step 4: Start Using

Once configured, you can ask your AI assistant to:
- "Show me all databases"
- "List tables in the sales database"
- "Describe the users table structure"
- "Run this SQL query: SELECT * FROM products LIMIT 10"

## Development

### Project Structure

```
mcp-databend/
├── mcp_databend/
│   ├── __init__.py     # Package initialization
│   ├── main.py         # Main entry point
│   ├── server.py       # MCP server implementation
│   └── env.py          # Environment configuration
├── pyproject.toml      # Project configuration
└── README.md           # This file
```

### Local Development

```bash
# Clone the repository
git clone https://github.com/databendlabs/mcp-databend
cd mcp-databend

# Install dependencies
uv sync --all-groups --all-extras

# Run in development mode
uv run mcp dev server.py

# Or run the main module directly
uv run python -m mcp_databend.main
```

### Building and Testing

```bash
# Build the package
uv build

# Test the built package
uv run --with ./dist/mcp_databend-0.1.0-py3-none-any.whl mcp-databend
```
