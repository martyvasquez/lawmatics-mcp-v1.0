# Lawmatics MCP Server

Model Context Protocol (MCP) server for the Lawmatics legal practice management platform. This server enables LLMs to interact with Lawmatics to manage contacts, matters, tasks, time entries, expenses, and more.

> **🔐 Authentication Note**: Lawmatics uses OAuth 2.0. See the **[OAuth Setup Guide](OAUTH_SETUP_GUIDE.md)** for complete setup instructions including callback URLs and credential configuration.

## Features

### 🔍 Search Operations
- **Contacts**: Search by name, email, phone, or associated matter/company
- **Matters**: Search by name, contact, status, or practice area
- **Tasks**: Search by contact, matter, status, assignee, or due date
- **Companies**: Search by name, email, or phone
- **Time Entries**: Search by contact, matter, user, or date range
- **Expenses**: Search by contact, matter, or date range

### 📋 Retrieval Operations
- Get detailed information for any entity by ID
- List all users in the account
- Access complete entity data including custom fields

### ✏️ Management Operations
- **Create**: Contacts, tasks, time entries, expenses
- **Update**: Contacts, tasks
- **Delete**: Tasks

### 🎯 MCP Resources
Direct URI access to entities:
- `lawmatics://contacts/{contact_id}`
- `lawmatics://matters/{matter_id}`
- `lawmatics://tasks/{task_id}`
- `lawmatics://companies/{company_id}`

### 📝 MCP Prompts
Pre-built workflows for common operations:
- **find-contact-by-phone**: Find all contacts and matters by phone number
- **matter-overview**: Comprehensive matter analysis with tasks and billing
- **create-new-client**: Complete client onboarding workflow
- **daily-task-summary**: Today's tasks and upcoming deadlines
- **billing-report**: Generate time and expense reports
- **matter-search-analysis**: Search and analyze matters by criteria

## Installation

### Prerequisites
- Python 3.12 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- Lawmatics account with API access

### Local Setup

1. **Clone or navigate to the repository**
   ```bash
   cd Lawmatics-MCP
   ```

2. **Install dependencies**
   ```bash
   uv sync
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your LAWMATICS_API_KEY
   ```

4. **Configure OAuth credentials**

   ⚠️ **Lawmatics uses OAuth 2.0 authentication**

   See the **[OAuth Setup Guide](OAUTH_SETUP_GUIDE.md)** for detailed instructions.

   **Quick Start**:
   - Go to Lawmatics Settings → API → OAuth Applications
   - Create new OAuth app with callback URL: `http://localhost:8000/oauth/callback`
   - Copy your Client ID and Client Secret
   - Add them to your `.env` file:
     ```env
     LAWMATICS_CLIENT_ID=your_client_id_here
     LAWMATICS_CLIENT_SECRET=your_client_secret_here
     ```
   - Complete the OAuth flow to get an access token (see OAuth Setup Guide)

5. **Run the server locally**
   ```bash
   uv run python -m app
   ```

   The server will start on `http://localhost:8000/mcp/`

## FastMCP Cloud Deployment

### Deploy to FastMCP Cloud

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial Lawmatics MCP Server"
   git remote add origin <your-repo-url>
   git push -u origin main
   ```

2. **Deploy on FastMCP Cloud**
   - Visit [https://fastmcp.cloud](https://fastmcp.cloud)
   - Sign in with GitHub
   - Click "New Project"
   - Select your repository
   - Configure:
     - **Name**: `lawmatics-mcp` (creates `https://lawmatics-mcp.fastmcp.app/mcp`)
     - **Entrypoint**: `cloud.py:mcp`
     - **Branch**: `main`

3. **Add Environment Variables in FastMCP Cloud Dashboard**
   ```
   LAWMATICS_API_KEY=your_actual_api_key_here
   LAWMATICS_BASE_URL=https://api.lawmatics.com/v1/
   LOG_LEVEL=INFO
   ```

4. **Deploy**
   - FastMCP Cloud will automatically build and deploy
   - Your server will be available at: `https://lawmatics-mcp.fastmcp.app/mcp`

