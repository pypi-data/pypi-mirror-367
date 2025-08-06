#!/usr/bin/env python3
"""
Test script to verify HTTPS setup for Meta Ads MCP
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from meta_ads_mcp.core.callback_server import start_callback_server, shutdown_callback_server, create_ssl_context
from meta_ads_mcp.core.auth import auth_manager
import time
import requests
import urllib3

# Disable SSL warnings for testing
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_ssl_context():
    """Test SSL context creation"""
    print("Testing SSL context creation...")
    context, cert_dir = create_ssl_context()
    
    if context:
        print("✅ SSL context created successfully")
        print(f"📁 Certificate directory: {cert_dir}")
        return True
    else:
        print("❌ SSL context creation failed")
        return False

def test_https_server():
    """Test HTTPS server startup"""
    print("\nTesting HTTPS server startup...")
    
    try:
        port, is_https = start_callback_server(use_https=True)
        protocol = "https" if is_https else "http"
        
        print(f"✅ Server started on {protocol}://localhost:{port}")
        print(f"🔒 HTTPS enabled: {is_https}")
        
        # Test server connectivity
        print(f"\nTesting server connectivity...")
        try:
            url = f"{protocol}://localhost:{port}/callback"
            response = requests.get(url, verify=False, timeout=5)
            print(f"✅ Server responds with status: {response.status_code}")
        except Exception as e:
            print(f"⚠️  Server connectivity test failed: {e}")
        
        # Clean up
        shutdown_callback_server()
        print("🧹 Server shut down")
        
        return is_https
        
    except Exception as e:
        print(f"❌ Server startup failed: {e}")
        return False

def test_auth_url_generation():
    """Test OAuth URL generation with HTTPS"""
    print("\nTesting OAuth URL generation...")
    
    try:
        # Start server
        port, is_https = start_callback_server(use_https=True)
        protocol = "https" if is_https else "http"
        
        # Update auth manager
        auth_manager.redirect_uri = f"{protocol}://localhost:{port}/callback"
        auth_url = auth_manager.get_auth_url()
        
        print(f"📝 Generated OAuth URL: {auth_url}")
        print(f"🔗 Redirect URI: {auth_manager.redirect_uri}")
        
        if "https://" in auth_manager.redirect_uri:
            print("✅ HTTPS redirect URI configured")
        else:
            print("⚠️  Using HTTP redirect URI (fallback mode)")
        
        # Clean up
        shutdown_callback_server()
        
        return is_https
        
    except Exception as e:
        print(f"❌ Auth URL generation failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🔧 Meta Ads MCP HTTPS Setup Test")
    print("=" * 40)
    
    # Test SSL context
    ssl_works = test_ssl_context()
    
    # Test HTTPS server
    https_works = test_https_server()
    
    # Test auth URL generation
    auth_works = test_auth_url_generation()
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 Test Summary:")
    print(f"SSL Context: {'✅' if ssl_works else '❌'}")
    print(f"HTTPS Server: {'✅' if https_works else '❌'}")
    print(f"Auth URL Generation: {'✅' if auth_works else '❌'}")
    
    if https_works:
        print("\n🎉 HTTPS is working! Your Facebook app should accept the redirect URI:")
        print("   https://localhost:8443/callback")
    else:
        print("\n⚠️  HTTPS not available. Using HTTP fallback:")
        print("   http://localhost:8888/callback")
        print("\n💡 To enable HTTPS:")
        print("   1. Ensure OpenSSL is installed: openssl version")
        print("   2. Check if port 8443 is available")
        print("   3. Use Facebook app development mode for HTTP")
    
    print("\n📖 For complete setup instructions, see HTTPS_SETUP.md")

if __name__ == "__main__":
    main()