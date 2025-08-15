#!/usr/bin/env python3
"""
Example script showing the complete flow from Composer asset percentages to Schwab buy orders.
This demonstrates how the script converts portfolio percentages into actual buy orders.
"""

import os
from dotenv import load_dotenv
from composer_api import get_composer_percentages
from pprint import pformat

load_dotenv()

def show_conversion_example():
    """Show the complete conversion from percentages to buy orders."""
    
    print("🔄 **Complete Flow: Composer Percentages → Schwab Buy Orders**")
    print("=" * 70)
    
    # Step 1: Get Composer percentages
    print("\n📊 **Step 1: Get Composer Portfolio Percentages**")
    print("-" * 50)
    
    try:
        percentages_data = get_composer_percentages()
        
        print("✅ Composer API Response:")
        print(f"   Portfolio Total: ${percentages_data.get('portfolio_total', 0):,.2f}")
        print(f"   Number of Assets: {len(percentages_data.get('assets', {}))}")
        
        # Show sample percentages
        sample_percentages = dict(list(percentages_data.get('percentages', {}).items())[:5])
        print(f"\n📈 Sample Asset Percentages:")
        for symbol, pct in sample_percentages.items():
            asset_data = percentages_data['assets'].get(symbol, {})
            market_value = asset_data.get('market_value', 0)
            print(f"   {symbol}: {pct}% (${market_value:,.2f})")
        
        if len(percentages_data.get('percentages', {})) > 5:
            print(f"   ... and {len(percentages_data.get('percentages', {})) - 5} more assets")
            
    except Exception as e:
        print(f"❌ Error getting Composer percentages: {e}")
        return
    
    # Step 2: Show configuration settings
    print("\n⚙️ **Step 2: Configuration Settings**")
    print("-" * 50)
    
    trade_with = float(os.getenv('TRADE_WITH', 100))
    padding = float(os.getenv('PADDING', 10.0))
    share_round = os.getenv('SHARE_ROUND', 'down')
    mode = os.getenv('MODE', 'debug')
    
    print(f"   TRADE_WITH: {trade_with}% (percentage of account to trade with)")
    print(f"   PADDING: ${padding:,.2f} (amount to subtract for slippage)")
    print(f"   SHARE_ROUND: {share_round} (how to round share quantities)")
    print(f"   MODE: {mode} (debug/live trading mode)")
    
    # Step 3: Simulate account breakdown
    print("\n💰 **Step 3: Account Value Calculation**")
    print("-" * 50)
    
    # Simulate a Schwab account value (in real scenario, this comes from Schwab API)
    simulated_account_value = 100000  # $100k example
    trade_value = simulated_account_value * (trade_with / 100) - padding
    
    print(f"   Simulated Account Value: ${simulated_account_value:,.2f}")
    print(f"   Trade Value Calculation: ${simulated_account_value:,.2f} × {trade_with}% - ${padding:,.2f}")
    print(f"   Available for Trading: ${trade_value:,.2f}")
    
    # Step 4: Convert percentages to dollar amounts
    print("\n💵 **Step 4: Convert Percentages to Dollar Amounts**")
    print("-" * 50)
    
    dollar_amounts = {}
    for symbol, percentage in sample_percentages.items():
        dollar_amount = trade_value * (percentage / 100)
        dollar_amounts[symbol] = round(dollar_amount, 2)
        print(f"   {symbol}: {percentage}% → ${dollar_amount:,.2f}")
    
    # Step 5: Convert dollar amounts to share quantities
    print("\n📈 **Step 5: Convert Dollar Amounts to Share Quantities**")
    print("-" * 50)
    
    # Simulate current stock prices (in real scenario, these come from Schwab quotes API)
    simulated_prices = {
        'TQQQ': 93.05,
        'UPRO': 101.62,
        'NAIL': 3.66,
        'EEV': 4.42,
        'EUM': 4.97
    }
    
    share_quantities = {}
    for symbol, dollar_amount in dollar_amounts.items():
        if symbol in simulated_prices:
            price = simulated_prices[symbol]
            if share_round == 'down':
                shares = int(dollar_amount / price)  # Floor division
            else:  # nearest
                shares = round(dollar_amount / price)
            
            share_quantities[symbol] = shares
            actual_cost = shares * price
            print(f"   {symbol}: ${dollar_amount:,.2f} ÷ ${price:.2f} = {shares} shares (${actual_cost:,.2f})")
    
    # Step 6: Show final buy orders
    print("\n🛒 **Step 6: Final Buy Orders**")
    print("-" * 50)
    
    print("📋 Orders that would be placed:")
    for symbol, shares in share_quantities.items():
        if shares > 0:
            print(f"   BUY {shares} shares of {symbol} @ MARKET")
        else:
            print(f"   SKIP {symbol} (0 shares)")
    
    # Step 7: Show the actual code flow
    print("\n🔧 **Step 7: Code Flow in the Script**")
    print("-" * 50)
    
    print("""
    # In copy_trade.py:
    percentages = get_percentages()  # Gets Composer data
    
    # In schwab_api.py:
    breakdown = schwab_conn.breakdown_account_by_quotes(account_num, percentages["percentages"])
    # This function:
    # 1. Gets account value from Schwab
    # 2. Applies TRADE_WITH percentage and PADDING
    # 3. Converts percentages to dollar amounts
    # 4. Gets current quotes for each ticker
    # 5. Converts dollar amounts to share quantities
    
    schwab_conn.buy_tickers_for_the_day(account_num, breakdown)
    # This function:
    # 1. Compares new holdings vs current holdings
    # 2. Sells positions that need to be reduced
    # 3. Buys positions that need to be increased
    # 4. Places actual market orders
    """)
    
    # Summary
    print("\n📊 **Summary**")
    print("-" * 50)
    print(f"   • Composer portfolio has {len(percentages_data.get('percentages', {}))} assets")
    print(f"   • Total portfolio value: ${percentages_data.get('portfolio_total', 0):,.2f}")
    print(f"   • Available for trading: ${trade_value:,.2f}")
    print(f"   • Would place {sum(1 for shares in share_quantities.values() if shares > 0)} buy orders")
    print(f"   • Mode: {mode.upper()} (orders {'would be' if mode == 'live' else 'would NOT be'} placed)")

if __name__ == "__main__":
    show_conversion_example()
