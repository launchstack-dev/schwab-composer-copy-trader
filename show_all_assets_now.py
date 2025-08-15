#!/usr/bin/env python3
"""
Script to show all assets in the current Composer portfolio with complete conversion data.
"""

import os
from dotenv import load_dotenv
from composer_api import get_composer_percentages
from pprint import pformat

load_dotenv()

def show_all_assets():
    """Show all assets in the current Composer portfolio."""
    
    print("📊 **Current Composer Portfolio - All Assets**")
    print("=" * 70)
    
    try:
        percentages_data = get_composer_percentages()
        
        # Configuration settings
        trade_with = float(os.getenv('TRADE_WITH', 100))
        padding = float(os.getenv('PADDING', 10.0))
        share_round = os.getenv('SHARE_ROUND', 'down')
        mode = os.getenv('MODE', 'debug')
        
        # Simulate account value
        simulated_account_value = 100000  # $100k example
        trade_value = simulated_account_value * (trade_with / 100) - padding
        
        # Convert percentages to dollar amounts
        dollar_amounts = {}
        for symbol, percentage in percentages_data.get('percentages', {}).items():
            dollar_amount = trade_value * (percentage / 100)
            dollar_amounts[symbol] = round(dollar_amount, 2)
        
        # Simulate current stock prices
        simulated_prices = {
            'TQQQ': 93.05, 'UPRO': 101.62, 'NAIL': 3.66, 'EEV': 4.42, 'EUM': 4.97,
            'SPY': 520.15, 'QQQ': 450.25, 'IWM': 200.50, 'TLT': 95.30, 'GLD': 215.80,
            'VTI': 265.40, 'VOO': 485.20, 'VEA': 45.60, 'VWO': 42.30, 'BND': 72.15,
            'PGR': 185.50, 'JPM': 195.80, 'MSFT': 420.30, 'AAPL': 175.20, 'GOOGL': 145.60,
            'AMZN': 180.40, 'NVDA': 850.20, 'TSLA': 245.80, 'META': 480.50, 'NFLX': 650.30,
            'CRM': 280.40, 'ADBE': 520.60, 'PYPL': 65.80, 'INTC': 35.40, 'AMD': 120.70,
            'ORCL': 125.30, 'CSCO': 48.90, 'IBM': 165.20, 'GE': 85.60, 'BA': 185.40,
            'CAT': 345.80, 'MMM': 95.20, 'KO': 60.40, 'PEP': 175.60, 'WMT': 65.80,
            'HD': 380.50, 'LOW': 225.30, 'COST': 850.20, 'TGT': 145.60, 'CVS': 75.40,
            'WBA': 25.80, 'JNJ': 165.40, 'PFE': 28.90, 'MRK': 125.60, 'ABBV': 145.80,
            'UNH': 520.40, 'ANTM': 485.20, 'CI': 325.60, 'HUM': 485.80, 'DVA': 95.40,
            'AET': 185.60, 'CNC': 75.20, 'MOH': 345.80, 'WCG': 265.40, 'HCA': 285.60,
            'THC': 125.80, 'UHS': 145.20, 'LPNT': 85.60, 'DGX': 125.40, 'LH': 225.80,
            'TMO': 485.60, 'DHR': 245.80, 'BDX': 225.40, 'ABT': 105.60, 'JNJ': 165.40,
            'PFE': 28.90, 'MRK': 125.60, 'ABBV': 145.80, 'UNH': 520.40, 'ANTM': 485.20,
            'CI': 325.60, 'HUM': 485.80, 'DVA': 95.40, 'AET': 185.60, 'CNC': 75.20,
            'MOH': 345.80, 'WCG': 265.40, 'HCA': 285.60, 'THC': 125.80, 'UHS': 145.20,
            'LPNT': 85.60, 'DGX': 125.40, 'LH': 225.80, 'TMO': 485.60, 'DHR': 245.80,
            'BDX': 225.40, 'ABT': 105.60
        }
        
        # Convert dollar amounts to share quantities
        share_quantities = {}
        for symbol, dollar_amount in dollar_amounts.items():
            if symbol in simulated_prices:
                price = simulated_prices[symbol]
                if share_round == 'down':
                    shares = int(dollar_amount / price)  # Floor division
                else:  # nearest
                    shares = round(dollar_amount / price)
                
                share_quantities[symbol] = {
                    'shares': shares,
                    'price': price,
                    'actual_cost': shares * price
                }
        
        # Print summary
        print(f"📊 **Portfolio Summary**")
        print("-" * 50)
        print(f"   Portfolio Total: ${percentages_data.get('portfolio_total', 0):,.2f}")
        print(f"   Number of Assets: {len(percentages_data.get('percentages', {}))}")
        print(f"   Trade Value: ${trade_value:,.2f}")
        print(f"   Mode: {mode.upper()}")
        
        # Sort assets by percentage
        sorted_percentages = sorted(
            percentages_data.get('percentages', {}).items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        print(f"\n📈 **All Assets by Percentage**")
        print("-" * 70)
        print(f"{'Symbol':<8} {'Pct':<6} {'Dollar Amt':<12} {'Shares':<8} {'Price':<8} {'Actual Cost':<12}")
        print("-" * 70)
        
        total_shares = 0
        total_actual_cost = 0
        
        for symbol, pct in sorted_percentages:
            dollar_amt = dollar_amounts.get(symbol, 0)
            share_info = share_quantities.get(symbol, {})
            shares = share_info.get('shares', 0)
            price = share_info.get('price', 0)
            actual_cost = share_info.get('actual_cost', 0)
            
            total_shares += shares
            total_actual_cost += actual_cost
            
            print(f"{symbol:<8} {pct:6.2f}% ${dollar_amt:10,.2f} {shares:6} ${price:8.2f} ${actual_cost:10,.2f}")
        
        print("-" * 70)
        print(f"{'TOTAL':<8} {'100%':<6} ${trade_value:10,.2f} {total_shares:6} {'':<8} ${total_actual_cost:10,.2f}")
        
        print(f"\n📋 **Buy Orders Summary**")
        print("-" * 50)
        print(f"   Total Assets: {len(sorted_percentages)}")
        print(f"   Assets with Shares > 0: {sum(1 for info in share_quantities.values() if info.get('shares', 0) > 0)}")
        print(f"   Total Shares to Buy: {total_shares}")
        print(f"   Total Cost: ${total_actual_cost:,.2f}")
        print(f"   Unused Funds: ${trade_value - total_actual_cost:,.2f}")
        
        # Show top 10 by dollar amount
        print(f"\n💰 **Top 10 by Dollar Amount**")
        print("-" * 50)
        sorted_by_dollar = sorted(dollar_amounts.items(), key=lambda x: x[1], reverse=True)[:10]
        for symbol, dollar_amt in sorted_by_dollar:
            pct = percentages_data.get('percentages', {}).get(symbol, 0)
            share_info = share_quantities.get(symbol, {})
            shares = share_info.get('shares', 0)
            print(f"   {symbol}: {pct:.2f}% → ${dollar_amt:,.2f} → {shares} shares")
        
    except Exception as e:
        print(f"❌ Error getting Composer data: {e}")

if __name__ == "__main__":
    show_all_assets()
