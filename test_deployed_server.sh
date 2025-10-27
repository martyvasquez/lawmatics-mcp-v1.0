#!/bin/bash
# Test script for deployed Lawmatics MCP Server
# Usage: ./test_deployed_server.sh <server_url>

SERVER_URL="${1:-https://lawmatics-mcp-v1-0.fastmcp.app}"

echo "======================================================================"
echo "Testing Lawmatics MCP Server: Find matters for phone 714-917-5140"
echo "======================================================================"
echo ""
echo "Server URL: $SERVER_URL"
echo ""

# Test 1: List available tools
echo "Step 1: Listing available tools..."
echo "----------------------------------------------------------------------"
curl -s -X POST "$SERVER_URL/mcp" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | jq '.'

echo ""
echo ""

# Test 2: Search for contacts by phone
echo "Step 2: Searching for contacts with phone 714-917-5140..."
echo "----------------------------------------------------------------------"
curl -s -X POST "$SERVER_URL/mcp" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "search_contacts",
      "arguments": {
        "phone": "714-917-5140"
      }
    }
  }' | jq '.'

echo ""
echo ""

# Test 3: Check server status
echo "Step 3: Checking server status..."
echo "----------------------------------------------------------------------"
curl -s -X POST "$SERVER_URL/mcp" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
      "name": "status",
      "arguments": {}
    }
  }' | jq '.'

echo ""
echo "======================================================================"
echo "Test Complete"
echo "======================================================================"
