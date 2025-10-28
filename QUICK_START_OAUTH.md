# 🚀 Quick Start: OAuth Setup for Lawmatics

## ⚡ TL;DR - What You Need Right Now

### When Lawmatics Asks for Callback URL:

**Choose based on where you'll run the server:**

| Environment | Callback URL |
|-------------|--------------|
| **Local Development** | `http://localhost:8000/oauth/callback` |
| **FastMCP Cloud** | `https://lawmatics-mcp.fastmcp.app/oauth/callback` |
| **Custom Domain** | `https://your-domain.com/oauth/callback` |

### Then Follow These 5 Steps:

1. **In Lawmatics**: Create OAuth app with your callback URL ✅
2. **Copy**: Client ID and Client Secret (save securely!) 🔑
3. **Add to `.env`**: Paste credentials 📝
4. **Run OAuth flow**: Get access token 🔄
5. **Test**: Run `uv run python test_phone_search.py` ✨

---

## 📋 Step-by-Step Instructions

### 1️⃣ Register OAuth Application in Lawmatics

```
Lawmatics Dashboard → Settings → API → OAuth Applications

Application Name: Lawmatics MCP Server
Description: MCP server for AI/LLM access
Callback URL: http://localhost:8000/oauth/callback  ← Use this for local dev
Scopes: ✓ Read  ✓ Write

→ Save and copy Client ID & Client Secret
```

### 2️⃣ Update Your .env File

```bash
cd Lawmatics-MCP
nano .env
```

Add these lines:
```env
LAWMATICS_CLIENT_ID=paste_your_client_id_here
LAWMATICS_CLIENT_SECRET=paste_your_client_secret_here
LAWMATICS_REDIRECT_URI=http://localhost:8000/oauth/callback
LAWMATICS_USE_PKCE=false
```

Save and exit (Ctrl+O, Enter, Ctrl+X)

### 3️⃣ Get Your Access Token

**Option A: Using Your Browser (Easiest)**

> Tip: set `LAWMATICS_USE_PKCE=false` in your `.env` before running the helper scripts so they generate the same minimal request Lawmatics expects.

1. Build the minimal authorize URL (replace `YOUR_CLIENT_ID` and ensure the redirect matches what you configured in Lawmatics):
   ```
   https://app.lawmatics.com/oauth/authorize?client_id=YOUR_CLIENT_ID&redirect_uri=https://lawmatics-mcp.fastmcp.app/oauth/callback&response_type=code
   ```
   *Lawmatics currently rejects plain `http://localhost` callbacks—use your HTTPS FastMCP Cloud URL or an HTTPS tunnel.*

2. Open the link in your browser and click **Grant Access**.
3. You should land on `https://lawmatics-mcp.fastmcp.app/oauth/callback?code=...`. Seeing a **404 Not Found** page is normal; copy the `code` value from the address bar.

**Option B: Exchange Code for Token**

Run this command (replace the placeholders):
```bash
curl -X POST https://api.lawmatics.com/oauth/token \
  -d "grant_type=authorization_code" \
  -d "code=YOUR_CODE_FROM_STEP_5" \
  -d "redirect_uri=https://lawmatics-mcp.fastmcp.app/oauth/callback" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET"
```

You'll get back:
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "def789...",
  "expires_in": 3600
}
```

Copy the `access_token` value.

> Want to use PKCE anyway? Include `&scope=read+write&code_challenge=...` in the authorize URL and pass `-d "code_verifier=YOUR_VERIFIER"` to the curl command. The helper scripts will print the verifier when `LAWMATICS_USE_PKCE=true`.

### 4️⃣ Add Access Token to .env

```bash
nano .env
```

Add this line:
```env
LAWMATICS_ACCESS_TOKEN=paste_your_access_token_here
```

### 5️⃣ Test It!

```bash
uv run python test_phone_search.py
```

If it works, you'll see contact and matter data! 🎉

---

## 🔧 For FastMCP Cloud Deployment

### Update Your Callback URL

1. **In Lawmatics OAuth app settings**:
   - Change callback URL to: `https://lawmatics-mcp.fastmcp.app/oauth/callback`
   - (Replace `lawmatics-mcp` with your actual project name)

2. **In FastMCP Cloud dashboard**:
   - Add environment variables:
     ```
     LAWMATICS_CLIENT_ID = your_client_id
     LAWMATICS_CLIENT_SECRET = your_client_secret
     LAWMATICS_REDIRECT_URI = https://lawmatics-mcp.fastmcp.app/oauth/callback
     LAWMATICS_ACCESS_TOKEN = your_access_token
     LAWMATICS_USE_PKCE = false
     ```

3. **Deploy!**

---

## 🆘 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| "Invalid redirect_uri" | Callback URL doesn't match what you registered in Lawmatics |
| "Invalid client" | Client ID or Secret is wrong - check for typos |
| "Access denied" | You didn't authorize the app - try OAuth flow again |
| "Token expired" | Get a new access token using the refresh token |
| Callback returns 404 | Expected when using FastMCP Cloud; the code is still in the URL |

---

## 📞 Need Help?

- **Full Guide**: See [OAUTH_SETUP_GUIDE.md](OAUTH_SETUP_GUIDE.md)
- **Lawmatics Support**: api@lawmatics.com
- **Docs**: https://docs.lawmatics.com

---

> To match Lawmatics' minimal OAuth spec, set `LAWMATICS_USE_PKCE=false` in your `.env` so the helper scripts and client omit PKCE fields.

## ✅ Checklist

Before running your server:

- [ ] OAuth app created in Lawmatics
- [ ] Callback URL set (local or cloud)
- [ ] Client ID copied to `.env`
- [ ] Client Secret copied to `.env`
- [ ] OAuth flow completed
- [ ] Access token added to `.env`
- [ ] Test successful: `uv run python test_phone_search.py`

**You're ready to go!** 🚀
