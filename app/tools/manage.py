"""Manage tools for Lawmatics MCP server - create and update entities."""

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

# Create the manage server
manage_server: FastMCP[Any] = FastMCP(
    name="Lawmatics Manage Server",
    instructions=(
        "Management server for Lawmatics providing create and update operations. "
        "This server enables creating new contacts, matters, tasks, companies, "
        "time entries, and expenses, as well as updating existing entities. "
        "Use these tools to modify data in your Lawmatics account."
    ),
)


@manage_server.tool()
async def create_contact(
    first_name: Annotated[str, Field(description="Contact's first name")],
    last_name: Annotated[str, Field(description="Contact's last name")],
    email: Annotated[str, Field(description="Contact's email address")] = "",
    phone: Annotated[str, Field(description="Contact's phone number")] = "",
    company_id: Annotated[str, Field(description="Associated company ID")] = "",
    contact_type: Annotated[str, Field(description="Type of contact (lead, client, referrer)")] = "lead",
    additional_fields: Annotated[dict[str, Any], Field(description="Additional custom fields")] = {},
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Create a new contact in Lawmatics.

    Creates a new contact (lead, client, or referrer) in your Lawmatics account.
    At minimum requires first and last name. Can include email, phone, company,
    and any custom fields your account has configured.

    Args:
        first_name: Contact's first name (required)
        last_name: Contact's last name (required)
        email: Contact's email address
        phone: Contact's phone number
        company_id: ID of associated company
        contact_type: Type of contact (lead, client, referrer)
        additional_fields: Dictionary of additional custom fields
        ctx: Optional FastMCP context for logging

    Returns:
        Dictionary containing the created contact with ID and all fields

    Raises:
        ValueError: If LAWMATICS_API_KEY is not found
        httpx.HTTPStatusError: If creation fails
    """
    if ctx:
        await ctx.info(f"Creating contact: {first_name} {last_name}")
    else:
        logger.info(f"Creating contact: {first_name} {last_name}")

    if not API_KEY:
        error_msg = "LAWMATICS_API_KEY not found in environment variables"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise ValueError(error_msg)

    payload: dict[str, Any] = {
        "first_name": first_name,
        "last_name": last_name,
        "type": contact_type,
    }

    if email:
        payload["email"] = email
    if phone:
        payload["phone"] = phone
    if company_id:
        payload["company_id"] = company_id

    # Merge additional fields
    payload.update(additional_fields)

    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{config.lawmatics_base_url}contacts",
                json=payload,
                headers=headers,
                timeout=config.lawmatics_timeout,
            )
            response.raise_for_status()
            data = response.json()

            if ctx:
                await ctx.info(f"Created contact with ID: {data.get('id')}")

            return data

    except httpx.HTTPStatusError as e:
        error_msg = f"HTTP error {e.response.status_code}: {e.response.text}"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise
    except Exception as e:
        error_msg = f"Error creating contact: {e}"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise


@manage_server.tool()
async def update_contact(
    contact_id: Annotated[str, Field(description="The unique contact ID to update")],
    first_name: Annotated[str, Field(description="Contact's first name")] = "",
    last_name: Annotated[str, Field(description="Contact's last name")] = "",
    email: Annotated[str, Field(description="Contact's email address")] = "",
    phone: Annotated[str, Field(description="Contact's phone number")] = "",
    status: Annotated[str, Field(description="Contact status")] = "",
    additional_fields: Annotated[dict[str, Any], Field(description="Additional fields to update")] = {},
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Update an existing contact in Lawmatics.

    Updates fields for an existing contact. Only provide the fields you want to change.
    Empty/omitted fields will not be modified.

    Args:
        contact_id: The unique identifier for the contact to update (required)
        first_name: Updated first name
        last_name: Updated last name
        email: Updated email address
        phone: Updated phone number
        status: Updated contact status
        additional_fields: Dictionary of additional fields to update
        ctx: Optional FastMCP context for logging

    Returns:
        Dictionary containing the updated contact information

    Raises:
        ValueError: If LAWMATICS_API_KEY is not found
        httpx.HTTPStatusError: If update fails or contact not found
    """
    if ctx:
        await ctx.info(f"Updating contact: {contact_id}")
    else:
        logger.info(f"Updating contact: {contact_id}")

    if not API_KEY:
        error_msg = "LAWMATICS_API_KEY not found in environment variables"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise ValueError(error_msg)

    payload: dict[str, Any] = {}

    if first_name:
        payload["first_name"] = first_name
    if last_name:
        payload["last_name"] = last_name
    if email:
        payload["email"] = email
    if phone:
        payload["phone"] = phone
    if status:
        payload["status"] = status

    # Merge additional fields
    payload.update(additional_fields)

    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{config.lawmatics_base_url}contacts/{contact_id}",
                json=payload,
                headers=headers,
                timeout=config.lawmatics_timeout,
            )
            response.raise_for_status()
            data = response.json()

            if ctx:
                await ctx.info(f"Updated contact: {contact_id}")

            return data

    except httpx.HTTPStatusError as e:
        error_msg = f"HTTP error {e.response.status_code}: {e.response.text}"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise
    except Exception as e:
        error_msg = f"Error updating contact: {e}"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise


