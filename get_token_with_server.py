#!/usr/bin/env python3
"""Get Lawmatics OAuth token with local callback server."""

import base64
import hashlib
import secrets
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlencode, urlparse

import httpx

# Your credentials
CLIENT_ID = "RbXrKANGJvnBrL-vTQDK8MOmTWh1iBzDp7z-0Aa4F1w"
CLIENT_SECRET = "fF8LJwTF5KpM5Gr89O0j79l0QNmgZN7eU_HnLNTL65I"
REDIRECT_URI = "http://localhost:8888/callback"

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
                <h1 style="color: green;">Success!</h1>
                <p>Authorization complete. You can close this window.</p>
                <p>Return to your terminal to see the access token.</p>
                </body></html>
            """)
        else:
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"""
                <html><body style="font-family: Arial; text-align: center; padding: 50px;">
                <h1 style="color: red;">Error</h1>
                <p>No authorization code received.</p>
                </body></html>
            """)

def run_server():
    server = HTTPServer(('localhost', 8888), CallbackHandler)
    server.handle_request()  # Handle one request then stop

print("=" * 70)
print("Lawmatics OAuth Token Retriever")
print("=" * 70)
print()
print("IMPORTANT: Before continuing, update your Lawmatics OAuth app:")
print()
print("  Redirect URI: http://localhost:8888/callback")
print()
input("Press Enter when you've updated the Redirect URI in Lawmatics...")
print()

# Start local server
print("Starting local callback server on http://localhost:8888...")
server_thread = threading.Thread(target=run_server)
server_thread.daemon = True
server_thread.start()

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

print("Opening browser for authorization...")
print()
webbrowser.open(auth_url)

print("Waiting for authorization...")
print("(A browser window should open - click 'Authorize')")
print()

# Wait for callback
server_thread.join(timeout=120)  # 2 minute timeout

if authorization_code:
    print("✅ Authorization code received!")
    print()
    print("=" * 70)
    print("Exchanging code for access token...")
    print("=" * 70)
    print()

    # Exchange code for token
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
        print("REFRESH TOKEN (save for later):")
        print("-" * 70)
        print(refresh_token)
        print()
        print("=" * 70)
        print(f"Expires in: {expires_in} seconds")
        print()
        print("=" * 70)
        print("NEXT STEPS:")
        print("=" * 70)
        print()
        print("1. Go to FastMCP Cloud dashboard")
        print("2. Navigate to Settings → Environment Variables")
        print("3. Add this variable:")
        print()
        print(f"   LAWMATICS_ACCESS_TOKEN={access_token}")
        print()
        print("4. Update Redirect URI back to:")
        print("   https://lawmatics-mcp-v1-0.fastmcp.app/oauth/callback")
        print()
        print("5. Save and redeploy!")
        print()
        print("=" * 70)
    else:
        print(f"❌ Error: HTTP {response.status_code}")
        print(response.text)
else:
    print("❌ Timeout: No authorization code received")
    print()
    print("Please try again and make sure to click 'Authorize' in the browser.")
