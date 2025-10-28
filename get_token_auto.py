#!/usr/bin/env python3
"""Get Lawmatics OAuth token with local callback server - AUTO MODE."""

import base64
import hashlib
import secrets
import time
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlencode, urlparse

import httpx

# Your credentials
CLIENT_ID = "RbXrKANGJvnBrL-vTQDK8MOmTWh1iBzDp7z-0Aa4F1w"
CLIENT_SECRET = "fF8LJwTF5KpM5Gr89O0j79l0QNmgZN7eU_HnLNTL65I"
REDIRECT_URI = "http://127.0.0.1:8888/callback"

authorization_code = None
code_verifier: str | None = None


def generate_pkce_pair() -> tuple[str, str]:
    """Generate PKCE code verifier/challenge pair."""
    verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode("ascii").rstrip("=")
    if len(verifier) < 43:
        verifier = verifier.ljust(43, "A")
    verifier = verifier[:128]
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    challenge = base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")
    return verifier, challenge


class CallbackHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Suppress logs

    def do_GET(self):
        global authorization_code

        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        if 'code' in params:
            authorization_code = params['code'][0]
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"""
                <html><body style="font-family: Arial; text-align: center; padding: 50px;">
                <h1 style="color: green;">&#10004; Success!</h1>
                <p style="font-size: 18px;">Authorization complete!</p>
                <p>You can close this window and return to your terminal.</p>
                </body></html>
            """)
        else:
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"""
                <html><body style="font-family: Arial; text-align: center; padding: 50px;">
                <h1 style="color: red;">&#10008; Error</h1>
                <p>No authorization code received.</p>
                </body></html>
            """)

def run_server():
    server = HTTPServer(('127.0.0.1', 8888), CallbackHandler)
    server.handle_request()

print("=" * 70)
print("Lawmatics OAuth Token Retriever")
print("=" * 70)
print()
print("STEP 1: Make sure you've updated the Redirect URI in Lawmatics to:")
print("        http://127.0.0.1:8888/callback")
print()
print("STEP 2: Starting local callback server...")
print()

# Start local server
server_thread = threading.Thread(target=run_server, daemon=True)
server_thread.start()
time.sleep(0.5)

print("✅ Server running on http://127.0.0.1:8888")
print()

# Build authorization URL
code_verifier, code_challenge = generate_pkce_pair()
params = {
    "client_id": CLIENT_ID,
    "redirect_uri": REDIRECT_URI,
    "response_type": "code",
    "scope": "read write",
    "code_challenge": code_challenge,
    "code_challenge_method": "S256",
}
auth_url = f"https://app.lawmatics.com/oauth/authorize?{urlencode(params)}"

print("STEP 3: Opening browser for authorization...")
print()
print("URL:", auth_url)
print()

try:
    webbrowser.open(auth_url)
    print("✅ Browser opened")
except Exception as e:
    print(f"⚠️  Could not open browser automatically: {e}")
    print("   Please visit the URL above manually")

print()
print("=" * 70)
print("Waiting for you to click 'Authorize' in the browser...")
print("(Timeout: 2 minutes)")
print("=" * 70)
print()

# Wait for callback
server_thread.join(timeout=120)

if authorization_code:
    print("✅ Authorization code received!")
    print()
    print("=" * 70)
    print("Exchanging code for access token...")
    print("=" * 70)
    print()

    try:
        response = httpx.post(
            "https://api.lawmatics.com/oauth/token",
            data={
                "grant_type": "authorization_code",
                "code": authorization_code,
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
            expires_in = data.get("expires_in", "unknown")

            print("✅ SUCCESS! Token retrieved")
            print()
            print("=" * 70)
            print("ACCESS TOKEN:")
            print("-" * 70)
            print(access_token)
            print()
            print("=" * 70)
            print("REFRESH TOKEN:")
            print("-" * 70)
            print(refresh_token)
            print()
            print("=" * 70)
            print(f"Token expires in: {expires_in} seconds")
            print()
            print("=" * 70)
            print("NEXT STEPS:")
            print("=" * 70)
            print()
            print("1. Go to FastMCP Cloud → Your Project → Settings → Environment Variables")
            print()
            print("2. Add this variable:")
            print(f"   Name:  LAWMATICS_ACCESS_TOKEN")
            print(f"   Value: {access_token}")
            print()
            print("3. Update Lawmatics Redirect URI back to:")
            print("   https://lawmatics-mcp-v1-0.fastmcp.app/oauth/callback")
            print()
            print("4. In FastMCP Cloud, click 'Save' and 'Redeploy'")
            print()
            print("5. Test your MCP server!")
            print()
            print("=" * 70)
        else:
            print(f"❌ Error exchanging token: HTTP {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Error: {e}")
else:
    print("❌ Timeout: No authorization code received within 2 minutes")
    print()
    print("Troubleshooting:")
    print("1. Make sure you clicked 'Authorize' in the browser")
    print("2. Check that Redirect URI in Lawmatics is: http://localhost:8888/callback")
    print("3. Try running the script again")