@manage_server.tool()
async def create_task(
    title: Annotated[str, Field(description="Task title")],
    description: Annotated[str, Field(description="Task description")] = "",
    due_date: Annotated[str, Field(description="Due date (YYYY-MM-DD)")] = "",
    assigned_to: Annotated[str, Field(description="User ID to assign task to")] = "",
    contact_id: Annotated[str, Field(description="Associated contact ID")] = "",
    matter_id: Annotated[str, Field(description="Associated matter ID")] = "",
    status: Annotated[str, Field(description="Task status (pending, completed)")] = "pending",
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Create a new task in Lawmatics.

    Creates a new task/to-do item in your Lawmatics account. Tasks can be
    associated with contacts, matters, and assigned to team members.

    Args:
        title: Task title (required)
        description: Detailed task description
        due_date: Task due date in YYYY-MM-DD format
        assigned_to: User ID of team member to assign task to
        contact_id: ID of associated contact
        matter_id: ID of associated matter
        status: Task status (pending or completed)
        ctx: Optional FastMCP context for logging

    Returns:
        Dictionary containing the created task with ID and all fields

    Raises:
        ValueError: If LAWMATICS_API_KEY is not found
        httpx.HTTPStatusError: If creation fails
    """
    if ctx:
        await ctx.info(f"Creating task: {title}")
    else:
        logger.info(f"Creating task: {title}")

    if not API_KEY:
        error_msg = "LAWMATICS_API_KEY not found in environment variables"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise ValueError(error_msg)

    payload: dict[str, Any] = {
        "title": title,
        "status": status,
    }

    if description:
        payload["description"] = description
    if due_date:
        payload["due_date"] = due_date
    if assigned_to:
        payload["assigned_to"] = assigned_to
    if contact_id:
        payload["contact_id"] = contact_id
    if matter_id:
        payload["matter_id"] = matter_id

    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{config.lawmatics_base_url}tasks",
                json=payload,
                headers=headers,
                timeout=config.lawmatics_timeout,
            )
            response.raise_for_status()
            data = response.json()

            if ctx:
                await ctx.info(f"Created task with ID: {data.get('id')}")

            return data

    except httpx.HTTPStatusError as e:
        error_msg = f"HTTP error {e.response.status_code}: {e.response.text}"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise
    except Exception as e:
        error_msg = f"Error creating task: {e}"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise


@manage_server.tool()
async def update_task(
    task_id: Annotated[str, Field(description="The unique task ID to update")],
    title: Annotated[str, Field(description="Updated task title")] = "",
    description: Annotated[str, Field(description="Updated task description")] = "",
    due_date: Annotated[str, Field(description="Updated due date (YYYY-MM-DD)")] = "",
    assigned_to: Annotated[str, Field(description="Updated user ID assignment")] = "",
    status: Annotated[str, Field(description="Updated task status")] = "",
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Update an existing task in Lawmatics.

    Updates fields for an existing task. Only provide the fields you want to change.
    Useful for marking tasks complete, updating due dates, or reassigning tasks.

    Args:
        task_id: The unique identifier for the task to update (required)
        title: Updated task title
        description: Updated task description
        due_date: Updated due date
        assigned_to: Updated user assignment
        status: Updated status (e.g., 'completed')
        ctx: Optional FastMCP context for logging

    Returns:
        Dictionary containing the updated task information

    Raises:
        ValueError: If LAWMATICS_API_KEY is not found
        httpx.HTTPStatusError: If update fails or task not found
    """
    if ctx:
        await ctx.info(f"Updating task: {task_id}")
    else:
        logger.info(f"Updating task: {task_id}")

    if not API_KEY:
        error_msg = "LAWMATICS_API_KEY not found in environment variables"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise ValueError(error_msg)

    payload: dict[str, Any] = {}

    if title:
        payload["title"] = title
    if description:
        payload["description"] = description
    if due_date:
        payload["due_date"] = due_date
    if assigned_to:
        payload["assigned_to"] = assigned_to
    if status:
        payload["status"] = status

    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{config.lawmatics_base_url}tasks/{task_id}",
                json=payload,
                headers=headers,
                timeout=config.lawmatics_timeout,
            )
            response.raise_for_status()
            data = response.json()

            if ctx:
                await ctx.info(f"Updated task: {task_id}")

            return data

    except httpx.HTTPStatusError as e:
        error_msg = f"HTTP error {e.response.status_code}: {e.response.text}"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise
    except Exception as e:
        error_msg = f"Error updating task: {e}"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise


@manage_server.tool()
async def create_time_entry(
    matter_id: Annotated[str, Field(description="Matter ID the time is associated with")],
    duration: Annotated[float, Field(description="Duration in hours", gt=0)],
    description: Annotated[str, Field(description="Description of work performed")],
    date: Annotated[str, Field(description="Date of work (YYYY-MM-DD)")],
    user_id: Annotated[str, Field(description="User ID who performed the work")] = "",
    billable: Annotated[bool, Field(description="Whether time is billable")] = True,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Create a new time entry in Lawmatics.

    Creates a new time entry for tracking billable hours on a matter.
    Time entries are used for billing and reporting.

    Args:
        matter_id: ID of the matter this time is for (required)
        duration: Number of hours worked (required)
        description: Description of the work performed (required)
        date: Date the work was performed in YYYY-MM-DD format (required)
        user_id: ID of user who performed the work
        billable: Whether this time is billable to the client
        ctx: Optional FastMCP context for logging

    Returns:
        Dictionary containing the created time entry with ID and all fields

    Raises:
        ValueError: If LAWMATICS_API_KEY is not found
        httpx.HTTPStatusError: If creation fails
    """
    if ctx:
        await ctx.info(f"Creating time entry for matter: {matter_id}")
    else:
        logger.info(f"Creating time entry for matter: {matter_id}")

    if not API_KEY:
        error_msg = "LAWMATICS_API_KEY not found in environment variables"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise ValueError(error_msg)

    payload: dict[str, Any] = {
        "matter_id": matter_id,
        "duration": duration,
        "description": description,
        "date": date,
        "billable": billable,
    }

    if user_id:
        payload["user_id"] = user_id

    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{config.lawmatics_base_url}time_entries",
                json=payload,
                headers=headers,
                timeout=config.lawmatics_timeout,
            )
            response.raise_for_status()
            data = response.json()

            if ctx:
                await ctx.info(f"Created time entry with ID: {data.get('id')}")

            return data

    except httpx.HTTPStatusError as e:
        error_msg = f"HTTP error {e.response.status_code}: {e.response.text}"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise
    except Exception as e:
        error_msg = f"Error creating time entry: {e}"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise


@manage_server.tool()
async def create_expense(
    matter_id: Annotated[str, Field(description="Matter ID the expense is associated with")],
    amount: Annotated[float, Field(description="Expense amount", gt=0)],
    description: Annotated[str, Field(description="Description of expense")],
    date: Annotated[str, Field(description="Date of expense (YYYY-MM-DD)")],
    category: Annotated[str, Field(description="Expense category")] = "",
    billable: Annotated[bool, Field(description="Whether expense is billable")] = True,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Create a new expense in Lawmatics.

    Creates a new expense entry for tracking case-related costs.
    Expenses can be billable or non-billable and are used for reimbursement tracking.

    Args:
        matter_id: ID of the matter this expense is for (required)
        amount: Expense amount in dollars (required)
        description: Description of the expense (required)
        date: Date the expense was incurred in YYYY-MM-DD format (required)
        category: Expense category (e.g., 'filing fees', 'travel')
        billable: Whether this expense is billable to the client
        ctx: Optional FastMCP context for logging

    Returns:
        Dictionary containing the created expense with ID and all fields

    Raises:
        ValueError: If LAWMATICS_API_KEY is not found
        httpx.HTTPStatusError: If creation fails
    """
    if ctx:
        await ctx.info(f"Creating expense for matter: {matter_id}")
    else:
        logger.info(f"Creating expense for matter: {matter_id}")

    if not API_KEY:
        error_msg = "LAWMATICS_API_KEY not found in environment variables"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise ValueError(error_msg)

    payload: dict[str, Any] = {
        "matter_id": matter_id,
        "amount": amount,
        "description": description,
        "date": date,
        "billable": billable,
    }

    if category:
        payload["category"] = category

    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{config.lawmatics_base_url}expenses",
                json=payload,
                headers=headers,
                timeout=config.lawmatics_timeout,
            )
            response.raise_for_status()
            data = response.json()

            if ctx:
                await ctx.info(f"Created expense with ID: {data.get('id')}")

            return data

    except httpx.HTTPStatusError as e:
        error_msg = f"HTTP error {e.response.status_code}: {e.response.text}"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise
    except Exception as e:
        error_msg = f"Error creating expense: {e}"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise


