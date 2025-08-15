from holdings_source import check_for_change, get_percentages, save_changes
from composer_api import ComposerAPIError
from logger_config import setup_logger
from schwab_api import schwab_client
from dotenv import load_dotenv
import time
import os

__version__ = "2025.8.13"

logger = setup_logger('copy_trade', 'logs/copy_trade.log')

# Load environment variables from .env file
load_dotenv()

# --------------------------------------
# How often we want to check for changes
PERIOD = int(os.getenv('PERIOD', 300))  # Default to 5 minutes
# How many times we want to retry actions
RETRY = int(os.getenv('RETRY', 3))
# How long we want to wait after changes are detected
CHANGE_WAIT = int(os.getenv('CHANGE_WAIT', 30))
# --------------------------------------

def handle_api_error(error: Exception, context: str) -> None:
    """Handle API errors with appropriate logging and recovery."""
    if isinstance(error, ComposerAPIError):
        logger.error(f"Composer API error in {context}: {error}")
        # For Composer API errors, we might want to wait longer before retrying
        time.sleep(60)  # Wait 1 minute before retrying
    else:
        logger.error(f"Error in {context}: {error}")

def execute_trades_for_account(account_num: str, percentages: dict, schwab_conn) -> bool:
    """Execute trades for a single account with retry logic."""
    for attempt in range(RETRY + 1):  # +1 for initial attempt
        try:
            logger.info(f"Executing trades for account {account_num} (attempt {attempt + 1}/{RETRY + 1})")
            print(f"Buying Tickers in Account Num: {account_num}")
            
            breakdown = schwab_conn.breakdown_account_by_quotes(account_num, percentages["percentages"])
            schwab_conn.buy_tickers_for_the_day(account_num, breakdown)
            
            logger.info(f"Successfully executed trades for account {account_num}")
            return True
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Account Num: {account_num} Error (attempt {attempt + 1}): {e}")
            print(f"Account Num: {account_num} Error: {e}")
            
            # Handle specific error cases
            if "Account has to low of a balance" in error_msg:
                logger.warning(f"Account {account_num} has insufficient balance, skipping")
                return False
            
            if "Invalid Token" in error_msg:
                logger.error("Invalid Schwab token detected")
                raise  # Re-raise to trigger token validation loop
            
            # If this was the last attempt, return False
            if attempt == RETRY:
                logger.error(f"Failed to execute trades for account {account_num} after {RETRY + 1} attempts")
                return False
            
            # Wait before retrying
            wait_time = PERIOD * (attempt + 1)  # Progressive backoff
            logger.info(f"Waiting {wait_time} seconds before retry")
            time.sleep(wait_time)
    
    return False

# How we run the copy trade method
if __name__ == '__main__':
    print(f"Version: {__version__}")
    print(f"Mode: {os.getenv('MODE', 'debug').lower()}")
    print(f"Trade Source: {os.getenv('TRADE_SOURCE', 'unknown')}")
    
    schwab_conn = schwab_client()
    failed_accounts = set()
    consecutive_errors = 0
    max_consecutive_errors = 5
    
    while True:
        try:
            # Check for failed accounts
            if len(failed_accounts) > 0:
                logger.error(f"\n!!! {len(failed_accounts)} accounts have failed: {failed_accounts} !!!\n")
                print(f"Some accounts have failed: {failed_accounts}")
                # TODO: Send Email/SMS notification that some accounts have failed
            
            # Validate Schwab token
            if not schwab_conn.is_token_valid():
                logger.error("\n!!! Invalid Schwab Token !!!\n")
                print("Invalid Schwab Token")
                # TODO: Send Email/SMS notification that the token is Invalid
                while True:
                    time.sleep(60)  # Wait 1 minute before checking again
                    # Could add token refresh logic here
            
            # Check for changes in holdings
            if check_for_change():
                logger.info("\n=== Change Detected ===\n")
                logger.info(f"Waiting for {CHANGE_WAIT} seconds before executing trades")
                print(f"Waiting for {CHANGE_WAIT} seconds before executing trades")
                time.sleep(CHANGE_WAIT)
                
                # Get current percentages
                try:
                    percentages = get_percentages()
                    logger.info(f"Retrieved percentages for {len(percentages.get('assets', {}))} assets")
                    
                    # Reset consecutive errors on successful API call
                    consecutive_errors = 0
                    
                except ComposerAPIError as e:
                    consecutive_errors += 1
                    handle_api_error(e, "getting percentages")
                    if consecutive_errors >= max_consecutive_errors:
                        logger.error(f"Too many consecutive API errors ({consecutive_errors}), waiting longer")
                        time.sleep(300)  # Wait 5 minutes
                        consecutive_errors = 0
                    continue
                except Exception as e:
                    logger.error(f"Unexpected error getting percentages: {e}")
                    time.sleep(PERIOD)
                    continue
                
                # Execute trades for each account
                account_nums = os.getenv('SCHWAB_ACCOUNT_NUMS', '').replace(" ", "").split(",")
                successful_accounts = set()
                
                for account_num in account_nums:
                    if not account_num.strip():
                        continue
                        
                    if account_num in failed_accounts:
                        logger.warning(f"Account Num: {account_num} is being skipped due to previous failures")
                        continue
                    
                    success = execute_trades_for_account(account_num, percentages, schwab_conn)
                    
                    if success:
                        successful_accounts.add(account_num)
                        # Remove from failed accounts if it was previously failed
                        failed_accounts.discard(account_num)
                    else:
                        failed_accounts.add(account_num)
                
                # Save changes only if we successfully processed at least one account
                if successful_accounts:
                    try:
                        save_changes(percentages)
                        logger.info(f"Successfully saved changes for accounts: {successful_accounts}")
                    except Exception as e:
                        logger.error(f"Failed to save changes: {e}")
                else:
                    logger.warning("No accounts were successfully processed, not saving changes")
            
            print("Awaiting Changes...")
            time.sleep(PERIOD)
            
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt, shutting down gracefully")
            print("\nShutting down gracefully...")
            break
        except Exception as e:
            logger.error(f"Unexpected error in main loop: {e}")
            print(f"Unexpected error: {e}")
            time.sleep(PERIOD)
            