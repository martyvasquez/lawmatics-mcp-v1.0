#!/usr/bin/env python3
"""Lawmatics MCP Server - FastMCP Implementation."""

import asyncio
import os
from datetime import UTC, datetime
from pathlib import Path
import sys
import tomllib
from typing import Annotated as _Annotated, Any

from fastmcp import Context as _Context, FastMCP
from loguru import logger
import psutil
from starlette.responses import JSONResponse
from starlette.routing import Route

from app.config import config
from app.tools import get_server, manage_server, search_server

# Configure logging
logger.info("Initializing Lawmatics MCP Server")


def get_version() -> str:
    """Get the version from pyproject.toml.

    Returns:
        The version string from pyproject.toml or 'unknown' if not found.
    """
    try:
        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
        with pyproject_path.open("rb") as f:
            data = tomllib.load(f)
        return data.get("project", {}).get("version", "unknown")
    except Exception:
        return "unknown"


def is_docker() -> bool:
    """Check if running inside a Docker container.

    Returns:
        True if running inside Docker, False otherwise.
    """
    return Path("/.dockerenv").exists() or (
        Path("/proc/1/cgroup").exists()
        and any(
            "docker" in line for line in Path("/proc/1/cgroup").open(encoding="utf-8")
        )
    )


mcp_auth = None
_auth_env = os.getenv("FASTMCP_SERVER_AUTH")
if _auth_env == "fastmcp.server.auth.providers.auth0.Auth0Provider":
    try:
        from fastmcp.server.auth.providers.auth0 import Auth0Provider  # type: ignore
        auth_kwargs: dict[str, Any] = {
            "config_url": os.environ["FASTMCP_SERVER_AUTH_AUTH0_CONFIG_URL"],
            "client_id": os.environ["FASTMCP_SERVER_AUTH_AUTH0_CLIENT_ID"],
            "client_secret": os.environ["FASTMCP_SERVER_AUTH_AUTH0_CLIENT_SECRET"],
            "audience": os.environ["FASTMCP_SERVER_AUTH_AUTH0_AUDIENCE"],
            "base_url": os.environ["FASTMCP_SERVER_AUTH_AUTH0_BASE_URL"],
        }
        issuer = os.getenv("FASTMCP_SERVER_AUTH_AUTH0_ISSUER_URL")
        if issuer:
            auth_kwargs["issuer_url"] = issuer
        mcp_auth = Auth0Provider(**auth_kwargs)
        logger.info("Configured Auth0 OAuth provider for MCP server")
    except KeyError as exc:
        missing = exc.args[0]
        raise RuntimeError(
            f"Missing required Auth0 configuration environment variable: {missing}"
        ) from exc
    except ImportError as exc:
        raise RuntimeError(
            "fastmcp Auth0 provider is not available. Ensure fastmcp>=2.13 is installed."
        ) from exc

# Create main server instance
_mcp_kwargs: dict[str, Any] = {
    "name": "Lawmatics MCP Server",
    "instructions": (
        "Model Context Protocol server providing LLMs with access to the Lawmatics legal practice management platform. "
        "This server enables comprehensive management of legal contacts (leads, clients, referrers), "
        "matters (cases), tasks, companies, time entries, and expenses. "
        "Available operations include: searching across all entity types, retrieving specific entities by ID, "
        "creating new entities, updating existing data, and managing relationships between entities. "
        "Perfect for legal CRM automation, case management, billing, and practice analytics. "
        "All tools support filtering by phone number, email, matter ID, and other criteria."
    ),
}

if mcp_auth is not None:
    _mcp_kwargs["auth"] = mcp_auth

mcp: FastMCP[Any] = FastMCP(**_mcp_kwargs)

