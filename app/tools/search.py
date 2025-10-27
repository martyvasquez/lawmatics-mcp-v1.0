"""Search tools for Lawmatics MCP server."""

import os
from typing import Annotated, Any

from dotenv import load_dotenv
from fastmcp import Context, FastMCP
import httpx
from loguru import logger
from pydantic import Field

from app.config import config

# Load environment variables
load_dotenv()

# Get API key from environment
API_KEY = os.getenv("LAWMATICS_API_KEY")

# Create the search server
search_server: FastMCP[Any] = FastMCP(
    name="Lawmatics Search Server",
    instructions=(
        "Search server for Lawmatics legal practice management platform. "
        "This server enables searching across contacts, matters, tasks, companies, "
        "time entries, and expenses. "
        "Search parameters include name filters, email/phone lookups, date ranges, and status filters. "
        "Results are returned with detailed metadata and can be filtered by various criteria."
    ),
)


@search_server.tool()
async def search_contacts(
    name: Annotated[str, Field(description="Search for contacts by name")] = "",
    email: Annotated[str, Field(description="Search for contacts by email address")] = "",
    phone: Annotated[str, Field(description="Search for contacts by phone number")] = "",
    matter_id: Annotated[str, Field(description="Filter contacts by matter ID")] = "",
    company_id: Annotated[str, Field(description="Filter contacts by company ID")] = "",
    limit: Annotated[int, Field(description="Maximum results to return", ge=1, le=100)] = 20,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Search for contacts in Lawmatics.

    This tool searches across contacts (leads, clients, referrers) in your Lawmatics account.
    Best for finding people by name, email, phone number, or associated matter/company.
    Supports filtering by multiple criteria simultaneously.

    Args:
        name: Search contacts by name (partial match supported)
        email: Search contacts by email address
        phone: Search contacts by phone number
        matter_id: Filter to contacts associated with a specific matter
        company_id: Filter to contacts associated with a specific company
        limit: Maximum number of results to return (1-100)
        ctx: Optional FastMCP context for logging

    Returns:
        Dictionary containing search results with contact details including
        name, email, phone, status, matter associations, and metadata.

    Raises:
        ValueError: If LAWMATICS_API_KEY is not found in environment variables.
    """
    search_params = []
    if name:
        search_params.append(f"name: {name}")
    if email:
        search_params.append(f"email: {email}")
    if phone:
        search_params.append(f"phone: {phone}")

    search_msg = f"Searching contacts with {', '.join(search_params) if search_params else 'no filters'}"

    if ctx:
        await ctx.info(search_msg)
    else:
        logger.info(search_msg)

    if not API_KEY:
        error_msg = "LAWMATICS_API_KEY not found in environment variables"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise ValueError(error_msg)

    params: dict[str, Any] = {}
    if name:
        params["name"] = name
    if email:
        params["email"] = email
    if phone:
        params["phone"] = phone
    if matter_id:
        params["matter_id"] = matter_id
    if company_id:
        params["company_id"] = company_id
    if limit:
        params["limit"] = limit

    headers = {"Authorization": f"Bearer {API_KEY}"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{config.lawmatics_base_url}contacts",
                params=params,
                headers=headers,
                timeout=config.lawmatics_timeout,
            )
            response.raise_for_status()
            data = response.json()

            result_count = len(data) if isinstance(data, list) else data.get("total", 0)
            if ctx:
                await ctx.info(f"Found {result_count} contacts")
            else:
                logger.info(f"Found {result_count} contacts")

            return data

    except httpx.HTTPStatusError as e:
        error_msg = f"HTTP error {e.response.status_code}: {e.response.text}"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise
    except Exception as e:
        error_msg = f"Search error: {e}"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise


@search_server.tool()
async def search_matters(
    name: Annotated[str, Field(description="Search for matters by name/title")] = "",
    contact_id: Annotated[str, Field(description="Filter matters by contact ID")] = "",
    status: Annotated[str, Field(description="Filter by matter status (e.g., 'active', 'closed')")] = "",
    practice_area: Annotated[str, Field(description="Filter by practice area")] = "",
    limit: Annotated[int, Field(description="Maximum results to return", ge=1, le=100)] = 20,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Search for matters (cases) in Lawmatics.

    This tool searches across legal matters/cases in your Lawmatics account.
    Best for finding cases by name, associated contact, status, or practice area.
    Matters represent the legal cases or projects your firm is handling.

    Args:
        name: Search matters by name/title
        contact_id: Filter to matters associated with a specific contact
        status: Filter by matter status
        practice_area: Filter by practice area/type of case
        limit: Maximum number of results to return (1-100)
        ctx: Optional FastMCP context for logging

    Returns:
        Dictionary containing search results with matter details including
        name, status, practice area, associated contacts, dates, and metadata.

    Raises:
        ValueError: If LAWMATICS_API_KEY is not found in environment variables.
    """
    search_msg = f"Searching matters with name: {name}, status: {status}"
    if ctx:
        await ctx.info(search_msg)
    else:
        logger.info(search_msg)

    if not API_KEY:
        error_msg = "LAWMATICS_API_KEY not found in environment variables"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise ValueError(error_msg)

    params: dict[str, Any] = {}
    if name:
        params["name"] = name
    if contact_id:
        params["contact_id"] = contact_id
    if status:
        params["status"] = status
    if practice_area:
        params["practice_area"] = practice_area
    if limit:
        params["limit"] = limit

    headers = {"Authorization": f"Bearer {API_KEY}"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{config.lawmatics_base_url}matters",
                params=params,
                headers=headers,
                timeout=config.lawmatics_timeout,
            )
            response.raise_for_status()
            data = response.json()

            result_count = len(data) if isinstance(data, list) else data.get("total", 0)
            if ctx:
                await ctx.info(f"Found {result_count} matters")
            else:
                logger.info(f"Found {result_count} matters")

            return data

    except httpx.HTTPStatusError as e:
        error_msg = f"HTTP error {e.response.status_code}: {e.response.text}"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise
    except Exception as e:
        error_msg = f"Search error: {e}"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise


@search_server.tool()
async def search_tasks(
    contact_id: Annotated[str, Field(description="Filter tasks by contact ID")] = "",
    matter_id: Annotated[str, Field(description="Filter tasks by matter ID")] = "",
    status: Annotated[str, Field(description="Filter by task status (e.g., 'pending', 'completed')")] = "",
    assigned_to: Annotated[str, Field(description="Filter by user ID assigned to task")] = "",
    due_date_after: Annotated[str, Field(description="Show tasks due after this date (YYYY-MM-DD)")] = "",
    due_date_before: Annotated[str, Field(description="Show tasks due before this date (YYYY-MM-DD)")] = "",
    limit: Annotated[int, Field(description="Maximum results to return", ge=1, le=100)] = 20,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Search for tasks in Lawmatics.

    This tool searches across tasks and to-dos in your Lawmatics account.
    Best for finding tasks by contact, matter, status, assignment, or due date.
    Tasks represent action items and follow-ups for your team.

    Args:
        contact_id: Filter to tasks for a specific contact
        matter_id: Filter to tasks for a specific matter
        status: Filter by task status
        assigned_to: Filter by user assigned to the task
        due_date_after: Show tasks due after this date
        due_date_before: Show tasks due before this date
        limit: Maximum number of results to return (1-100)
        ctx: Optional FastMCP context for logging

    Returns:
        Dictionary containing search results with task details including
        title, description, status, assignee, due date, and associations.

    Raises:
        ValueError: If LAWMATICS_API_KEY is not found in environment variables.
    """
    if ctx:
        await ctx.info(f"Searching tasks with matter_id: {matter_id}, status: {status}")
    else:
        logger.info(f"Searching tasks with matter_id: {matter_id}, status: {status}")

    if not API_KEY:
        error_msg = "LAWMATICS_API_KEY not found in environment variables"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise ValueError(error_msg)

    params: dict[str, Any] = {}
    if contact_id:
        params["contact_id"] = contact_id
    if matter_id:
        params["matter_id"] = matter_id
    if status:
        params["status"] = status
    if assigned_to:
        params["assigned_to"] = assigned_to
    if due_date_after:
        params["due_date_after"] = due_date_after
    if due_date_before:
        params["due_date_before"] = due_date_before
    if limit:
        params["limit"] = limit

    headers = {"Authorization": f"Bearer {API_KEY}"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{config.lawmatics_base_url}tasks",
                params=params,
                headers=headers,
                timeout=config.lawmatics_timeout,
            )
            response.raise_for_status()
            data = response.json()

            result_count = len(data) if isinstance(data, list) else data.get("total", 0)
            if ctx:
                await ctx.info(f"Found {result_count} tasks")
            else:
                logger.info(f"Found {result_count} tasks")

            return data

    except httpx.HTTPStatusError as e:
        error_msg = f"HTTP error {e.response.status_code}: {e.response.text}"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise
    except Exception as e:
        error_msg = f"Search error: {e}"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise


@search_server.tool()
async def search_companies(
    name: Annotated[str, Field(description="Search for companies by name")] = "",
    email: Annotated[str, Field(description="Search for companies by email")] = "",
    phone: Annotated[str, Field(description="Search for companies by phone number")] = "",
    limit: Annotated[int, Field(description="Maximum results to return", ge=1, le=100)] = 20,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Search for companies in Lawmatics.

    This tool searches across companies/organizations in your Lawmatics account.
    Best for finding companies by name, email, or phone number.
    Companies represent organizations associated with your contacts and matters.

    Args:
        name: Search companies by name
        email: Search companies by email
        phone: Search companies by phone number
        limit: Maximum number of results to return (1-100)
        ctx: Optional FastMCP context for logging

    Returns:
        Dictionary containing search results with company details including
        name, email, phone, address, and associated contacts.

    Raises:
        ValueError: If LAWMATICS_API_KEY is not found in environment variables.
    """
    if ctx:
        await ctx.info(f"Searching companies with name: {name}")
    else:
        logger.info(f"Searching companies with name: {name}")

    if not API_KEY:
        error_msg = "LAWMATICS_API_KEY not found in environment variables"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise ValueError(error_msg)

    params: dict[str, Any] = {}
    if name:
        params["name"] = name
    if email:
        params["email"] = email
    if phone:
        params["phone"] = phone
    if limit:
        params["limit"] = limit

    headers = {"Authorization": f"Bearer {API_KEY}"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{config.lawmatics_base_url}companies",
                params=params,
                headers=headers,
                timeout=config.lawmatics_timeout,
            )
            response.raise_for_status()
            data = response.json()

            result_count = len(data) if isinstance(data, list) else data.get("total", 0)
            if ctx:
                await ctx.info(f"Found {result_count} companies")
            else:
                logger.info(f"Found {result_count} companies")

            return data

    except httpx.HTTPStatusError as e:
        error_msg = f"HTTP error {e.response.status_code}: {e.response.text}"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise
    except Exception as e:
        error_msg = f"Search error: {e}"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise


@search_server.tool()
async def search_time_entries(
    contact_id: Annotated[str, Field(description="Filter time entries by contact ID")] = "",
    matter_id: Annotated[str, Field(description="Filter time entries by matter ID")] = "",
    user_id: Annotated[str, Field(description="Filter by user who logged the time")] = "",
    date_after: Annotated[str, Field(description="Show entries after this date (YYYY-MM-DD)")] = "",
    date_before: Annotated[str, Field(description="Show entries before this date (YYYY-MM-DD)")] = "",
    limit: Annotated[int, Field(description="Maximum results to return", ge=1, le=100)] = 20,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Search for time entries in Lawmatics.

    This tool searches across time entries logged in your Lawmatics account.
    Best for finding billable hours by contact, matter, user, or date range.
    Time entries track hours worked on cases and clients.

    Args:
        contact_id: Filter to time entries for a specific contact
        matter_id: Filter to time entries for a specific matter
        user_id: Filter by user who logged the time
        date_after: Show entries logged after this date
        date_before: Show entries logged before this date
        limit: Maximum number of results to return (1-100)
        ctx: Optional FastMCP context for logging

    Returns:
        Dictionary containing search results with time entry details including
        duration, description, date, rate, user, and matter associations.

    Raises:
        ValueError: If LAWMATICS_API_KEY is not found in environment variables.
    """
    if ctx:
        await ctx.info(f"Searching time entries with matter_id: {matter_id}")
    else:
        logger.info(f"Searching time entries with matter_id: {matter_id}")

    if not API_KEY:
        error_msg = "LAWMATICS_API_KEY not found in environment variables"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise ValueError(error_msg)

    params: dict[str, Any] = {}
    if contact_id:
        params["contact_id"] = contact_id
    if matter_id:
        params["matter_id"] = matter_id
    if user_id:
        params["user_id"] = user_id
    if date_after:
        params["date_after"] = date_after
    if date_before:
        params["date_before"] = date_before
    if limit:
        params["limit"] = limit

    headers = {"Authorization": f"Bearer {API_KEY}"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{config.lawmatics_base_url}time_entries",
                params=params,
                headers=headers,
                timeout=config.lawmatics_timeout,
            )
            response.raise_for_status()
            data = response.json()

            result_count = len(data) if isinstance(data, list) else data.get("total", 0)
            if ctx:
                await ctx.info(f"Found {result_count} time entries")
            else:
                logger.info(f"Found {result_count} time entries")

            return data

    except httpx.HTTPStatusError as e:
        error_msg = f"HTTP error {e.response.status_code}: {e.response.text}"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise
    except Exception as e:
        error_msg = f"Search error: {e}"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise


@search_server.tool()
async def search_expenses(
    contact_id: Annotated[str, Field(description="Filter expenses by contact ID")] = "",
    matter_id: Annotated[str, Field(description="Filter expenses by matter ID")] = "",
    date_after: Annotated[str, Field(description="Show expenses after this date (YYYY-MM-DD)")] = "",
    date_before: Annotated[str, Field(description="Show expenses before this date (YYYY-MM-DD)")] = "",
    limit: Annotated[int, Field(description="Maximum results to return", ge=1, le=100)] = 20,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Search for expenses in Lawmatics.

    This tool searches across expenses logged in your Lawmatics account.
    Best for finding case-related expenses by contact, matter, or date range.
    Expenses track costs and reimbursable items associated with cases.

    Args:
        contact_id: Filter to expenses for a specific contact
        matter_id: Filter to expenses for a specific matter
        date_after: Show expenses incurred after this date
        date_before: Show expenses incurred before this date
        limit: Maximum number of results to return (1-100)
        ctx: Optional FastMCP context for logging

    Returns:
        Dictionary containing search results with expense details including
        amount, description, date, category, and matter associations.

    Raises:
        ValueError: If LAWMATICS_API_KEY is not found in environment variables.
    """
    if ctx:
        await ctx.info(f"Searching expenses with matter_id: {matter_id}")
    else:
        logger.info(f"Searching expenses with matter_id: {matter_id}")

    if not API_KEY:
        error_msg = "LAWMATICS_API_KEY not found in environment variables"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise ValueError(error_msg)

    params: dict[str, Any] = {}
    if contact_id:
        params["contact_id"] = contact_id
    if matter_id:
        params["matter_id"] = matter_id
    if date_after:
        params["date_after"] = date_after
    if date_before:
        params["date_before"] = date_before
    if limit:
        params["limit"] = limit

    headers = {"Authorization": f"Bearer {API_KEY}"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{config.lawmatics_base_url}expenses",
                params=params,
                headers=headers,
                timeout=config.lawmatics_timeout,
            )
            response.raise_for_status()
            data = response.json()

            result_count = len(data) if isinstance(data, list) else data.get("total", 0)
            if ctx:
                await ctx.info(f"Found {result_count} expenses")
            else:
                logger.info(f"Found {result_count} expenses")

            return data

    except httpx.HTTPStatusError as e:
        error_msg = f"HTTP error {e.response.status_code}: {e.response.text}"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise
    except Exception as e:
        error_msg = f"Search error: {e}"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise
