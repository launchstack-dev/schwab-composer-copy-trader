# Asset Percentages to Buy Orders Conversion

This document shows the key code sections that convert Composer asset percentages into Schwab buy orders.

## 1. Getting Composer Percentages

**File: `composer_api.py`**

```python
def get_composer_percentages() -> Dict[str, Any]:
    """Get portfolio percentages from Composer account."""
    accounts = list_accounts()
    account_uuid = find_account_uuid(accounts)
    percentages = get_account_data(account_uuid)
    return percentages

# Returns structure like:
{
    "percentages": {
        "TQQQ": 32.03,
        "UPRO": 0.86,
        "NAIL": 1.10,
        # ... more assets
    },
    "assets": {
        "TQQQ": {
            "current_price": 93.05,
            "market_value": 5610.53,
            "qty": 60.29,
            "rounded_qty": 60.29
        },
        # ... more assets
    },
    "portfolio_total": 332992.33
}
```

## 2. Converting Percentages to Dollar Amounts

**File: `schwab_api.py` - `breakdown_account_by_quotes()`**

```python
def breakdown_account_by_quotes(self, account_num: int, percentages: dict) -> dict:
    """Convert percentages to dollar amounts and then to share quantities."""
    
    # Step 1: Get account trade value
    total = self.get_account_trade_value(account_num)
    # total = account_value * (TRADE_WITH/100) - PADDING
    
    # Step 2: Convert percentages to dollar amounts
    for stock in percentages:
        percentages[stock] = round(total * percentages[stock]/100, 2)
    
    # Step 3: Get current quotes for each ticker
    ticker_data = self.get_quotes(ticker_quotes)
    
    # Step 4: Convert dollar amounts to share quantities
    buy_amounts = {}
    for stock in percentages:
        if stock == "checksum":
            continue
        quotes[stock] = ticker_data[stock]["quote"]["mark"]
        
        # Apply rounding based on SHARE_ROUND setting
        if SHARE_ROUND is ShareRounding.NEAREST:
            buy_amounts[stock] = round(percentages[stock]/quotes[stock])
        elif SHARE_ROUND is ShareRounding.DOWN:
            buy_amounts[stock] = math.floor(percentages[stock]/quotes[stock])
    
    return buy_amounts
```

## 3. Account Value Calculation

**File: `schwab_api.py` - `get_account_trade_value()`**

```python
def get_account_trade_value(self, account_num: int):
    """Calculate how much of the account to trade with."""
    account_total = self.get_account_holding_value(account_num)
    
    # Apply TRADE_WITH percentage and PADDING
    trade_value = account_total * (TRADE_WITH/100) - PADDING
    
    return round(trade_value, 2)
```

## 4. Executing Buy Orders

**File: `schwab_api.py` - `buy_tickers_for_the_day()`**

```python
def buy_tickers_for_the_day(self, account_num: int, tickers: dict):
    """Execute buy orders for the day based on changes."""
    
    # Step 1: Compare new vs current holdings
    old = self.get_current_holdings(account_num)
    new = tickers
    
    # Step 2: Calculate differences
    added_keys = {key: new[key] for key in new if key not in old}
    removed_keys = {key: old[key] for key in old if key not in new}
    changed_keys = {key: {'old': old[key], 'new': new[key]} 
                   for key in old if key in new and old[key] != new[key]}
    
    # Step 3: Execute sell orders first (if any)
    if MODE is Modes.LIVE:
        sell_orders = self.sell_tickers(account_num, removed_keys)
        # Wait for sells to complete...
        
        # Step 4: Execute buy orders
        buy_orders = self.buy_tickers(account_num, added_keys)
```

## 5. Individual Buy Order Placement

**File: `schwab_api.py` - `buy_tickers()`**

```python
def buy_tickers(self, account_num: int, tickers: dict):
    """Place individual buy orders."""
    account_hash = self.get_account_hash(account_num)
    orders = []
    
    for ticker, quantity in tickers.items():
        if quantity == 0:
            continue
        logger.info(f"!!! Buying {quantity} of {ticker} !!!")
        
        # Place market buy order
        order = equity_buy_market(symbol=ticker, quantity=quantity).build()
        order_id = self.c.place_order(account_hash, order)
        orders.append(order_id)
    
    return orders
```

## 6. Main Execution Flow

**File: `copy_trade.py`**

```python
# Main loop that orchestrates everything
if check_for_change():
    # Get current percentages from Composer
    percentages = get_percentages()
    
    for account_num in schwab_accounts:
        # Convert percentages to buy orders
        breakdown = schwab_conn.breakdown_account_by_quotes(
            account_num, 
            percentages["percentages"]
        )
        
        # Execute the trades
        schwab_conn.buy_tickers_for_the_day(account_num, breakdown)
    
    # Save changes for next comparison
    save_changes(percentages)
```

## Configuration Settings

**File: `.env`**

```bash
# Trading configuration
TRADE_WITH=100          # Percentage of account to trade with
PADDING=10.0           # Amount to subtract for slippage
SHARE_ROUND=down       # How to round share quantities (down/nearest)
MODE=debug             # debug/live trading mode
PERIOD=300             # Seconds between checks
CHANGE_WAIT=30         # Seconds to wait after detecting changes
RETRY=3                # Number of retry attempts
```

## Example Conversion

**Input (Composer percentages):**
```
TQQQ: 32.03%
UPRO: 0.86%
NAIL: 1.10%
```

**Step 1: Account Value**
```
Account Value: $100,000
Trade Value: $100,000 × 100% - $10 = $99,990
```

**Step 2: Dollar Amounts**
```
TQQQ: $99,990 × 32.03% = $32,027.70
UPRO: $99,990 × 0.86% = $859.91
NAIL: $99,990 × 1.10% = $1,099.89
```

**Step 3: Share Quantities (with current prices)**
```
TQQQ: $32,027.70 ÷ $93.05 = 344 shares
UPRO: $859.91 ÷ $101.62 = 8 shares
NAIL: $1,099.89 ÷ $3.66 = 300 shares
```

**Step 4: Final Orders**
```
BUY 344 shares of TQQQ @ MARKET
BUY 8 shares of UPRO @ MARKET
BUY 300 shares of NAIL @ MARKET
```

This is how the script automatically converts your Composer portfolio percentages into actual Schwab buy orders!
