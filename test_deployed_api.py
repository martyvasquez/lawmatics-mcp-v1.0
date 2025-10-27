#!/usr/bin/env python3
"""Test the deployed Lawmatics MCP Server via HTTP.

This script tests the deployed server by calling the search_contacts tool
to find all matters associated with phone number 714-917-5140.

Usage:
    python test_deployed_api.py [server_url]

Example:
    python test_deployed_api.py https://your-project.fastmcp.app
"""

import asyncio
import sys
import httpx
import json


async def test_deployed_server(server_url: str):
    """Test the deployed MCP server."""

    print("=" * 70)
    print("Testing Deployed Lawmatics MCP Server")
    print("=" * 70)
    print(f"\nServer URL: {server_url}")
    print()

    async with httpx.AsyncClient(timeout=30.0) as client:

        # Test 1: List available tools
        print("STEP 1: Listing available tools...")
        print("-" * 70)
        try:
            response = await client.post(
                f"{server_url}/mcp",
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/list",
                    "params": {}
                }
            )
            data = response.json()

            if "result" in data:
                tools = data["result"].get("tools", [])
                print(f"✅ Found {len(tools)} tools")
                print("\nAvailable tools:")
                for tool in tools[:5]:  # Show first 5
                    print(f"  - {tool.get('name')}")
                if len(tools) > 5:
                    print(f"  ... and {len(tools) - 5} more")
            else:
                print(f"❌ Error: {data.get('error', 'Unknown error')}")
                return

        except Exception as e:
            print(f"❌ Failed to connect: {e}")
            return

        print()

        # Test 2: Check server status
        print("\nSTEP 2: Checking server status...")
        print("-" * 70)
        try:
            response = await client.post(
                f"{server_url}/mcp",
                json={
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/call",
                    "params": {
                        "name": "status",
                        "arguments": {}
                    }
                }
            )
            data = response.json()

            if "result" in data:
                result = data["result"]
                if isinstance(result, dict) and "content" in result:
                    # MCP format response
                    content = result["content"][0]["text"]
                    status_data = json.loads(content)
                    print(f"✅ Server Status: {status_data.get('status')}")
                    print(f"   Service: {status_data.get('service')}")
                    print(f"   Version: {status_data.get('version')}")
                else:
                    print(f"✅ Status: {result}")
            else:
                print(f"⚠️  Status check returned: {data.get('error', 'No error info')}")

        except Exception as e:
            print(f"⚠️  Status check failed: {e}")

        print()

        # Test 3: Search for contacts by phone
        print("\nSTEP 3: Searching for contacts with phone 714-917-5140...")
        print("-" * 70)
        try:
            response = await client.post(
                f"{server_url}/mcp",
                json={
                    "jsonrpc": "2.0",
                    "id": 3,
                    "method": "tools/call",
                    "params": {
                        "name": "search_contacts",
                        "arguments": {
                            "phone": "714-917-5140"
                        }
                    }
                }
            )
            data = response.json()

            if "result" in data:
                result = data["result"]
                if isinstance(result, dict) and "content" in result:
                    # MCP format response
                    content = result["content"][0]["text"]
                    contacts_data = json.loads(content)

                    if isinstance(contacts_data, list):
                        contacts = contacts_data
                    else:
                        contacts = contacts_data.get("data", contacts_data.get("results", []))

                    print(f"✅ Found {len(contacts)} contact(s)")

                    if contacts:
                        for idx, contact in enumerate(contacts, 1):
                            name = f"{contact.get('first_name', '')} {contact.get('last_name', '')}".strip()
                            email = contact.get('email', 'N/A')
                            print(f"\n   Contact {idx}:")
                            print(f"     Name:  {name}")
                            print(f"     Email: {email}")
                            print(f"     ID:    {contact.get('id', 'N/A')}")
                    else:
                        print("   No contacts found with this phone number")
                else:
                    print(f"✅ Result: {result}")
            elif "error" in data:
                error = data["error"]
                print(f"❌ Error: {error.get('message', 'Unknown error')}")
                if "data" in error:
                    print(f"   Details: {error['data']}")
            else:
                print(f"⚠️  Unexpected response: {data}")

        except httpx.HTTPStatusError as e:
            print(f"❌ HTTP Error {e.response.status_code}: {e.response.text}")
        except Exception as e:
            print(f"❌ Search failed: {e}")

    print()
    print("=" * 70)
    print("Test Complete")
    print("=" * 70)


def main():
    """Main entry point."""
    # Get server URL from command line or use default
    if len(sys.argv) > 1:
        server_url = sys.argv[1].rstrip('/')
    else:
        server_url = "https://lawmatics-mcp-v1-0.fastmcp.app"

    # Run the test
    asyncio.run(test_deployed_server(server_url))


if __name__ == "__main__":
    main()
