#!/usr/bin/env python3
"""
Quick test to find the correct Composer API endpoints.
"""

import os
import httpx
from dotenv import load_dotenv

load_dotenv()

COMPOSER_API_KEY = os.getenv("COMPOSER_API_KEY", "").strip()
COMPOSER_API_SECRET = os.getenv("COMPOSER_API_SECRET", "").strip()

def test_endpoint(base_url, path, description, headers):
    """Test a specific endpoint."""
    url = f"{base_url}{path}"
    
    print(f"\n🔍 Testing: {description}")
    print(f"   URL: {url}")
    
    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(url, headers=headers)
            print(f"   Status: {resp.status_code}")
            if resp.status_code < 400:
                print(f"   ✅ Success!")
                try:
                    data = resp.json()
                    print(f"   Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                    if isinstance(data, dict) and 'accounts' in data:
                        print(f"   Found {len(data.get('accounts', []))} accounts")
                except:
                    print(f"   Response: {resp.text[:200]}...")
            else:
                print(f"   ❌ Error: {resp.text[:200]}...")
    except Exception as e:
        print(f"   ❌ Exception: {e}")

def main():
    """Test various Composer API endpoint combinations."""
    print("🔍 Composer API Endpoint Discovery")
    print("=" * 40)
    
    # Test different authentication methods
    auth_methods = [
        {
            "name": "Bearer + X-API-Key",
            "headers": {
                "Authorization": f"Bearer {COMPOSER_API_SECRET}",
                "X-API-Key": COMPOSER_API_KEY,
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
        },
        {
            "name": "Bearer only",
            "headers": {
                "Authorization": f"Bearer {COMPOSER_API_SECRET}",
                "Accept": "application/json",
            }
        },
        {
            "name": "X-API-Key only",
            "headers": {
                "X-API-Key": COMPOSER_API_KEY,
                "Accept": "application/json",
            }
        },
        {
            "name": "x-origin + x-api-key-id (old format)",
            "headers": {
                "x-origin": "public-api",
                "x-api-key-id": COMPOSER_API_KEY,
                "Authorization": f"Bearer {COMPOSER_API_SECRET}",
                "accept": "application/json",
            }
        }
    ]
    
    # Test different base URLs
    base_urls = [
        "https://api.composer.trade",
        "https://app.composer.trade/api",
        "https://api.composer.trade/api",
        "https://app.composer.trade",
        "https://composer.trade/api",
        "https://composer.trade"
    ]
    
    # Test different account endpoints
    account_paths = [
        "/v1/accounts",
        "/accounts",
        "/v1/portfolio/accounts",
        "/portfolio/accounts",
        "/api/v1/accounts",
        "/api/accounts",
        "/accounts/list",
        "/v1/accounts/list"
    ]
    
    for auth_method in auth_methods:
        print(f"\n🔐 Testing authentication: {auth_method['name']}")
        print("-" * 50)
        
        for base_url in base_urls:
            for path in account_paths:
                test_endpoint(base_url, path, f"{base_url}{path}", auth_method['headers'])

if __name__ == "__main__":
    main()
