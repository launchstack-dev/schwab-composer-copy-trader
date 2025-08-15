#!/usr/bin/env python3
"""
Script to run the conversion example at 3:55 PM Eastern time and record the results.
"""

import os
import time
import datetime
import pytz
from dotenv import load_dotenv
from composer_api import get_composer_percentages
from pprint import pformat
import json

load_dotenv()

def wait_until_355pm_eastern():
    """Wait until 3:55 PM Eastern time."""
    eastern = pytz.timezone('US/Eastern')
    
    while True:
        now = datetime.datetime.now(eastern)
        target_time = now.replace(hour=15, minute=55, second=0, microsecond=0)
        
        if now >= target_time:
            # If it's already past 3:55 PM, wait until tomorrow
            target_time += datetime.timedelta(days=1)
        
        time_until_target = (target_time - now).total_seconds()
        
        print(f"⏰ Waiting until 3:55 PM Eastern time...")
        print(f"   Current time (Eastern): {now.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print(f"   Target time: {target_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print(f"   Time remaining: {time_until_target/3600:.1f} hours")
        
        if time_until_target > 3600:  # More than 1 hour
            time.sleep(3600)  # Sleep for 1 hour
        elif time_until_target > 60:  # More than 1 minute
            time.sleep(60)  # Sleep for 1 minute
        else:
            time.sleep(1)  # Sleep for 1 second

def record_conversion_data():
    """Record the conversion data at 3:55 PM Eastern."""
    
    eastern = pytz.timezone('US/Eastern')
    timestamp = datetime.datetime.now(eastern).strftime('%Y-%m-%d_%H-%M-%S_%Z')
    
    print(f"\n🕐 **Executing at {timestamp}**")
    print("=" * 70)
    
    # Get Composer percentages
    try:
        percentages_data = get_composer_percentages()
        
        # Configuration settings
        trade_with = float(os.getenv('TRADE_WITH', 100))
        padding = float(os.getenv('PADDING', 10.0))
        share_round = os.getenv('SHARE_ROUND', 'down')
        mode = os.getenv('MODE', 'debug')
        
        # Simulate account value (in real scenario, this comes from Schwab API)
        simulated_account_value = 100000  # $100k example
        trade_value = simulated_account_value * (trade_with / 100) - padding
        
        # Convert percentages to dollar amounts
        dollar_amounts = {}
        for symbol, percentage in percentages_data.get('percentages', {}).items():
            dollar_amount = trade_value * (percentage / 100)
            dollar_amounts[symbol] = round(dollar_amount, 2)
        
        # Simulate current stock prices (in real scenario, these come from Schwab quotes API)
        # Using some common ETF prices as examples
        simulated_prices = {
            'TQQQ': 93.05, 'UPRO': 101.62, 'NAIL': 3.66, 'EEV': 4.42, 'EUM': 4.97,
            'SPY': 520.15, 'QQQ': 450.25, 'IWM': 200.50, 'TLT': 95.30, 'GLD': 215.80,
            'VTI': 265.40, 'VOO': 485.20, 'VEA': 45.60, 'VWO': 42.30, 'BND': 72.15
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
        
        # Save to file with timestamp
        filename = f"conversion_record_{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump(recorded_data, f, indent=2)
        
        # Also append to a cumulative file
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
        
        # Print summary
        print(f"\n📊 **Recorded Data Summary**")
        print("-" * 50)
        print(f"   Portfolio Total: ${percentages_data.get('portfolio_total', 0):,.2f}")
        print(f"   Number of Assets: {len(percentages_data.get('percentages', {}))}")
        print(f"   Trade Value: ${trade_value:,.2f}")
        print(f"   Mode: {mode.upper()}")
        
        print(f"\n📈 **All Assets by Percentage**")
        print("-" * 50)
        sorted_percentages = sorted(
            percentages_data.get('percentages', {}).items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        print(f"{'Symbol':<8} {'Pct':<6} {'Dollar Amt':<12} {'Shares':<8} {'Price':<8} {'Actual Cost':<12}")
        print("-" * 70)
        for symbol, pct in sorted_percentages:
            dollar_amt = dollar_amounts.get(symbol, 0)
            share_info = share_quantities.get(symbol, {})
            shares = share_info.get('shares', 0)
            price = share_info.get('price', 0)
            actual_cost = share_info.get('actual_cost', 0)
            
            print(f"{symbol:<8} {pct:6.2f}% ${dollar_amt:10,.2f} {shares:6} ${price:8.2f} ${actual_cost:10,.2f}")
        
        print(f"\n💾 **Data saved to: {filename}**")
        
        # Also save a human-readable summary
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
            for symbol, pct in sorted_percentages:
                dollar_amt = dollar_amounts.get(symbol, 0)
                share_info = share_quantities.get(symbol, {})
                shares = share_info.get('shares', 0)
                price = share_info.get('price', 0)
                actual_cost = share_info.get('actual_cost', 0)
                
                f.write(f"{symbol:<8} {pct:6.2f}% ${dollar_amt:10,.2f} {shares:6} ${price:8.2f} ${actual_cost:10,.2f}\n")
        
        print(f"📝 **Summary saved to: {summary_filename}**")
        print(f"📚 **Cumulative history saved to: {cumulative_filename}**")
        
        # Show comparison with previous data if available
        if len(cumulative_data) > 1:
            print(f"\n📊 **Comparison with Previous Record**")
            print("-" * 50)
            previous_data = cumulative_data[-2]  # Second to last entry
            current_total = percentages_data.get('portfolio_total', 0)
            previous_total = previous_data.get('portfolio_total', 0)
            change = current_total - previous_total
            change_pct = (change / previous_total * 100) if previous_total > 0 else 0
            
            print(f"   Portfolio Total Change: ${change:+,.2f} ({change_pct:+.2f}%)")
            print(f"   Previous: ${previous_total:,.2f}")
            print(f"   Current:  ${current_total:,.2f}")
            
            # Show top 5 changes in percentages
            current_pcts = percentages_data.get('percentages', {})
            previous_pcts = previous_data.get('percentages', {})
            
            changes = []
            for symbol in set(current_pcts.keys()) | set(previous_pcts.keys()):
                current_pct = current_pcts.get(symbol, 0)
                previous_pct = previous_pcts.get(symbol, 0)
                change_pct = current_pct - previous_pct
                if abs(change_pct) > 0.01:  # Only show significant changes
                    changes.append((symbol, change_pct, current_pct, previous_pct))
            
            if changes:
                changes.sort(key=lambda x: abs(x[1]), reverse=True)
                print(f"\n   Top 5 Percentage Changes:")
                for symbol, change_pct, current_pct, previous_pct in changes[:5]:
                    print(f"     {symbol}: {previous_pct:.2f}% → {current_pct:.2f}% ({change_pct:+.2f}%)")
        
        return recorded_data
        
    except Exception as e:
        error_msg = f"Error recording conversion data: {e}"
        print(f"❌ {error_msg}")
        
        # Save error to file
        error_filename = f"conversion_error_{timestamp}.txt"
        with open(error_filename, 'w') as f:
            f.write(f"Error at {timestamp}: {e}\n")
        
        return None

def main():
    """Main function to wait and record data."""
    print("🚀 **Composer to Schwab Conversion Recorder**")
    print("=" * 50)
    print("This script will wait until 3:55 PM Eastern time")
    print("and then record the current conversion data.")
    print("=" * 50)
    
    # Wait until 3:55 PM Eastern
    wait_until_355pm_eastern()
    
    # Record the data
    recorded_data = record_conversion_data()
    
    if recorded_data:
        print(f"\n✅ **Recording completed successfully!**")
    else:
        print(f"\n❌ **Recording failed!**")

if __name__ == "__main__":
    main()