if mcp_auth is not None:
    try:
        auth_routes = mcp_auth.get_routes(mcp_path="/mcp")
        mcp._additional_http_routes.extend(auth_routes)
        logger.info("Registered Auth0 discovery routes for MCP server")

        def _openid_configuration_route(request: Any) -> JSONResponse:
            base_url = os.environ["FASTMCP_SERVER_AUTH_AUTH0_BASE_URL"].rstrip("/")
            issuer = os.getenv("FASTMCP_SERVER_AUTH_AUTH0_ISSUER_URL", base_url).rstrip(
                "/"
            )

            config_json = {
                "issuer": issuer,
                "authorization_endpoint": f"{base_url}/authorize",
                "token_endpoint": f"{base_url}/token",
                "registration_endpoint": f"{base_url}/register",
                "response_types_supported": ["code"],
                "grant_types_supported": ["authorization_code"],
                "token_endpoint_auth_methods_supported": [
                    "none",
                    "client_secret_post",
                ],
                "code_challenge_methods_supported": ["S256"],
                "scopes_supported": [
                    "openid",
                    "profile",
                    "email",
                    "token",
                ],
                "claims_supported": ["sub", "api_token"],
            }
            return JSONResponse(config_json)

        mcp._additional_http_routes.append(
            Route(
                "/.well-known/openid-configuration",
                _openid_configuration_route,
                methods=["GET"],
            )
        )
    except Exception as exc:
        logger.warning(f"Failed to register Auth0 routes: {exc}")


@mcp.tool()
def status() -> dict[str, Any]:
    """Check the status of the Lawmatics MCP server.

    Returns:
        A dictionary containing server status, system metrics, and service information.
    """
    logger.info("Status check requested")

    # Get system info using psutil
    process = psutil.Process()
    process_start = datetime.fromtimestamp(process.create_time(), tz=UTC)
    uptime_seconds = (datetime.now(UTC) - process_start).total_seconds()

    # Format uptime as human readable
    hours, remainder = divmod(int(uptime_seconds), 3600)
    minutes, seconds = divmod(remainder, 60)
    uptime = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    # Docker and environment info
    docker_info = is_docker()
    environment = "docker" if docker_info else "native"

    return {
        "status": "healthy",
        "service": "Lawmatics MCP Server",
        "version": get_version(),
        "timestamp": datetime.now(UTC).isoformat(),
        "environment": {
            "runtime": environment,
            "docker": docker_info,
            "python_version": sys.version.split()[0],
        },
        "system": {
            "process_uptime": uptime,
            "memory_mb": round(process.memory_info().rss / 1024 / 1024, 1),
            "cpu_percent": round(process.cpu_percent(interval=0.1), 1),
        },
        "server": {
            "tools_available": ["search", "get", "manage"],
            "transport": "streamable-http",
            "api_base": config.lawmatics_base_url,
            "host": config.host,
            "port": config.mcp_port,
        },
    }


# Server composition setup
_initialized = False


async def _ensure_setup() -> None:
    """Ensure server setup runs exactly once.

    This function lazily loads sub-servers, which happens when:
    - main() is called for local development
    - FastMCP Cloud starts the server
    """
    global _initialized
    if not _initialized:
        logger.info("Setting up Lawmatics MCP server sub-servers")

        # Import sub-servers without prefixes for better UX
        await mcp.import_server(search_server)
        logger.info("Imported search server tools")

        await mcp.import_server(get_server)
        logger.info("Imported get server tools")

        await mcp.import_server(manage_server)
        logger.info("Imported manage server tools")

        _initialized = True
        logger.info("Server setup complete - all sub-servers loaded")


# ============================================================================
# Resources and Prompts (registered at module level for fastmcp inspect)
# ============================================================================

import httpx as _httpx
from pydantic import Field as _Field

_API_KEY = os.getenv("LAWMATICS_ACCESS_TOKEN") or os.getenv("LAWMATICS_API_KEY")


