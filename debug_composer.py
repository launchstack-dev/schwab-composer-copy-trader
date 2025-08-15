#!/usr/bin/env python3
"""
Debug script to see the actual Composer API data structure.
"""

import os
import json
from dotenv import load_dotenv
from composer_api import list_accounts, get_account_data, ComposerAPIError

load_dotenv()

def main():
    """Debug the Composer API data structure."""
    print("🔍 Debugging Composer API Data Structure")
    print("=" * 50)
    
    try:
        # Test 1: List accounts
        print("\n📋 1. Testing list_accounts()...")
        accounts = list_accounts()
        print(f"✅ Found {len(accounts.get('accounts', []))} accounts")
        
        # Show account details
        for i, account in enumerate(accounts.get('accounts', [])):
            print(f"   Account {i+1}:")
            print(f"     UUID: {account.get('account_uuid', 'N/A')}")
            print(f"     Number: {account.get('account_number', 'N/A')}")
            print(f"     Name: {account.get('name', 'N/A')}")
            print(f"     Type: {account.get('account_type', 'N/A')}")
        
        # Test 2: Get holdings for the first account
        if accounts.get('accounts'):
            account_uuid = accounts['accounts'][0]['account_uuid']
            account_num = accounts['accounts'][0].get('account_number', 'Unknown')
            
            print(f"\n📊 2. Testing get_account_data() for account {account_num}...")
            holdings_data = get_account_data(account_uuid)
            
            print(f"✅ Raw holdings data structure:")
            print(json.dumps(holdings_data, indent=2))
            
            # Test 3: Check if we can get the raw API response
            print(f"\n🔍 3. Testing raw API response...")
            from composer_api import _get
            path = f"/api/v0.1/portfolio/accounts/{account_uuid}/holding-stats"
            raw_data = _get(path)
            print(f"✅ Raw API response:")
            print(json.dumps(raw_data, indent=2))
            
        else:
            print("❌ No accounts found")
            
    except ComposerAPIError as e:
        print(f"❌ Composer API Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")

if __name__ == "__main__":
    main()
