#!/usr/bin/env python3
"""
Configuration validation script for the copy trader.
This script helps verify that all required configuration is set up correctly.
"""

import os
import sys
from dotenv import load_dotenv
from typing import Dict, List, Tuple

def check_env_file() -> bool:
    """Check if .env file exists and load it."""
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("   Please copy example.env to .env and fill in your configuration.")
        return False
    
    load_dotenv()
    print("✅ .env file found and loaded")
    return True

def validate_composer_config() -> Tuple[bool, List[str]]:
    """Validate Composer API configuration."""
    errors = []
    
    # Check required environment variables
    required_vars = {
        'COMPOSER_API_KEY': 'Composer API Key',
        'COMPOSER_API_SECRET': 'Composer API Secret',
        'COMPOSER_ACCOUNT_NUM': 'Composer Account Number'
    }
    
    for var, description in required_vars.items():
        value = os.getenv(var, '').strip()
        if not value:
            errors.append(f"Missing {description} ({var})")
        else:
            print(f"✅ {description} configured")
    
    return len(errors) == 0, errors

def validate_schwab_config() -> Tuple[bool, List[str]]:
    """Validate Schwab API configuration."""
    errors = []
    
    # Check required environment variables
    required_vars = {
        'SCWAHB_API_KEY': 'Schwab API Key',
        'SCWAHB_SECRET_KEY': 'Schwab Secret Key',
        'SCHWAB_ACCOUNT_NUMS': 'Schwab Account Numbers'
    }
    
    for var, description in required_vars.items():
        value = os.getenv(var, '').strip()
        if not value:
            errors.append(f"Missing {description} ({var})")
        else:
            print(f"✅ {description} configured")
    
    # Validate account numbers format
    account_nums = os.getenv('SCHWAB_ACCOUNT_NUMS', '').strip()
    if account_nums:
        try:
            accounts = [acc.strip() for acc in account_nums.split(',') if acc.strip()]
            if not accounts:
                errors.append("SCHWAB_ACCOUNT_NUMS is empty or invalid format")
            else:
                print(f"✅ Found {len(accounts)} Schwab account(s): {accounts}")
        except Exception as e:
            errors.append(f"Invalid SCHWAB_ACCOUNT_NUMS format: {e}")
    
    return len(errors) == 0, errors

def validate_alpaca_config() -> Tuple[bool, List[str]]:
    """Validate Alpaca API configuration."""
    errors = []
    
    # Check required environment variables
    required_vars = {
        'ALPACA_API_KEY': 'Alpaca API Key',
        'ALPACA_SECRET_KEY': 'Alpaca Secret Key'
    }
    
    for var, description in required_vars.items():
        value = os.getenv(var, '').strip()
        if not value:
            errors.append(f"Missing {description} ({var})")
        else:
            print(f"✅ {description} configured")
    
    # Check PAPER setting
    paper = os.getenv('PAPER', 'true').lower()
    if paper not in ['true', 'false']:
        errors.append("PAPER must be 'true' or 'false'")
    else:
        print(f"✅ Paper trading mode: {paper}")
    
    return len(errors) == 0, errors

def validate_trade_settings() -> Tuple[bool, List[str]]:
    """Validate trade settings configuration."""
    errors = []
    
    # Check TRADE_SOURCE
    trade_source = os.getenv('TRADE_SOURCE', '').lower().strip()
    if trade_source not in ['alpaca', 'composer']:
        errors.append("TRADE_SOURCE must be 'alpaca' or 'composer'")
    else:
        print(f"✅ Trade source: {trade_source}")
    
    # Check numeric settings
    numeric_settings = {
        'PERIOD': (5, 3600, 'seconds between checks'),
        'CHANGE_WAIT': (1, 300, 'seconds to wait after changes'),
        'RETRY': (1, 10, 'number of retry attempts'),
        'TRADE_WITH': (1, 100, 'percentage of account to trade with'),
        'PADDING': (0, 1000, 'padding amount in dollars')
    }
    
    for setting, (min_val, max_val, description) in numeric_settings.items():
        try:
            value = int(os.getenv(setting, 0))
            if min_val <= value <= max_val:
                print(f"✅ {setting}: {value} ({description})")
            else:
                errors.append(f"{setting} must be between {min_val} and {max_val}")
        except ValueError:
            errors.append(f"{setting} must be a valid number")
    
    # Check MODE
    mode = os.getenv('MODE', '').lower().strip()
    if mode not in ['debug', 'live']:
        errors.append("MODE must be 'debug' or 'live'")
    else:
        print(f"✅ Trading mode: {mode}")
    
    return len(errors) == 0, errors

def test_composer_connection() -> bool:
    """Test Composer API connection."""
    try:
        from composer_api import get_composer_percentages
        print("🔄 Testing Composer API connection...")
        
        percentages = get_composer_percentages()
        if percentages and percentages.get('assets'):
            print(f"✅ Composer API connection successful! Found {len(percentages['assets'])} assets")
            return True
        else:
            print("⚠️  Composer API connected but no assets found")
            return True
            
    except ImportError:
        print("❌ Cannot import composer_api module")
        return False
    except Exception as e:
        print(f"❌ Composer API connection failed: {e}")
        return False

def test_alpaca_connection() -> bool:
    """Test Alpaca API connection."""
    try:
        from alpaca_api import get_alpaca_percentages
        print("🔄 Testing Alpaca API connection...")
        
        percentages = get_alpaca_percentages()
        if percentages and percentages.get('assets'):
            print(f"✅ Alpaca API connection successful! Found {len(percentages['assets'])} assets")
            return True
        else:
            print("⚠️  Alpaca API connected but no assets found")
            return True
            
    except ImportError:
        print("❌ Cannot import alpaca_api module")
        return False
    except Exception as e:
        print(f"❌ Alpaca API connection failed: {e}")
        return False

def main():
    """Main validation function."""
    print("🔍 Copy Trader Configuration Validation")
    print("=" * 50)
    
    # Check environment file
    if not check_env_file():
        sys.exit(1)
    
    print("\n📋 Configuration Validation:")
    print("-" * 30)
    
    all_valid = True
    all_errors = []
    
    # Validate Composer config
    print("\n🎼 Composer Configuration:")
    valid, errors = validate_composer_config()
    if not valid:
        all_valid = False
        all_errors.extend(errors)
    
    # Validate Schwab config
    print("\n🏦 Schwab Configuration:")
    valid, errors = validate_schwab_config()
    if not valid:
        all_valid = False
        all_errors.extend(errors)
    
    # Validate Alpaca config
    print("\n🐑 Alpaca Configuration:")
    valid, errors = validate_alpaca_config()
    if not valid:
        all_valid = False
        all_errors.extend(errors)
    
    # Validate trade settings
    print("\n⚙️  Trade Settings:")
    valid, errors = validate_trade_settings()
    if not valid:
        all_valid = False
        all_errors.extend(errors)
    
    # Test API connections
    print("\n🔗 API Connection Tests:")
    print("-" * 30)
    
    trade_source = os.getenv('TRADE_SOURCE', '').lower().strip()
    
    if trade_source == 'composer':
        composer_ok = test_composer_connection()
        if not composer_ok:
            all_valid = False
    elif trade_source == 'alpaca':
        alpaca_ok = test_alpaca_connection()
        if not alpaca_ok:
            all_valid = False
    else:
        print("⚠️  Unknown trade source, skipping API tests")
    
    # Summary
    print("\n📊 Validation Summary:")
    print("=" * 30)
    
    if all_valid and not all_errors:
        print("✅ All configuration is valid!")
        print("\n🚀 You're ready to run the copy trader!")
        print("   Run: python copy_trade.py")
    else:
        print("❌ Configuration issues found:")
        for error in all_errors:
            print(f"   • {error}")
        print("\n🔧 Please fix the issues above before running the copy trader.")
        sys.exit(1)

if __name__ == "__main__":
    main()
