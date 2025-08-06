# HTTPS Setup for Facebook OAuth

This document explains how the Meta Ads MCP server handles Facebook's HTTPS requirement for OAuth redirects.

## The Problem

Facebook requires HTTPS for OAuth redirect URIs in production apps. Using `http://localhost` URLs will result in the error:
```
This redirect failed because the redirect URI is not whitelisted in the app's Client OAuth Settings.
```

## The Solution

The Meta Ads MCP server automatically attempts to create an HTTPS localhost server for OAuth callbacks. Here's how it works:

### 1. Automatic HTTPS Setup

When you authenticate, the server will:
1. Generate a self-signed SSL certificate for localhost
2. Start an HTTPS server on port 8443 (or next available port)
3. Use `https://localhost:8443/callback` as the redirect URI

### 2. Facebook App Configuration

In your Facebook app settings, you need to add the HTTPS callback URL to your Valid OAuth Redirect URIs:

1. Go to your [Facebook Developer Console](https://developers.facebook.com/apps/)
2. Select your app
3. Go to **Products** → **Facebook Login** → **Settings**
4. Add `https://localhost:8443/callback` to **Valid OAuth Redirect URIs**
5. Save changes

### 3. SSL Certificate Warning

When you first visit the HTTPS callback URL, your browser will show a security warning because it's a self-signed certificate. This is normal and expected for local development.

To proceed:
- **Chrome/Edge**: Click "Advanced" → "Proceed to localhost (unsafe)"
- **Firefox**: Click "Advanced" → "Accept the Risk and Continue"
- **Safari**: Click "Show Details" → "visit this website"

### 4. Fallback to HTTP

If HTTPS setup fails (e.g., OpenSSL not available), the server will fall back to HTTP mode. In this case:

1. Use your Facebook app in **Development Mode**
2. Add test users to your app
3. Only test users can authenticate in development mode

## Requirements

- **OpenSSL**: Required for generating SSL certificates (usually pre-installed on macOS/Linux)
- **Facebook App in Production Mode**: Required for HTTPS callbacks with real users

## Troubleshooting

### "Could not create SSL certificate"
- Ensure OpenSSL is installed: `openssl version`
- Check if the port 8443 is available
- Try running with HTTP fallback (development mode)

### "SSL: CERTIFICATE_VERIFY_FAILED"
- This is expected for self-signed certificates
- Click through the browser security warning
- The certificate is valid for localhost only

### "Invalid redirect URI"
- Ensure `https://localhost:8443/callback` is added to your Facebook app
- Check if the port number matches what the server is using
- Verify your app is in Production mode (not Development)

## Alternative Solutions

1. **Use Pipeboard Authentication**: Set `PIPEBOARD_API_TOKEN` environment variable for managed authentication
2. **Use ngrok**: Create a public HTTPS tunnel to your localhost
3. **Development Mode**: Use Facebook app development mode with HTTP callbacks

## Security Note

The self-signed certificates are generated temporarily and deleted when the server shuts down. They are only valid for localhost and cannot be used to intercept traffic to other domains.