@manage_server.tool()
async def delete_task(
    task_id: Annotated[str, Field(description="The unique task ID to delete")],
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Delete a task from Lawmatics.

    Permanently deletes a task. This operation cannot be undone.
    Use with caution.

    Args:
        task_id: The unique identifier for the task to delete (required)
        ctx: Optional FastMCP context for logging

    Returns:
        Dictionary confirming deletion

    Raises:
        ValueError: If LAWMATICS_API_KEY is not found
        httpx.HTTPStatusError: If deletion fails or task not found
    """
    if ctx:
        await ctx.info(f"Deleting task: {task_id}")
    else:
        logger.info(f"Deleting task: {task_id}")

    if not API_KEY:
        error_msg = "LAWMATICS_API_KEY not found in environment variables"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise ValueError(error_msg)

    headers = {"Authorization": f"Bearer {API_KEY}"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{config.lawmatics_base_url}tasks/{task_id}",
                headers=headers,
                timeout=config.lawmatics_timeout,
            )
            response.raise_for_status()

            if ctx:
                await ctx.info(f"Deleted task: {task_id}")

            return {"success": True, "message": f"Task {task_id} deleted successfully"}

    except httpx.HTTPStatusError as e:
        error_msg = f"HTTP error {e.response.status_code}: {e.response.text}"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise
    except Exception as e:
        error_msg = f"Error deleting task: {e}"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise
