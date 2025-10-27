"""Get tools for Lawmatics MCP server - retrieve specific entities by ID."""

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

# Get API credentials from environment (OAuth or legacy API key)
API_KEY = os.getenv("LAWMATICS_ACCESS_TOKEN") or os.getenv("LAWMATICS_API_KEY")

# Create the get server
get_server: FastMCP[Any] = FastMCP(
    name="Lawmatics Get Server",
    instructions=(
        "Retrieval server for Lawmatics providing direct access to specific entities by ID. "
        "This server enables retrieving full details for contacts, matters, tasks, companies, "
        "time entries, expenses, and users. "
        "Use these tools when you have a specific ID and need complete entity information."
    ),
)


@get_server.tool()
async def get_contact(
    contact_id: Annotated[str, Field(description="The unique contact ID")],
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Get a contact by ID from Lawmatics.

    Retrieves complete information for a specific contact including all fields,
    custom fields, associated matters, notes, and activity history.

    Args:
        contact_id: The unique identifier for the contact
        ctx: Optional FastMCP context for logging

    Returns:
        Dictionary containing complete contact information

    Raises:
        ValueError: If LAWMATICS_API_KEY is not found
        httpx.HTTPStatusError: If the contact is not found or request fails
    """
    if ctx:
        await ctx.info(f"Retrieving contact: {contact_id}")
    else:
        logger.info(f"Retrieving contact: {contact_id}")

    if not API_KEY:
        error_msg = "LAWMATICS_ACCESS_TOKEN or LAWMATICS_API_KEY not found in environment variables"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise ValueError(error_msg)

    headers = {"Authorization": f"Bearer {API_KEY}"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{config.lawmatics_base_url}contacts/{contact_id}",
                headers=headers,
                timeout=config.lawmatics_timeout,
            )
            response.raise_for_status()
            data = response.json()

            if ctx:
                await ctx.info(f"Retrieved contact: {data.get('name', contact_id)}")

            return data

    except httpx.HTTPStatusError as e:
        error_msg = f"HTTP error {e.response.status_code}: {e.response.text}"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise
    except Exception as e:
        error_msg = f"Error retrieving contact: {e}"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise


@get_server.tool()
async def get_matter(
    matter_id: Annotated[str, Field(description="The unique matter ID")],
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Get a matter by ID from Lawmatics.

    Retrieves complete information for a specific matter/case including all fields,
    custom fields, associated contacts, tasks, documents, and case history.

    Args:
        matter_id: The unique identifier for the matter
        ctx: Optional FastMCP context for logging

    Returns:
        Dictionary containing complete matter information

    Raises:
        ValueError: If LAWMATICS_API_KEY is not found
        httpx.HTTPStatusError: If the matter is not found or request fails
    """
    if ctx:
        await ctx.info(f"Retrieving matter: {matter_id}")
    else:
        logger.info(f"Retrieving matter: {matter_id}")

    if not API_KEY:
        error_msg = "LAWMATICS_ACCESS_TOKEN or LAWMATICS_API_KEY not found in environment variables"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise ValueError(error_msg)

    headers = {"Authorization": f"Bearer {API_KEY}"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{config.lawmatics_base_url}matters/{matter_id}",
                headers=headers,
                timeout=config.lawmatics_timeout,
            )
            response.raise_for_status()
            data = response.json()

            if ctx:
                await ctx.info(f"Retrieved matter: {data.get('name', matter_id)}")

            return data

    except httpx.HTTPStatusError as e:
        error_msg = f"HTTP error {e.response.status_code}: {e.response.text}"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise
    except Exception as e:
        error_msg = f"Error retrieving matter: {e}"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise


@get_server.tool()
async def get_task(
    task_id: Annotated[str, Field(description="The unique task ID")],
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Get a task by ID from Lawmatics.

    Retrieves complete information for a specific task including title, description,
    status, due date, assignee, and associated matter/contact.

    Args:
        task_id: The unique identifier for the task
        ctx: Optional FastMCP context for logging

    Returns:
        Dictionary containing complete task information

    Raises:
        ValueError: If LAWMATICS_API_KEY is not found
        httpx.HTTPStatusError: If the task is not found or request fails
    """
    if ctx:
        await ctx.info(f"Retrieving task: {task_id}")
    else:
        logger.info(f"Retrieving task: {task_id}")

    if not API_KEY:
        error_msg = "LAWMATICS_ACCESS_TOKEN or LAWMATICS_API_KEY not found in environment variables"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise ValueError(error_msg)

    headers = {"Authorization": f"Bearer {API_KEY}"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{config.lawmatics_base_url}tasks/{task_id}",
                headers=headers,
                timeout=config.lawmatics_timeout,
            )
            response.raise_for_status()
            data = response.json()

            if ctx:
                await ctx.info(f"Retrieved task: {data.get('title', task_id)}")

            return data

    except httpx.HTTPStatusError as e:
        error_msg = f"HTTP error {e.response.status_code}: {e.response.text}"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise
    except Exception as e:
        error_msg = f"Error retrieving task: {e}"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise


@get_server.tool()
async def get_company(
    company_id: Annotated[str, Field(description="The unique company ID")],
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Get a company by ID from Lawmatics.

    Retrieves complete information for a specific company/organization including
    all fields, contact information, associated contacts, and custom fields.

    Args:
        company_id: The unique identifier for the company
        ctx: Optional FastMCP context for logging

    Returns:
        Dictionary containing complete company information

    Raises:
        ValueError: If LAWMATICS_API_KEY is not found
        httpx.HTTPStatusError: If the company is not found or request fails
    """
    if ctx:
        await ctx.info(f"Retrieving company: {company_id}")
    else:
        logger.info(f"Retrieving company: {company_id}")

    if not API_KEY:
        error_msg = "LAWMATICS_ACCESS_TOKEN or LAWMATICS_API_KEY not found in environment variables"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise ValueError(error_msg)

    headers = {"Authorization": f"Bearer {API_KEY}"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{config.lawmatics_base_url}companies/{company_id}",
                headers=headers,
                timeout=config.lawmatics_timeout,
            )
            response.raise_for_status()
            data = response.json()

            if ctx:
                await ctx.info(f"Retrieved company: {data.get('name', company_id)}")

            return data

    except httpx.HTTPStatusError as e:
        error_msg = f"HTTP error {e.response.status_code}: {e.response.text}"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise
    except Exception as e:
        error_msg = f"Error retrieving company: {e}"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise


@get_server.tool()
async def get_time_entry(
    time_entry_id: Annotated[str, Field(description="The unique time entry ID")],
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Get a time entry by ID from Lawmatics.

    Retrieves complete information for a specific time entry including
    duration, description, date, billing rate, user, and matter association.

    Args:
        time_entry_id: The unique identifier for the time entry
        ctx: Optional FastMCP context for logging

    Returns:
        Dictionary containing complete time entry information

    Raises:
        ValueError: If LAWMATICS_API_KEY is not found
        httpx.HTTPStatusError: If the time entry is not found or request fails
    """
    if ctx:
        await ctx.info(f"Retrieving time entry: {time_entry_id}")
    else:
        logger.info(f"Retrieving time entry: {time_entry_id}")

    if not API_KEY:
        error_msg = "LAWMATICS_ACCESS_TOKEN or LAWMATICS_API_KEY not found in environment variables"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise ValueError(error_msg)

    headers = {"Authorization": f"Bearer {API_KEY}"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{config.lawmatics_base_url}time_entries/{time_entry_id}",
                headers=headers,
                timeout=config.lawmatics_timeout,
            )
            response.raise_for_status()
            return response.json()

    except httpx.HTTPStatusError as e:
        error_msg = f"HTTP error {e.response.status_code}: {e.response.text}"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise
    except Exception as e:
        error_msg = f"Error retrieving time entry: {e}"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise


@get_server.tool()
async def get_expense(
    expense_id: Annotated[str, Field(description="The unique expense ID")],
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Get an expense by ID from Lawmatics.

    Retrieves complete information for a specific expense including
    amount, description, date, category, and matter association.

    Args:
        expense_id: The unique identifier for the expense
        ctx: Optional FastMCP context for logging

    Returns:
        Dictionary containing complete expense information

    Raises:
        ValueError: If LAWMATICS_API_KEY is not found
        httpx.HTTPStatusError: If the expense is not found or request fails
    """
    if ctx:
        await ctx.info(f"Retrieving expense: {expense_id}")
    else:
        logger.info(f"Retrieving expense: {expense_id}")

    if not API_KEY:
        error_msg = "LAWMATICS_ACCESS_TOKEN or LAWMATICS_API_KEY not found in environment variables"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise ValueError(error_msg)

    headers = {"Authorization": f"Bearer {API_KEY}"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{config.lawmatics_base_url}expenses/{expense_id}",
                headers=headers,
                timeout=config.lawmatics_timeout,
            )
            response.raise_for_status()
            return response.json()

    except httpx.HTTPStatusError as e:
        error_msg = f"HTTP error {e.response.status_code}: {e.response.text}"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise
    except Exception as e:
        error_msg = f"Error retrieving expense: {e}"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise


@get_server.tool()
async def get_user(
    user_id: Annotated[str, Field(description="The unique user ID")],
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Get a user by ID from Lawmatics.

    Retrieves complete information for a specific user/team member including
    name, email, role, permissions, and settings.

    Args:
        user_id: The unique identifier for the user
        ctx: Optional FastMC P context for logging

    Returns:
        Dictionary containing complete user information

    Raises:
        ValueError: If LAWMATICS_API_KEY is not found
        httpx.HTTPStatusError: If the user is not found or request fails
    """
    if ctx:
        await ctx.info(f"Retrieving user: {user_id}")
    else:
        logger.info(f"Retrieving user: {user_id}")

    if not API_KEY:
        error_msg = "LAWMATICS_ACCESS_TOKEN or LAWMATICS_API_KEY not found in environment variables"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise ValueError(error_msg)

    headers = {"Authorization": f"Bearer {API_KEY}"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{config.lawmatics_base_url}users/{user_id}",
                headers=headers,
                timeout=config.lawmatics_timeout,
            )
            response.raise_for_status()
            data = response.json()

            if ctx:
                await ctx.info(f"Retrieved user: {data.get('name', user_id)}")

            return data

    except httpx.HTTPStatusError as e:
        error_msg = f"HTTP error {e.response.status_code}: {e.response.text}"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise
    except Exception as e:
        error_msg = f"Error retrieving user: {e}"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise


@get_server.tool()
async def list_users(
    ctx: Context | None = None,
) -> dict[str, Any]:
    """List all users in Lawmatics.

    Retrieves a list of all users/team members in your Lawmatics account.
    Useful for getting user IDs for filtering tasks, time entries, etc.

    Args:
        ctx: Optional FastMCP context for logging

    Returns:
        Dictionary containing list of users with basic information

    Raises:
        ValueError: If LAWMATICS_API_KEY is not found
        httpx.HTTPStatusError: If request fails
    """
    if ctx:
        await ctx.info("Retrieving user list")
    else:
        logger.info("Retrieving user list")

    if not API_KEY:
        error_msg = "LAWMATICS_ACCESS_TOKEN or LAWMATICS_API_KEY not found in environment variables"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise ValueError(error_msg)

    headers = {"Authorization": f"Bearer {API_KEY}"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{config.lawmatics_base_url}users",
                headers=headers,
                timeout=config.lawmatics_timeout,
            )
            response.raise_for_status()
            data = response.json()

            result_count = len(data) if isinstance(data, list) else data.get("total", 0)
            if ctx:
                await ctx.info(f"Retrieved {result_count} users")

            return data

    except httpx.HTTPStatusError as e:
        error_msg = f"HTTP error {e.response.status_code}: {e.response.text}"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise
    except Exception as e:
        error_msg = f"Error retrieving users: {e}"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise
