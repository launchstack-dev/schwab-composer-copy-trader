#!/usr/bin/env python3
"""
Script to save current Composer data to files immediately.
"""

import os
import datetime
import pytz
import json
from dotenv import load_dotenv
from composer_api import get_composer_percentages

load_dotenv()

def save_current_data():
    """Save current Composer data to files."""
    
    eastern = pytz.timezone('US/Eastern')
    timestamp = datetime.datetime.now(eastern).strftime('%Y-%m-%d_%H-%M-%S_%Z')
    
    print(f"💾 **Saving Current Data at {timestamp}**")
    print("=" * 50)
    
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
            'TMO': 485.60, 'DHR': 245.80, 'BDX': 225.40, 'ABT': 105.60
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
        
        # Prepare data for recording
        recorded_data = {
            'timestamp': timestamp,
            'portfolio_total': percentages_data.get('portfolio_total', 0),
            'num_assets': len(percentages_data.get('percentages', {})),
            'configuration': {
                'trade_with': trade_with,
                'padding': padding,
                'share_round': share_round,
                'mode': mode,
                'simulated_account_value': simulated_account_value,
                'trade_value': trade_value
            },
            'percentages': percentages_data.get('percentages', {}),
            'dollar_amounts': dollar_amounts,
            'share_quantities': share_quantities,
            'assets_data': percentages_data.get('assets', {})
        }
        
        # Save to timestamped file
        filename = f"conversion_record_{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump(recorded_data, f, indent=2)
        
        # Also append to cumulative file
        cumulative_filename = "conversion_history.json"
        cumulative_data = []
        
        # Load existing data if file exists
        if os.path.exists(cumulative_filename):
            try:
                with open(cumulative_filename, 'r') as f:
                    cumulative_data = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                cumulative_data = []
        
        # Add new data
        cumulative_data.append(recorded_data)
        
        # Save cumulative data
        with open(cumulative_filename, 'w') as f:
            json.dump(cumulative_data, f, indent=2)
        
        # Save human-readable summary
        summary_filename = f"conversion_summary_{timestamp}.txt"
        with open(summary_filename, 'w') as f:
            f.write(f"Composer to Schwab Conversion Record\n")
            f.write(f"Timestamp: {timestamp}\n")
            f.write(f"=" * 50 + "\n\n")
            
            f.write(f"Portfolio Total: ${percentages_data.get('portfolio_total', 0):,.2f}\n")
            f.write(f"Number of Assets: {len(percentages_data.get('percentages', {}))}\n")
            f.write(f"Trade Value: ${trade_value:,.2f}\n")
            f.write(f"Mode: {mode.upper()}\n\n")
            
            f.write("Complete Asset Breakdown:\n")
            f.write("-" * 50 + "\n")
            f.write(f"{'Symbol':<8} {'Pct':<6} {'Dollar Amt':<12} {'Shares':<8} {'Price':<8} {'Actual Cost':<12}\n")
            f.write("-" * 50 + "\n")
            
            sorted_percentages = sorted(
                percentages_data.get('percentages', {}).items(), 
                key=lambda x: x[1], 
                reverse=True
            )
            
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
                
                f.write(f"{symbol:<8} {pct:6.2f}% ${dollar_amt:10,.2f} {shares:6} ${price:8.2f} ${actual_cost:10,.2f}\n")
            
            f.write("-" * 50 + "\n")
            f.write(f"{'TOTAL':<8} {'100%':<6} ${trade_value:10,.2f} {total_shares:6} {'':<8} ${total_actual_cost:10,.2f}\n")
        
        # Print summary
        print(f"✅ **Data Saved Successfully!**")
        print(f"   📄 Individual file: {filename}")
        print(f"   📚 Cumulative file: {cumulative_filename}")
        print(f"   📝 Summary file: {summary_filename}")
        
        print(f"\n📊 **Current Portfolio Summary**")
        print("-" * 50)
        print(f"   Portfolio Total: ${percentages_data.get('portfolio_total', 0):,.2f}")
        print(f"   Number of Assets: {len(percentages_data.get('percentages', {}))}")
        print(f"   Trade Value: ${trade_value:,.2f}")
        print(f"   Mode: {mode.upper()}")
        
        return recorded_data
        
    except Exception as e:
        error_msg = f"Error saving data: {e}"
        print(f"❌ {error_msg}")
        
        # Save error to file
        error_filename = f"conversion_error_{timestamp}.txt"
        with open(error_filename, 'w') as f:
            f.write(f"Error at {timestamp}: {e}\n")
        
        return None

if __name__ == "__main__":
    save_current_data()
