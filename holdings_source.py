from __future__ import annotations

from composer_api import get_composer_percentages
from alpaca_api import get_alpaca_percentages 
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

    Selection is controlled by HOLDINGS_SOURCE:
      - 'alpaca'
      - 'composer' (uses COMPOSER_ACCOUNT_ID)
    """
    src = (os.getenv("TRADE_SOURCE", "None Found")).lower().strip()
    if src == "alpaca":
        return get_alpaca_percentages()
    elif src == "composer":
        return get_composer_percentages()
    # elif src == "composer_symphony":
    #     sid = os.getenv("COMPOSER_SYMPHONY_ID", "").strip()
    #     if not sid:
    #         raise RuntimeError("COMPOSER_SYMPHONY_ID is required when HOLDINGS_SOURCE=composer_symphony")
    #     pct = get_symphony_percentages(sid)
    #     return {"percentages": pct.percentages, "assets": pct.assets, "portfolio_total": pct.portfolio_total}
    else:
        raise RuntimeError(f"Unknown TRADE_SOURCE: {src}")

def check_for_change() -> bool:
    """Compare current normalized holdings vs. last saved snapshot; return True if changed."""
    cur_positions = get_percentages()
    
    if not os.path.exists(SAVED_POS_FILE):
        with open(SAVED_POS_FILE, 'w') as file:
            yaml.dump(cur_positions, file, default_flow_style=False)
        return True
    else:
        with open(SAVED_POS_FILE, 'r') as file:
            saved_pos = yaml.safe_load(file)
        
        for asset, qty in cur_positions["assets"].items():
            if asset not in saved_pos["assets"]:
                logger.info(f"\n===\n!!! Changes Detected !!!\nOld Holdings: \n{pformat(saved_pos)}\nNew Holdings: \n{pformat(cur_positions)}\n===")
                return True
            if qty["qty"] != saved_pos["assets"][asset]["qty"]:
                logger.info(f"\n===\n!!! Changes Detected !!!\nOld Holdings: \n{pformat(saved_pos)}\nNew Holdings: \n{pformat(cur_positions)}\n===")
                return True
        
    return False

def save_changes(cur_positions) -> None:
    """Persist current snapshot."""
    with open(SAVED_POS_FILE, 'w') as f:
        yaml.dump(cur_positions, f, default_flow_style=False)

if __name__ == '__main__':
    pass