@mcp.resource(
    uri="lawmatics://contacts/{contact_id}",
    name="Contact by ID",
    description="Get a specific contact by ID",
    mime_type="application/json",
)
async def get_contact_resource(
    contact_id: _Annotated[str, _Field(description="The contact ID")],
    ctx: _Context | None = None,
) -> dict[str, Any]:
    """Get a contact by ID from Lawmatics."""
    if not _API_KEY:
        raise ValueError("LAWMATICS_ACCESS_TOKEN or LAWMATICS_API_KEY not found")

    headers = {"Authorization": f"Bearer {_API_KEY}"}
    async with _httpx.AsyncClient() as client:
        response = await client.get(
            f"{config.lawmatics_base_url}contacts/{contact_id}",
            headers=headers,
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()


@mcp.resource(
    uri="lawmatics://matters/{matter_id}",
    name="Matter by ID",
    description="Get a specific matter/case by ID",
    mime_type="application/json",
)
async def get_matter_resource(
    matter_id: _Annotated[str, _Field(description="The matter ID")],
    ctx: _Context | None = None,
) -> dict[str, Any]:
    """Get a matter by ID from Lawmatics."""
    if not _API_KEY:
        raise ValueError("LAWMATICS_ACCESS_TOKEN or LAWMATICS_API_KEY not found")

    headers = {"Authorization": f"Bearer {_API_KEY}"}
    async with _httpx.AsyncClient() as client:
        response = await client.get(
            f"{config.lawmatics_base_url}matters/{matter_id}",
            headers=headers,
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()


@mcp.resource(
    uri="lawmatics://tasks/{task_id}",
    name="Task by ID",
    description="Get a specific task by ID",
    mime_type="application/json",
)
async def get_task_resource(
    task_id: _Annotated[str, _Field(description="The task ID")],
    ctx: _Context | None = None,
) -> dict[str, Any]:
    """Get a task by ID from Lawmatics."""
    if not _API_KEY:
        raise ValueError("LAWMATICS_ACCESS_TOKEN or LAWMATICS_API_KEY not found")

    headers = {"Authorization": f"Bearer {_API_KEY}"}
    async with _httpx.AsyncClient() as client:
        response = await client.get(
            f"{config.lawmatics_base_url}tasks/{task_id}",
            headers=headers,
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()


@mcp.resource(
    uri="lawmatics://companies/{company_id}",
    name="Company by ID",
    description="Get a specific company by ID",
    mime_type="application/json",
)
async def get_company_resource(
    company_id: _Annotated[str, _Field(description="The company ID")],
    ctx: _Context | None = None,
) -> dict[str, Any]:
    """Get a company by ID from Lawmatics."""
    if not _API_KEY:
        raise ValueError("LAWMATICS_ACCESS_TOKEN or LAWMATICS_API_KEY not found")

    headers = {"Authorization": f"Bearer {_API_KEY}"}
    async with _httpx.AsyncClient() as client:
        response = await client.get(
            f"{config.lawmatics_base_url}companies/{company_id}",
            headers=headers,
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()


# ============================================================================
# Prompts
# ============================================================================


@mcp.prompt(
    name="find-contact-by-phone",
    description="Find all contacts and matters associated with a phone number",
)
async def find_contact_by_phone_prompt(
    phone_number: _Annotated[str, _Field(description="The phone number to search for")],
) -> list[str]:
    """Generate a prompt for finding contacts by phone number."""
    return [
        f"I need to find all contacts and matters associated with phone number: {phone_number}",
        "",
        "Please follow these steps:",
        f"1. Use 'search_contacts' tool with phone: '{phone_number}' to find matching contacts",
        "2. For each contact found:",
        "   - Display the contact's full name, email, and current status",
        "   - Note any associated company or organization",
        "3. If contacts are found, use their contact IDs to search for associated matters:",
        "   - For each contact, use 'search_matters' with the contact_id parameter",
        "   - List all matters with their status and practice area",
        "4. Provide a summary of:",
        "   - Total contacts found with this phone number",
        "   - Total matters associated with these contacts",
        "   - Current status of each matter (active, closed, etc.)",
    ]


@mcp.prompt(
    name="matter-overview",
    description="Get comprehensive overview of a matter including all associated data",
)
async def matter_overview_prompt(
    matter_id: _Annotated[str, _Field(description="The matter ID to analyze")],
) -> list[str]:
    """Generate a prompt for comprehensive matter overview."""
    return [
        f"I need a comprehensive overview of matter ID: {matter_id}",
        "",
        "STEP 1: Matter Details",
        f"  - Use 'get_matter' tool to retrieve full matter information",
        "  - Extract: matter name, status, practice area, dates, and description",
        "",
        "STEP 2: Associated Contacts",
        f"  - Use 'search_contacts' with matter_id: '{matter_id}' to find all related contacts",
        "  - List primary contact(s), their role, and contact information",
        "",
        "STEP 3: Active Tasks",
        f"  - Use 'search_tasks' with matter_id: '{matter_id}' to find all tasks",
        "  - Categorize by status (pending vs. completed)",
        "  - Identify overdue tasks if any",
        "  - List upcoming tasks with due dates",
        "",
        "STEP 4: Time & Billing",
        f"  - Use 'search_time_entries' with matter_id: '{matter_id}' to get billable hours",
        f"  - Use 'search_expenses' with matter_id: '{matter_id}' to get expenses",
        "  - Calculate total hours logged and total expenses",
        "",
        "STEP 5: Summary",
        "  - Provide executive summary with key statistics",
        "  - Flag any issues (overdue tasks, pending items)",
        "  - Recommend next actions if applicable",
    ]


@mcp.prompt(
    name="create-new-client",
    description="Workflow for creating a new client with complete information",
)
async def create_new_client_prompt(
    first_name: _Annotated[str, _Field(description="Client's first name")],
    last_name: _Annotated[str, _Field(description="Client's last name")],
    email: _Annotated[str, _Field(description="Client's email address")],
    phone: _Annotated[str, _Field(description="Client's phone number")],
) -> list[str]:
    """Generate a prompt for creating a new client."""
    return [
        f"I need to create a new client: {first_name} {last_name}",
        f"Email: {email}",
        f"Phone: {phone}",
        "",
        "STEP 1: Check for Existing Contact",
        f"  - Use 'search_contacts' with email: '{email}' and phone: '{phone}'",
        "  - If contact exists, ask if update is needed instead",
        "",
        "STEP 2: Create Contact",
        "  - Use 'create_contact' tool with the following:",
        f"    - first_name: '{first_name}'",
        f"    - last_name: '{last_name}'",
        f"    - email: '{email}'",
        f"    - phone: '{phone}'",
        "    - contact_type: 'client'",
        "  - Capture the returned contact_id",
        "",
        "STEP 3: Confirm Creation",
        "  - Use 'get_contact' with the new contact_id to verify",
        "  - Display the complete contact record",
        "",
        "STEP 4: Ask About Next Steps",
        "  - Does this client need a matter/case created?",
        "  - Should any tasks be created for follow-up?",
    ]


@mcp.prompt(
    name="daily-task-summary",
    description="Get summary of today's tasks and upcoming deadlines",
)
async def daily_task_summary_prompt(
    user_id: _Annotated[str, _Field(description="User ID to get tasks for")] = "",
) -> list[str]:
    """Generate a prompt for daily task summary."""
    user_filter = f" for user {user_id}" if user_id else " for all users"
    messages = [
        f"I need a daily task summary{user_filter}",
        "",
        "STEP 1: Today's Tasks",
        f"  - Use 'search_tasks' with due_date_before set to today",
    ]

    if user_id:
        messages.append(f"  - Filter by assigned_to: '{user_id}'")

    messages.extend([
        "  - Group by status (pending, completed)",
        "",
        "STEP 2: Overdue Tasks",
        "  - Use 'search_tasks' with due_date_before set to yesterday",
        "  - Filter for status: 'pending'",
        "  - These are critical overdue items",
        "",
        "STEP 3: Upcoming This Week",
        "  - Use 'search_tasks' with due_date_before set to 7 days from now",
        "  - Focus on pending tasks",
        "",
        "STEP 4: Summary Report",
        "  - Total overdue tasks (with count)",
        "  - Total tasks due today",
        "  - Total tasks due this week",
        "  - Group by matter/contact if applicable",
        "  - Provide prioritized action list",
    ])

    return messages


@mcp.prompt(
    name="billing-report",
    description="Generate billing report for a matter or client",
)
async def billing_report_prompt(
    matter_id: _Annotated[str, _Field(description="Matter ID for billing report")] = "",
    contact_id: _Annotated[str, _Field(description="Contact ID for billing report")] = "",
    start_date: _Annotated[str, _Field(description="Start date (YYYY-MM-DD)")] = "",
    end_date: _Annotated[str, _Field(description="End date (YYYY-MM-DD)")] = "",
) -> list[str]:
    """Generate a prompt for billing report."""
    if not matter_id and not contact_id:
        return ["Error: Must provide either matter_id or contact_id for billing report"]

    filter_desc = f"matter {matter_id}" if matter_id else f"contact {contact_id}"
    date_range = f" from {start_date} to {end_date}" if start_date and end_date else ""

    return [
        f"I need a billing report for {filter_desc}{date_range}",
        "",
        "STEP 1: Retrieve Time Entries",
        f"  - Use 'search_time_entries' filtered by {filter_desc}",
        "  - Add date filters if provided",
        "  - Calculate total billable hours",
        "  - Group by user/attorney",
        "",
        "STEP 2: Retrieve Expenses",
        f"  - Use 'search_expenses' filtered by {filter_desc}",
        "  - Add date filters if provided",
        "  - Calculate total billable expenses",
        "  - Group by category",
        "",
        "STEP 3: Get Matter/Contact Details",
        "  - Use appropriate get tool for context",
        "  - Include client name, matter name/description",
        "",
        "STEP 4: Generate Report",
        "  - Create formatted billing summary with:",
        "    - Client/Matter information",
        "    - Time entries table (date, user, hours, description)",
        "    - Expenses table (date, category, amount, description)",
        "    - Subtotals by attorney/category",
        "    - Grand total (time + expenses)",
        "  - Note: rates may need to be added manually from firm settings",
    ]


@mcp.prompt(
    name="matter-search-analysis",
    description="Search for matters by criteria and provide analysis",
)
async def matter_search_analysis_prompt(
    practice_area: _Annotated[str, _Field(description="Practice area to filter by")] = "",
    status: _Annotated[str, _Field(description="Matter status to filter by")] = "",
) -> list[str]:
    """Generate a prompt for matter search and analysis."""
    return [
        f"I need to search and analyze matters{f' in practice area: {practice_area}' if practice_area else ''}{f' with status: {status}' if status else ''}",
        "",
        "STEP 1: Search Matters",
        "  - Use 'search_matters' with specified filters",
        "  - Set appropriate limit (suggest 50 for analysis)",
        "",
        "STEP 2: Basic Analysis",
        "  - Count total matters found",
        "  - Breakdown by status if not filtered",
        "  - Breakdown by practice area if not filtered",
        "",
        "STEP 3: Activity Analysis",
        "  - For each matter, check for recent activity:",
        "    - Use 'search_tasks' to count pending tasks",
        "    - Use 'search_time_entries' to check recent billing",
        "  - Identify stagnant matters (no recent activity)",
        "",
        "STEP 4: Summary Report",
        "  - Total matters by category",
        "  - Active vs. inactive matters",
        "  - Matters with pending tasks",
        "  - Recommendations for follow-up",
    ]


async def main() -> None:
    """Run the Lawmatics MCP server with streamable-http transport."""
    # Ensure sub-servers are loaded before starting
    await _ensure_setup()

    logger.info("Starting Lawmatics MCP server with streamable-http transport")
    logger.info(
        f"Server configuration: host={config.host}, port={config.mcp_port}, log_level={config.log_level}"
    )

    try:
        await mcp.run_async(
            transport="streamable-http",
            host=config.host,
            port=config.mcp_port,
            path="/mcp/",
            log_level=config.log_level.lower(),
        )
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        raise


if __name__ == "__main__":
    logger.info("Starting Lawmatics MCP server")
    asyncio.run(main())
