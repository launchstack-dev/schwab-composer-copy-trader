#!/usr/bin/env python3
"""
Test script for Composer API integration.
This script tests the updated Composer API endpoints and authentication.
"""

import os
import sys
from dotenv import load_dotenv

def test_composer_api():
    """Test the Composer API integration."""
    print("🧪 Testing Composer API Integration")
    print("=" * 40)
    
    # Load environment variables
    load_dotenv()
    
    # Check if Composer credentials are configured
    api_key = os.getenv('COMPOSER_API_KEY', '').strip()
    api_secret = os.getenv('COMPOSER_API_SECRET', '').strip()
    account_num = os.getenv('COMPOSER_ACCOUNT_NUM', '').strip()
    
    if not all([api_key, api_secret, account_num]):
        print("❌ Composer credentials not configured")
        print("   Please set COMPOSER_API_KEY, COMPOSER_API_SECRET, and COMPOSER_ACCOUNT_NUM in your .env file")
        return False
    
    print("✅ Composer credentials found")
    
    try:
        # Import and test the Composer API
        from composer_api import (
            list_accounts, 
            get_composer_percentages, 
            ComposerAPIError
        )
        
        print("\n🔗 Testing API Connection...")
        
        # Test 1: List accounts
        print("   Testing list_accounts()...")
        accounts = list_accounts()
        print(f"   ✅ Found {len(accounts.get('accounts', []))} accounts")
        
        # Test 2: Get percentages
        print("   Testing get_composer_percentages()...")
        percentages = get_composer_percentages()
        
        if percentages and percentages.get('assets'):
            print(f"   ✅ Retrieved {len(percentages['assets'])} assets")
            print(f"   ✅ Portfolio total: ${percentages.get('portfolio_total', 0):,.2f}")
            
            # Show some sample assets
            print("\n   Sample assets:")
            for i, (symbol, data) in enumerate(list(percentages['assets'].items())[:5]):
                pct = percentages['percentages'].get(symbol, 0)
                print(f"     {symbol}: {pct}% (${data['market_value']:,.2f})")
            
            if len(percentages['assets']) > 5:
                print(f"     ... and {len(percentages['assets']) - 5} more assets")
        else:
            print("   ⚠️  No assets found in portfolio")
        
        print("\n✅ All Composer API tests passed!")
        return True
        
    except ComposerAPIError as e:
        print(f"❌ Composer API Error: {e}")
        return False
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("   Make sure all dependencies are installed: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False

def test_holdings_source():
    """Test the holdings source integration."""
    print("\n🧪 Testing Holdings Source Integration")
    print("=" * 40)
    
    try:
        from holdings_source import get_percentages, check_for_change, save_changes
        
        print("   Testing get_percentages()...")
        percentages = get_percentages()
        
        if percentages and percentages.get('assets'):
            print(f"   ✅ Retrieved {len(percentages['assets'])} assets from holdings source")
            
            print("   Testing check_for_change()...")
            has_changes = check_for_change()
            print(f"   ✅ Change detection: {has_changes}")
            
            print("   Testing save_changes()...")
            save_changes(percentages)
            print("   ✅ Changes saved successfully")
            
        else:
            print("   ⚠️  No assets found in holdings source")
        
        print("\n✅ All Holdings Source tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Holdings Source Error: {e}")
        return False

def main():
    """Main test function."""
    print("🚀 Composer API Integration Test Suite")
    print("=" * 50)
    
    # Test Composer API
    composer_ok = test_composer_api()
    
    # Test holdings source (only if Composer API works)
    if composer_ok:
        holdings_ok = test_holdings_source()
    else:
        holdings_ok = False
        print("\n⏭️  Skipping holdings source tests due to Composer API failure")
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 20)
    
    if composer_ok and holdings_ok:
        print("✅ All tests passed!")
        print("\n🎉 Your Composer API integration is working correctly!")
        print("   You can now run: python copy_trade.py")
    else:
        print("❌ Some tests failed")
        print("\n🔧 Please check your configuration and try again")
        if not composer_ok:
            print("   - Verify Composer API credentials")
            print("   - Check network connectivity")
        if not holdings_ok:
            print("   - Check TRADE_SOURCE setting in .env")
            print("   - Verify account permissions")
    
    return composer_ok and holdings_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
