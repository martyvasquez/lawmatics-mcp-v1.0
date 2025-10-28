#!/usr/bin/env python3
"""Manual OAuth token retrieval for Lawmatics.

This script helps you get an access token when you don't have a callback server.
"""

import base64
import hashlib
import secrets
import webbrowser
from urllib.parse import urlencode

# Your OAuth credentials
CLIENT_ID = "RbXrKANGJvnBrL-vTQDK8MOmTWh1iBzDp7z-0Aa4F1w"
CLIENT_SECRET = "fF8LJwTF5KpM5Gr89O0j79l0QNmgZN7eU_HnLNTL65I"
REDIRECT_URI = "https://lawmatics-mcp-v1-0.fastmcp.app/oauth/callback"


def generate_pkce_pair() -> tuple[str, str]:
    verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode("ascii").rstrip("=")
    if len(verifier) < 43:
        verifier = verifier.ljust(43, "A")
    verifier = verifier[:128]
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    challenge = base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")
    return verifier, challenge

print("=" * 70)
print("Lawmatics OAuth Access Token Generator")
print("=" * 70)
print()

# Step 1: Generate authorization URL
code_verifier, code_challenge = generate_pkce_pair()

# Display PKCE helper info
print("PKCE Code Verifier (keep this for the token exchange):")
print(code_verifier)
print()
params = {
    "client_id": CLIENT_ID,
    "redirect_uri": REDIRECT_URI,
    "response_type": "code",
    "scope": "read write",
    "code_challenge": code_challenge,
    "code_challenge_method": "S256",
}

auth_url = f"https://app.lawmatics.com/oauth/authorize?{urlencode(params)}"

print("STEP 1: Authorize the application")
print("-" * 70)
print("Opening your browser to authorize the application...")
print()
print("If the browser doesn't open automatically, visit this URL:")
print(auth_url)
print()

# Open browser
try:
    webbrowser.open(auth_url)
except:
    pass

print("After clicking 'Authorize', you'll be redirected to a page that says:")
print("'Could not authenticate: undefined'")
print()
print("DON'T WORRY - This is expected!")
print()
print("Look at the URL in your browser's address bar. It should look like:")
print("https://lawmatics-mcp-v1-0.fastmcp.app/oauth/callback?code=XXXXX")
print()
print("=" * 70)
print()

# Step 2: Get the code
code = input("Paste the ENTIRE URL here: ").strip()

# Extract code from URL
if "code=" in code:
    code = code.split("code=")[1]
    if "&" in code:
        code = code.split("&")[0]
    print()
    print("✅ Code extracted:", code[:20] + "...")
else:
    print()
    print("⚠️  No 'code' parameter found. Using input as-is.")

print()
print("=" * 70)
print("STEP 2: Exchanging code for access token...")
print("-" * 70)

# Step 3: Exchange for token
import httpx

try:
    response = httpx.post(
        "https://api.lawmatics.com/oauth/token",
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code_verifier": code_verifier,
        },
        timeout=30.0
    )

    if response.status_code == 200:
        data = response.json()
        access_token = data.get("access_token")
        refresh_token = data.get("refresh_token")

        print("✅ SUCCESS! Access token retrieved.")
        print()
        print("=" * 70)
        print("YOUR ACCESS TOKEN:")
        print("-" * 70)
        print(access_token)
        print()
        print("=" * 70)
        print("YOUR REFRESH TOKEN (save this for later):")
        print("-" * 70)
        print(refresh_token)
        print()
        print("=" * 70)
        print()
        print("NEXT STEPS:")
        print("1. Go to FastMCP Cloud dashboard")
        print("2. Navigate to your project settings")
        print("3. Add environment variable:")
        print()
        print(f"   LAWMATICS_ACCESS_TOKEN={access_token}")
        print()
        print("4. Save and redeploy")
        print("=" * 70)

    else:
        print(f"❌ Error: HTTP {response.status_code}")
        print(response.text)

except Exception as e:
    print(f"❌ Error: {e}")
