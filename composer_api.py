from __future__ import annotations

from typing import Dict, Any, Optional, List
from logger_config import setup_logger
from dotenv import load_dotenv
import httpx
import os
import time

load_dotenv()
logger = setup_logger('composer_api', 'logs/composer.log')

# --- Config (override via .env as needed) ---
COMPOSER_API_BASE    = "https://api.composer.trade"  # Updated to production API
COMPOSER_API_KEY     = os.getenv("COMPOSER_API_KEY", "").strip()
COMPOSER_API_SECRET  = os.getenv("COMPOSER_API_SECRET", "").strip()
COMPOSER_ACCOUNT_NUM = os.getenv("COMPOSER_ACCOUNT_NUM", "").strip()

# Updated Endpoints based on current Composer API
ACCOUNTS_PATH              = "/api/v0.1/accounts/list"                       
ACCOUNT_HOLDINGS_PATH_TMPL = "/api/v0.1/portfolio/accounts/{account_uuid}/holding-stats" 
SYMPHONY_PATH_TMPL         = "/api/v0.1/symphonies/{symphony_id}"
ACCOUNT_STATS_PATH_TMPL    = "/api/v0.1/accounts/{account_uuid}/stats"

class ComposerAPIError(Exception):
    """Custom exception for Composer API errors"""
    pass

def _get(path: str, params: Optional[Dict[str, Any]] = None, retries: int = 3) -> Any:
    """HTTP GET helper with Composer auth and retry logic."""
    url = f"{COMPOSER_API_BASE}{path}"
    headers = {
        "x-origin": 'public-api',
        "x-api-key-id": COMPOSER_API_KEY,
        "Authorization": f"Bearer {COMPOSER_API_SECRET}",
        "accept": "application/json",
    }
    
    for attempt in range(retries):
        try:
            with httpx.Client(timeout=30.0) as client:
                resp = client.get(url, headers=headers, params=params)
                
                if resp.status_code == 429:  # Rate limit
                    wait_time = int(resp.headers.get('Retry-After', 60))
                    logger.warning(f"Rate limited, waiting {wait_time} seconds")
                    time.sleep(wait_time)
                    continue
                    
                if resp.status_code >= 400:
                    error_msg = f"Composer GET {path} failed: {resp.status_code}"
                    try:
                        error_data = resp.json()
                        error_msg += f" - {error_data.get('message', resp.text)}"
                    except:
                        error_msg += f" - {resp.text}"
                    raise ComposerAPIError(error_msg)
                    
                return resp.json()
                
        except httpx.TimeoutException:
            if attempt == retries - 1:
                raise ComposerAPIError(f"Timeout after {retries} attempts for {path}")
            logger.warning(f"Timeout on attempt {attempt + 1}, retrying...")
            time.sleep(2 ** attempt)  # Exponential backoff
        except httpx.RequestError as e:
            if attempt == retries - 1:
                raise ComposerAPIError(f"Request failed after {retries} attempts: {e}")
            logger.warning(f"Request error on attempt {attempt + 1}, retrying...")
            time.sleep(2 ** attempt)

def list_accounts() -> Dict[str, Any]:
    """List Composer brokerage accounts for the API user."""
    try:
        response = _get(ACCOUNTS_PATH)
        logger.info(f"Successfully retrieved {len(response.get('accounts', []))} accounts")
        return response
    except Exception as e:
        logger.error(f"Failed to list accounts: {e}")
        raise

