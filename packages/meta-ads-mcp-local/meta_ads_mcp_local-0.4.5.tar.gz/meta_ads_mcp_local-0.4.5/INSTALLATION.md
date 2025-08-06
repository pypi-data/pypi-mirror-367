# Installation Options for meta-ads-mcp-local

Since the package is built but not yet published to PyPI, here are three ways to use it:

## Option 1: Install from Local Directory (Recommended)

```bash
# Install directly from the local directory
uvx --from /path/to/meta-ads-mcp-local meta-ads-mcp-local

# Or install it permanently
pip install /path/to/meta-ads-mcp-local
```

**MCP Configuration:**
```json
{
  "mcpServers": {
    "meta-ads": {
      "command": "meta-ads-mcp-local",
      "args": ["--app-id", "YOUR_META_APP_ID"],
      "env": {
        "META_APP_ID": "YOUR_META_APP_ID",
        "META_APP_SECRET": "YOUR_META_APP_SECRET"
      }
    }
  }
}
```

## Option 2: Install from Built Wheel

```bash
# Install from the built wheel file
uvx --from dist/meta_ads_mcp_local-0.3.8-py3-none-any.whl meta-ads-mcp-local

# Or with pip
pip install dist/meta_ads_mcp_local-0.3.8-py3-none-any.whl
```

## Option 3: Use Development Mode

```bash
# Install in development mode
pip install -e .
```

**MCP Configuration:**
```json
{
  "mcpServers": {
    "meta-ads": {
      "command": "python",
      "args": ["-m", "meta_ads_mcp", "--app-id", "YOUR_META_APP_ID"],
      "env": {
        "META_APP_ID": "YOUR_META_APP_ID",
        "META_APP_SECRET": "YOUR_META_APP_SECRET"
      }
    }
  }
}
```

## Publishing to PyPI (Optional)

To publish to PyPI:

1. Create account at https://pypi.org/account/register/
2. Generate API token at https://pypi.org/manage/account/token/
3. Configure credentials:
   ```bash
   # Option A: Use environment variables
   export TWINE_USERNAME=__token__
   export TWINE_PASSWORD=your_api_token_here
   
   # Option B: Use .pypirc file
   echo "[pypi]
   username = __token__
   password = your_api_token_here" > ~/.pypirc
   ```
4. Upload package:
   ```bash
   twine upload dist/*
   ```

## Features of meta-ads-mcp-local

This fork includes:

✅ **HTTPS Support** - Automatic SSL certificate generation for localhost OAuth callbacks
✅ **Facebook OAuth Compliance** - Works with Facebook's HTTPS redirect requirements  
✅ **Automatic Fallback** - Falls back to HTTP if HTTPS setup fails
✅ **Self-Signed Certificates** - Generates temporary SSL certificates for development
✅ **Enhanced Security** - Better handling of OAuth flows

## HTTPS OAuth Callback URLs

The package automatically uses:
- **HTTPS**: `https://localhost:8443/callback` (preferred)
- **HTTP Fallback**: `http://localhost:8888/callback` (if HTTPS fails)

Make sure to add both URLs to your Facebook app's Valid OAuth Redirect URIs.