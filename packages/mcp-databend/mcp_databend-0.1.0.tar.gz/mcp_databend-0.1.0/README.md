# MCP Server for Databend

Model Context Protocol server for Databend database interactions.

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

### Step 2: Install and Run

```bash
# Clone or download this repository
git clone https://github.com/datafuselabs/mcp-server-databend
cd mcp-server-databend

# Install dependencies
uv sync --all-groups --all-extras

# Set your connection string
export DATABEND_DSN="your-connection-string-here"

# Test the server
uv run mcp dev server.py
```

### Step 3: Configure Your MCP Client

#### Standard MCP Configuration

**Recommended: Using uv with local path**

This method provides Python version management with local installation:

```json
{
  "mcpServers": {
    "mcp-databend": {
      "command": "uv",
      "args": [
        "run",
        "--python",
        "3.12",
        "/absolute/path/to/mcp-server-databend/server.py"
      ],
      "env": {
        "DATABEND_DSN": "your-connection-string-here"
      }
    }
  }
}
```

**How to get the path:**
```bash
# After cloning the repository
cd mcp-server-databend
pwd  # This shows your absolute path
# Example: /Users/username/mcp-server-databend
# Use: /Users/username/mcp-server-databend/server.py
```

**Alternative: Using system Python**

If you prefer to use system Python:

```json
{
  "mcpServers": {
    "mcp-databend": {
      "command": "python",
      "args": ["/absolute/path/to/mcp-server-databend/server.py"],
      "env": {
        "DATABEND_DSN": "your-connection-string-here"
      }
    }
  }
}
```

**Future: Using uv (when published)**

Once published to PyPI, you'll be able to use:

```json
{
  "mcpServers": {
    "mcp-databend": {
      "command": "uv",
      "args": [
        "run",
        "--with",
        "mcp-databend",
        "--python",
        "3.12",
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
