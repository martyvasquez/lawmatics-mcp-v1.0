#!/bin/bash
# Script to exchange OAuth authorization code for access token (PKCE aware)
# Usage: ./get_access_token.sh YOUR_AUTHORIZATION_CODE YOUR_CODE_VERIFIER

if [ -z "$1" ] || [ -z "$2" ]; then
  echo "Usage: ./get_access_token.sh YOUR_AUTHORIZATION_CODE YOUR_CODE_VERIFIER"
  echo ""
  echo "First, generate the authorization URL with the companion Python script."
  echo "It will display the code verifier alongside the authorization URL."
  echo "After authorizing, copy the 'code' parameter from the redirect URL and note the verifier."
  echo "Then run: ./get_access_token.sh YOUR_CODE YOUR_CODE_VERIFIER"
  exit 1
fi

CODE="$1"
CODE_VERIFIER="$2"

echo "========================================================================"
echo "Exchanging authorization code for access token..."
echo "========================================================================"
echo ""

curl -X POST https://api.lawmatics.com/oauth/token \
  -d "grant_type=authorization_code" \
  -d "code=$CODE" \
  -d "redirect_uri=https://lawmatics-mcp-v1-0.fastmcp.app/oauth/callback" \
  -d "client_id=RbXrKANGJvnBrL-vTQDK8MOmTWh1iBzDp7z-0Aa4F1w" \
  -d "client_secret=fF8LJwTF5KpM5Gr89O0j79l0QNmgZN7eU_HnLNTL65I" \
  -d "code_verifier=$CODE_VERIFIER" | jq '.'

echo ""
echo "========================================================================"
echo "Copy the 'access_token' value and add it to FastMCP Cloud as:"
echo "LAWMATICS_ACCESS_TOKEN=your_access_token_here"
echo "========================================================================"
