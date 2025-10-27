# Lawmatics OAuth 2.0 Setup Guide

## 🔐 OAuth Authentication Overview

Lawmatics uses **OAuth 2.0** for API authentication, which requires:
1. **Client ID** - Your application identifier
2. **Client Secret** - Your application password (keep this secure!)
3. **Redirect URI / Callback URL** - Where Lawmatics sends users after authorization

## 📋 Step-by-Step Setup

### Step 1: Choose Your Callback URL

**Before registering your OAuth application in Lawmatics**, you need to know your callback URL:

#### For Local Development:
```
http://localhost:8000/oauth/callback
```

#### For FastMCP Cloud Deployment:
```
https://lawmatics-mcp.fastmcp.app/oauth/callback
```
**Note**: Replace `lawmatics-mcp` with your actual project name on FastMCP Cloud

#### For Custom Domain:
```
https://your-custom-domain.com/oauth/callback
```

---

### Step 2: Register OAuth Application in Lawmatics

1. **Log into Lawmatics**
   - Go to https://app.lawmatics.com

2. **Navigate to API Settings**
   - Click **Settings** (gear icon)
   - Go to **Integrations** or **API** section
   - Look for **OAuth Applications** or **API Access**

3. **Create New OAuth Application**
   - Click "Create New Application" or "Add OAuth App"
   - Fill in the application details:

   ```
   Application Name: Lawmatics MCP Server
   Description: Model Context Protocol server for AI/LLM access
   Callback URL: http://localhost:8000/oauth/callback
   Scopes: read, write (select all needed permissions)
   ```

4. **Save and Copy Credentials**
   After saving, Lawmatics will show you:
   - **Client ID**: `abc123...` (copy this)
   - **Client Secret**: `xyz789...` (copy this - shown only once!)

   ⚠️ **IMPORTANT**: Save the Client Secret immediately! You won't see it again.

---

### Step 3: Configure Your MCP Server

#### Option A: Using Environment Variables (Recommended)

1. **Edit your `.env` file:**
   ```bash
   cd Lawmatics-MCP
   nano .env
   ```

2. **Add your OAuth credentials:**
   ```env
   # Lawmatics OAuth 2.0 Credentials
   LAWMATICS_CLIENT_ID=your_client_id_from_step_2
   LAWMATICS_CLIENT_SECRET=your_client_secret_from_step_2
   LAWMATICS_REDIRECT_URI=http://localhost:8000/oauth/callback
   ```

3. **Save the file** (Ctrl+O, Enter, Ctrl+X)

#### Option B: For FastMCP Cloud

1. **Go to FastMCP Cloud Dashboard**
   - Visit https://fastmcp.cloud
   - Select your project

2. **Add Environment Variables**
   ```
   LAWMATICS_CLIENT_ID = your_client_id_here
   LAWMATICS_CLIENT_SECRET = your_client_secret_here
   LAWMATICS_REDIRECT_URI = https://lawmatics-mcp.fastmcp.app/oauth/callback
   ```

3. **Deploy or Redeploy** your server

---

### Step 4: Obtain Access Token

Now you need to complete the OAuth flow to get an access token:

#### Manual OAuth Flow (One-Time Setup)

1. **Start your MCP server:**
   ```bash
   uv run python -m app
   ```

2. **Visit the authorization URL in your browser:**
   ```
   https://app.lawmatics.com/oauth/authorize?client_id=YOUR_CLIENT_ID&redirect_uri=http://localhost:8000/oauth/callback&response_type=code&scope=read+write
   ```

   Replace `YOUR_CLIENT_ID` with your actual Client ID.

3. **Authorize the application**
   - Log into Lawmatics (if not already logged in)
   - Review the permissions requested
   - Click "Authorize" or "Allow"

4. **You'll be redirected to:**
   ```
   http://localhost:8000/oauth/callback?code=AUTHORIZATION_CODE
   ```

5. **Copy the authorization code** from the URL (the part after `code=`)

6. **Exchange the code for an access token** using this curl command:
   ```bash
   curl -X POST https://api.lawmatics.com/oauth/token \
     -d "grant_type=authorization_code" \
     -d "code=AUTHORIZATION_CODE" \
     -d "redirect_uri=http://localhost:8000/oauth/callback" \
     -d "client_id=YOUR_CLIENT_ID" \
     -d "client_secret=YOUR_CLIENT_SECRET"
   ```

7. **You'll receive a JSON response:**
   ```json
   {
     "access_token": "your_access_token_here",
     "token_type": "Bearer",
     "expires_in": 3600,
     "refresh_token": "your_refresh_token_here",
     "scope": "read write"
   }
   ```

8. **Add the access token to your `.env` file:**
   ```env
   LAWMATICS_ACCESS_TOKEN=your_access_token_here
   ```

---

### Step 5: Test Your Connection

1. **Run the test script:**
   ```bash
   uv run python test_phone_search.py
   ```

2. **Or test with a simple request:**
   ```bash
   curl -X GET "https://api.lawmatics.com/v1/users" \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
   ```

3. **If successful**, you should see JSON data returned!

---

## 🔄 Token Refresh

Access tokens typically expire after 1 hour. To refresh:

```bash
curl -X POST https://api.lawmatics.com/oauth/token \
  -d "grant_type=refresh_token" \
  -d "refresh_token=YOUR_REFRESH_TOKEN" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET"
```

The MCP server includes automatic token refresh logic in `app/oauth.py`.

---

## 📝 Complete .env File Example

```env
# Lawmatics OAuth 2.0 Credentials
LAWMATICS_CLIENT_ID=abc123def456ghi789
LAWMATICS_CLIENT_SECRET=xyz789uvw456rst123
LAWMATICS_REDIRECT_URI=http://localhost:8000/oauth/callback

# Access Token (obtained from OAuth flow)
LAWMATICS_ACCESS_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# API Base URL
LAWMATICS_BASE_URL=https://api.lawmatics.com/v1/

# Server Configuration
HOST=0.0.0.0
MCP_PORT=8000
LOG_LEVEL=INFO
DEBUG=false
ENVIRONMENT=development
```

---

## 🚨 Troubleshooting

### Issue: "Invalid Redirect URI"
**Solution**: Make sure the Redirect URI in your `.env` matches exactly what you registered in Lawmatics (including protocol: `http://` vs `https://`)

### Issue: "Invalid Client Credentials"
**Solution**:
- Verify your Client ID and Client Secret are correct
- Check for extra spaces or line breaks
- Regenerate credentials in Lawmatics if needed

### Issue: "Token Expired"
**Solution**: Use the refresh token to get a new access token (see Token Refresh section above)

### Issue: "Scope Error"
**Solution**: When creating the OAuth app in Lawmatics, ensure you selected all necessary scopes (read, write, etc.)

---

## 🔒 Security Best Practices

1. **Never commit credentials to Git**
   - `.env` is in `.gitignore`
   - Use `.env.example` as a template only

2. **Use different credentials for different environments**
   - Dev: One set of credentials
   - Production: Different credentials

3. **Rotate credentials periodically**
   - Regenerate Client Secret every 90 days
   - Revoke old credentials after rotation

4. **Store production credentials securely**
   - Use FastMCP Cloud environment variables (encrypted)
   - Or use a secrets manager (AWS Secrets Manager, etc.)

5. **Limit OAuth scopes**
   - Only request permissions you actually need
   - Use read-only scopes when possible

---

## 📚 Additional Resources

- **Lawmatics API Docs**: https://docs.lawmatics.com
- **Lawmatics Support**: api@lawmatics.com
- **OAuth 2.0 Spec**: https://oauth.net/2/
- **FastMCP Docs**: https://gofastmcp.com

---

## ✅ Quick Checklist

Before running your MCP server, verify:

- [ ] OAuth application created in Lawmatics
- [ ] Callback URL registered (matches your deployment)
- [ ] Client ID and Secret saved securely
- [ ] `.env` file configured with credentials
- [ ] Access token obtained via OAuth flow
- [ ] Test connection successful
- [ ] Tokens refresh automatically

---

## 🎯 Next Steps

Once OAuth is configured:

1. **Test the phone search feature:**
   ```bash
   uv run python test_phone_search.py
   ```

2. **Start the MCP server:**
   ```bash
   uv run python -m app
   ```

3. **Deploy to FastMCP Cloud** with OAuth credentials

Your Lawmatics MCP Server is now ready to authenticate and interact with the Lawmatics API! 🚀
