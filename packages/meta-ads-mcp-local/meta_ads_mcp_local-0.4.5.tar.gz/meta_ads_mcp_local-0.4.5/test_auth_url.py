#!/usr/bin/env python3
"""
Test script to verify the OAuth URL uses HTTPS redirect URI
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from meta_ads_mcp.core.callback_server import start_callback_server, shutdown_callback_server
from meta_ads_mcp.core.auth import auth_manager
import time

def test_auth_url_generation():
    """Test that OAuth URL generation uses HTTPS redirect URI"""
    print("🔧 Testing OAuth URL Generation with HTTPS")
    print("=" * 50)
    
    try:
        # Start the callback server (should use HTTPS)
        print("Starting callback server...")
        port, is_https = start_callback_server(use_https=True)
        protocol = "https" if is_https else "http"
        
        print(f"✅ Server started on {protocol}://localhost:{port}")
        print(f"🔒 HTTPS enabled: {is_https}")
        
        # Update auth manager redirect URI (this simulates what happens in authenticate())
        auth_manager.redirect_uri = f"{protocol}://localhost:{port}/callback"
        print(f"📝 Updated auth_manager.redirect_uri: {auth_manager.redirect_uri}")
        
        # Generate the OAuth URL
        oauth_url = auth_manager.get_auth_url()
        print(f"🔗 Generated OAuth URL:")
        print(f"   {oauth_url}")
        
        # Check if the URL contains HTTPS redirect
        if "redirect_uri=https://localhost:" in oauth_url:
            print("✅ SUCCESS: OAuth URL uses HTTPS redirect URI!")
        elif "redirect_uri=http://localhost:" in oauth_url:
            print("⚠️  FALLBACK: OAuth URL uses HTTP redirect URI (HTTPS failed)")
        else:
            print("❌ ERROR: Unexpected redirect URI in OAuth URL")
        
        # Clean up
        shutdown_callback_server()
        print("🧹 Server shut down")
        
        return is_https
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Run the test"""
    https_works = test_auth_url_generation()
    
    print("\n" + "=" * 50)
    if https_works:
        print("🎉 HTTPS OAuth URL generation is working!")
        print("📋 Your Facebook app should have this redirect URI:")
        print("   https://localhost:8443/callback")
    else:
        print("⚠️  Using HTTP fallback. Add this redirect URI:")
        print("   http://localhost:8888/callback")
    
    print("\n💡 Update your MCP configuration to use:")
    print('   "command": "uvx",')
    print('   "args": ["meta-ads-mcp-local", "--app-id", "1356516965651373"]')

if __name__ == "__main__":
    main()