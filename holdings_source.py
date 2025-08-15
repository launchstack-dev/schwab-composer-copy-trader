from __future__ import annotations

from composer_api import get_composer_percentages, ComposerAPIError
from logger_config import setup_logger
from dotenv import load_dotenv
from typing import Dict, Any
from pprint import pformat
import yaml
import os

load_dotenv()
logger = setup_logger('trade_source', 'logs/trade_source.log')
SAVED_POS_FILE = "./saved_pos.yaml"

def get_percentages() -> Dict[str, Any]:
    """Return the normalized structure {percentages, assets, portfolio_total} for the selected source.

    Selection is controlled by TRADE_SOURCE:
      - 'alpaca'
      - 'composer' (uses COMPOSER_ACCOUNT_NUM)
    """
    src = (os.getenv("TRADE_SOURCE", "None Found")).lower().strip()
    
    try:
        if src == "alpaca":
            # Only import alpaca_api when needed
            from alpaca_api import get_alpaca_percentages
            return get_alpaca_percentages()
        elif src == "composer":
            return get_composer_percentages()
        # elif src == "composer_symphony":
        #     sid = os.getenv("COMPOSER_SYMPHONY_ID", "").strip()
        #     if not sid:
        #         raise RuntimeError("COMPOSER_SYMPHONY_ID is required when TRADE_SOURCE=composer_symphony")
        #     pct = get_symphony_percentages(sid)
        #     return {"percentages": pct.percentages, "assets": pct.assets, "portfolio_total": pct.portfolio_total}
        else:
            raise RuntimeError(f"Unknown TRADE_SOURCE: {src}")
    except ComposerAPIError as e:
        logger.error(f"Composer API error: {e}")
        raise
    except Exception as e:
        logger.error(f"Error getting percentages from {src}: {e}")
        raise

def check_for_change() -> bool:
    """Compare current normalized holdings vs. last saved snapshot; return True if changed."""
    try:
        cur_positions = get_percentages()
        
        if not os.path.exists(SAVED_POS_FILE):
            with open(SAVED_POS_FILE, 'w') as file:
                yaml.dump(cur_positions, file, default_flow_style=False)
            logger.info("No saved positions file found, creating initial snapshot")
            return True
        else:
            with open(SAVED_POS_FILE, 'r') as file:
                saved_pos = yaml.safe_load(file)
            
            if not saved_pos or not isinstance(saved_pos, dict):
                logger.warning("Invalid saved positions file, recreating")
                with open(SAVED_POS_FILE, 'w') as file:
                    yaml.dump(cur_positions, file, default_flow_style=False)
                return True
            
            # Check for new assets
            for asset in cur_positions.get("assets", {}):
                if asset not in saved_pos.get("assets", {}):
                    logger.info(f"\n===\n!!! Changes Detected !!!\nNew asset found: {asset}\nOld Holdings: \n{pformat(saved_pos)}\nNew Holdings: \n{pformat(cur_positions)}\n===")
                    return True
            
            # Check for quantity changes
            for asset, qty in cur_positions.get("assets", {}).items():
                if asset not in saved_pos.get("assets", {}):
                    continue
                if qty["qty"] != saved_pos["assets"][asset]["qty"]:
                    logger.info(f"\n===\n!!! Changes Detected !!!\nQuantity change for {asset}: {saved_pos['assets'][asset]['qty']} -> {qty['qty']}\nOld Holdings: \n{pformat(saved_pos)}\nNew Holdings: \n{pformat(cur_positions)}\n===")
                    return True
            
            # Check for removed assets
            for asset in saved_pos.get("assets", {}):
                if asset not in cur_positions.get("assets", {}):
                    logger.info(f"\n===\n!!! Changes Detected !!!\nAsset removed: {asset}\nOld Holdings: \n{pformat(saved_pos)}\nNew Holdings: \n{pformat(cur_positions)}\n===")
                    return True
        
        return False
        
    except Exception as e:
        logger.error(f"Error checking for changes: {e}")
        # If we can't check for changes, assume there are changes to be safe
        return True

def save_changes(cur_positions: Dict[str, Any]) -> None:
    """Persist current snapshot."""
    try:
        # Create backup of existing file
        if os.path.exists(SAVED_POS_FILE):
            backup_file = f"{SAVED_POS_FILE}.backup"
            with open(SAVED_POS_FILE, 'r') as src, open(backup_file, 'w') as dst:
                dst.write(src.read())
        
        with open(SAVED_POS_FILE, 'w') as f:
            yaml.dump(cur_positions, f, default_flow_style=False)
        
        logger.info(f"Successfully saved position snapshot with {len(cur_positions.get('assets', {}))} assets")
        
    except Exception as e:
        logger.error(f"Error saving changes: {e}")
        raise

if __name__ == '__main__':
    # Test the holdings source
    try:
        print("Testing holdings source...")
        percentages = get_percentages()
        print(f"Successfully retrieved {len(percentages.get('assets', {}))} assets")
        print(f"Portfolio total: ${percentages.get('portfolio_total', 0):,.2f}")
        
        has_changes = check_for_change()
        print(f"Changes detected: {has_changes}")
        
    except Exception as e:
        print(f"Test failed: {e}")