### Automatic Updates
FastMCP Cloud automatically redeploys when you push to your main branch:
```bash
git add .
git commit -m "Update tools"
git push origin main
```

## Usage

### Development Commands

```bash
# Run server locally
uv run python -m app

# Run with FastMCP dev mode (hot reload)
fastmcp dev cloud.py:mcp

# Inspect server structure
fastmcp inspect cloud.py:mcp

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=app --cov-report=term-missing

# Type checking
uv run mypy app/

# Code formatting
uv run ruff format .

# Linting
uv run ruff check .
```

### Example Queries

Once running, you can interact with the MCP server through any MCP-compatible client:

**Find contacts by phone:**
```
Use the find-contact-by-phone prompt with phone_number: 714-917-5140
```

**Search for matters:**
```
Use search_matters tool with practice_area: "Personal Injury" and status: "active"
```

**Create a new task:**
```
Use create_task tool with title: "Follow up with client", matter_id: "123", due_date: "2025-11-01"
```

**Get matter overview:**
```
Use matter-overview prompt with matter_id: "456"
```

## API Coverage

### Supported Entities
- ✅ Contacts (leads, clients, referrers)
- ✅ Matters (cases)
- ✅ Tasks
- ✅ Companies
- ✅ Time Entries
- ✅ Expenses
- ✅ Users

### Supported Operations
- ✅ Search/List with filtering
- ✅ Get by ID
- ✅ Create new entities
- ✅ Update existing entities
- ✅ Delete entities (tasks)

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `LAWMATICS_API_KEY` | Yes | - | Your Lawmatics API key |
| `LAWMATICS_BASE_URL` | No | `https://api.lawmatics.com/v1/` | Lawmatics API base URL |
| `HOST` | No | `0.0.0.0` | Server host |
| `MCP_PORT` | No | `8000` | Server port |
| `LOG_LEVEL` | No | `INFO` | Logging level |
| `DEBUG` | No | `false` | Debug mode |
| `ENVIRONMENT` | No | `production` | Environment name |

## Architecture

### Project Structure
```
Lawmatics-MCP/
├── app/
│   ├── __init__.py           # Package initialization
│   ├── __main__.py          # Entry point
│   ├── config.py            # Configuration management
│   ├── server.py            # Main MCP server
│   └── tools/               # Tool modules
│       ├── __init__.py      # Tools package
│       ├── search.py        # Search operations
│       ├── get.py          # Get operations
│       └── manage.py       # Create/update/delete operations
├── tests/                   # Test suite
├── cloud.py                # FastMCP Cloud entrypoint
├── pyproject.toml          # Dependencies
├── .env.example           # Environment template
└── README.md             # This file
```

### Server Composition
The MCP server uses FastMCP's composition pattern:
- **Main Server**: Status tool, resources, and prompts
- **Search Server**: 6 search tools (contacts, matters, tasks, etc.)
- **Get Server**: 8 retrieval tools (get by ID, list users)
- **Manage Server**: 7 management tools (create, update, delete)

Total: **22 tools + 4 resources + 6 prompts**

## Troubleshooting

### API Key Issues
- Ensure your `LAWMATICS_API_KEY` is set correctly in `.env` or FastMCP Cloud
- Verify the key is valid by testing it with curl:
  ```bash
  curl -X GET "https://api.lawmatics.com/v1/users" \
    -H "Authorization: Bearer YOUR_API_KEY"
  ```

### Connection Issues
- Check that `LAWMATICS_BASE_URL` points to the correct API endpoint
- Verify network connectivity to api.lawmatics.com
- Check FastMCP Cloud logs for detailed error messages

### Tool Discovery
- Run `fastmcp inspect cloud.py:mcp` to verify all tools are loaded
- Ensure sub-servers are importing correctly in `app/tools/__init__.py`

## Support

- **Lawmatics API Documentation**: [https://docs.lawmatics.com](https://docs.lawmatics.com)
- **Lawmatics API Support**: api@lawmatics.com
- **FastMCP Documentation**: [https://gofastmcp.com](https://gofastmcp.com)
- **MCP Specification**: [https://spec.modelcontextprotocol.io/](https://spec.modelcontextprotocol.io/)

## License

[Your License Here]

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