def _normalize_positions_to_percentages(holdings_data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert Composer holdings data to normalized percentage format."""
    percentages = {"assets": {}, "percentages": {}, "portfolio_total": 0.0}
    
    # Handle different possible data structures
    holdings = holdings_data.get("holdings", [])
    if not holdings and isinstance(holdings_data, list):
        holdings = holdings_data
    
    if not isinstance(holdings, list):
        logger.error(f"Unexpected holdings data structure: {type(holdings)}")
        return percentages
    
    total_value = 0.0
    
    for holding in holdings:
        try:
            # Extract basic holding info
            symbol = holding.get("symbol")
            asset_class = holding.get("asset_class", "").lower()
            price = holding.get("price", 0)
            
            # Skip cash and non-equities
            if symbol == "$USD" or asset_class != "equities":
                continue
            
            # Get symphony data
            symphony_data = holding.get("symphony", {})
            if not symphony_data:
                continue
            
            # Extract allocation and value from symphony
            allocation = symphony_data.get("allocation", 0)
            value = symphony_data.get("value", 0)
            amount = symphony_data.get("amount", 0)
            
            # Skip if no allocation or value
            if allocation <= 0 or value <= 0:
                continue
            
            # Calculate percentage (allocation is already a decimal, convert to percentage)
            percentage = allocation * 100
            total_value += value
            
            # Store asset data
            percentages["assets"][symbol] = {
                'current_price': price,
                'market_value': value,
                'qty': amount,
                'rounded_qty': round(amount, 2)
            }
            
            percentages["percentages"][symbol] = round(percentage, 2)
            
        except Exception as e:
            logger.warning(f"Error processing holding {holding.get('symbol', 'unknown')}: {e}")
            continue
    
    # Set portfolio total
    if total_value > 0:
        percentages["portfolio_total"] = total_value
    
    logger.info(f"Processed {len(percentages['assets'])} assets with total value: ${total_value:,.2f}")
    return percentages

def get_account_data(account_uuid: str) -> Dict[str, Any]:
    """Pull holdings for a Composer brokerage account and convert to % of portfolio."""
    try:
        path = ACCOUNT_HOLDINGS_PATH_TMPL.format(account_uuid=account_uuid)
        data = _get(path)
        
        if not data:
            raise ComposerAPIError("No data returned from holdings endpoint")
        
        logger.info(f"Retrieved holdings data for account {account_uuid}")
        return _normalize_positions_to_percentages(data)
        
    except Exception as e:
        logger.error(f"Failed to get account data for {account_uuid}: {e}")
        raise

def get_symphony_percentages(symphony_id: str) -> Optional[Dict[str, Any]]:
    """Pull a single symphony definition and convert its weights to percentages."""
    try:
        path = SYMPHONY_PATH_TMPL.format(symphony_id=symphony_id)
        data = _get(path)
        
        if not data:
            return None
        
        # Extract weights from symphony definition
        weights = {}
        assets = {}
        
        def extract_weights(node, parent_weight=1.0):
            """Recursively extract weights from symphony tree"""
            if not isinstance(node, dict):
                return
            
            step = node.get("step")
            weight = node.get("weight", {})
            
            if step == "asset":
                symbol = node.get("ticker")
                if symbol and weight:
                    asset_weight = (weight.get("num", 0) / weight.get("den", 100)) * parent_weight
                    weights[symbol] = round(asset_weight * 100, 2)
                    assets[symbol] = {
                        'current_price': 0,  # Would need separate price lookup
                        'market_value': 0,
                        'qty': 0,
                        'rounded_qty': 0
                    }
            
            # Process children
            children = node.get("children", [])
            for child in children:
                extract_weights(child, parent_weight)
        
        extract_weights(data)
        
        return {
            "assets": assets,
            "percentages": weights,
            "portfolio_total": 0.0
        }
        
    except Exception as e:
        logger.error(f"Failed to get symphony percentages for {symphony_id}: {e}")
        return None

def get_composer_percentages() -> Dict[str, Any]:
    """Get portfolio percentages from Composer account."""
    try:
        accounts = list_accounts()
        logger.info(f"Found {len(accounts.get('accounts', []))} Composer accounts")
        
        if not accounts or not accounts.get("accounts"):
            raise ComposerAPIError("No accounts found")
        
        account_uuid = None
        
        # Find the account UUID for the specified account number
        for account in accounts["accounts"]:
            if account.get("account_number") == COMPOSER_ACCOUNT_NUM:
                account_uuid = account["account_uuid"]
                break
        
        if not account_uuid:
            available_accounts = [acc.get("account_number") for acc in accounts["accounts"]]
            raise ComposerAPIError(
                f"Account number {COMPOSER_ACCOUNT_NUM} not found. "
                f"Available accounts: {available_accounts}"
            )
        
        percentages = get_account_data(account_uuid)
        logger.info(f"Successfully retrieved percentages for account {account_uuid}")
        return percentages
        
    except Exception as e:
        logger.error(f"Failed to get Composer percentages: {e}")
        raise

if __name__ == "__main__":
    # Test the API connection
    try:
        percentages = get_composer_percentages()
        print("Composer API test successful!")
        print(f"Found {len(percentages.get('assets', {}))} assets")
    except Exception as e:
        print(f"Composer API test failed: {e}")