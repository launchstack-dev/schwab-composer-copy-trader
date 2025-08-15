# Schwab Copy Trader

A Python-based copy trading system that automatically mirrors portfolio allocations from Alpaca or Composer to Schwab brokerage accounts.

## Fork Information

This repository is a fork of [TheLeetTaco's alpaca_to_schwab project](https://github.com/TheLeetTaco/alpaca_to_schwab/tree/main). 

**Original Repository**: [https://github.com/TheLeetTaco/alpaca_to_schwab](https://github.com/TheLeetTaco/alpaca_to_schwab)

**Original Author**: [TheLeetTaco](https://github.com/TheLeetTaco)

This fork includes additional features and improvements while maintaining the core functionality of the original project.

## Features

- **Multi-Source Support**: Copy trades from Alpaca or Composer portfolios
- **Automatic Rebalancing**: Monitors for changes and automatically rebalances Schwab accounts
- **Robust Error Handling**: Comprehensive retry logic and error recovery
- **Configurable Settings**: Flexible configuration for trading parameters
- **Real-time Monitoring**: Continuous monitoring with configurable check intervals

## Requirements

- Python 3.8+
- Schwab API access
- Alpaca API access (if using Alpaca as source)
- Composer API access (if using Composer as source)

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd alpaca_to_schwab
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**:
   ```bash
   cp example.env .env
   # Edit .env with your API keys and settings
   ```

4. **Validate configuration**:
   ```bash
   python validate_config.py
   ```

## Configuration

### Environment Variables

#### Composer API (if using Composer as source)
```
COMPOSER_API_KEY=your_composer_api_key
COMPOSER_API_SECRET=your_composer_api_secret
COMPOSER_ACCOUNT_NUM=your_composer_account_number
```

#### Schwab API
```
SCWAHB_API_KEY=your_schwab_api_key
SCWAHB_SECRET_KEY=your_schwab_secret_key
SCHWAB_ACCOUNT_NUMS=account1,account2,account3
```

#### Alpaca API (if using Alpaca as source)
```
ALPACA_API_KEY=your_alpaca_api_key
ALPACA_SECRET_KEY=your_alpaca_secret_key
PAPER=true  # or false for live trading
```

#### Trading Settings
```
TRADE_SOURCE=composer  # or alpaca
MODE=debug  # or live
PERIOD=300  # seconds between checks
CHANGE_WAIT=30  # seconds to wait after detecting changes
RETRY=3  # number of retry attempts
TRADE_WITH=100  # percentage of account to trade with
PADDING=10.0  # padding amount in dollars
```

## Usage

### Quick Start

1. **Validate your configuration**:
   ```bash
   python validate_config.py
   ```

2. **Run the copy trader**:
   ```bash
   python copy_trade.py
   ```

### Testing Individual Components

- **Test Composer API**:
  ```bash
  python composer_api.py
  ```

- **Test holdings source**:
  ```bash
  python holdings_source.py
  ```

## Recent Updates (2025)

### Composer API Integration Improvements

- **Updated API Endpoints**: Migrated to current Composer API endpoints
- **Enhanced Authentication**: Improved authentication headers and error handling
- **Better Error Recovery**: Added retry logic with exponential backoff
- **Rate Limiting**: Proper handling of API rate limits
- **Data Structure Updates**: Updated to handle current Composer API response formats

### Key Changes Made

1. **API Base URL**: Updated from staging to production API
2. **Authentication Headers**: Standardized to current Composer API requirements
3. **Error Handling**: Added custom `ComposerAPIError` exception class
4. **Retry Logic**: Implemented robust retry mechanism with backoff
5. **Data Processing**: Updated to handle current holdings data structure
6. **Configuration Validation**: Added comprehensive validation script

### Breaking Changes

- **API Endpoints**: Changed from `/accounts/list` to `/v1/accounts`
- **Authentication**: Updated header format and naming
- **Data Structure**: Modified to handle new Composer API response format

## Architecture

### Core Components

- **`composer_api.py`**: Handles Composer API interactions
- **`alpaca_api.py`**: Handles Alpaca API interactions  
- **`schwab_api.py`**: Handles Schwab API interactions
- **`holdings_source.py`**: Manages portfolio data from different sources
- **`copy_trade.py`**: Main application logic
- **`validate_config.py`**: Configuration validation utility

### Data Flow

1. **Monitor**: Continuously check for portfolio changes
2. **Fetch**: Retrieve current holdings from source (Alpaca/Composer)
3. **Compare**: Detect changes against saved snapshot
4. **Execute**: Place trades in Schwab accounts to match target allocation
5. **Save**: Update local snapshot for next comparison

## Error Handling

The system includes comprehensive error handling:

- **API Errors**: Custom exception handling for different API providers
- **Retry Logic**: Automatic retry with exponential backoff
- **Rate Limiting**: Proper handling of API rate limits
- **Token Validation**: Automatic Schwab token validation
- **Account Failures**: Individual account failure tracking

## Logging

All operations are logged to the `logs/` directory:

- `composer.log`: Composer API operations
- `copy_trade.log`: Main application operations
- `trade_source.log`: Holdings source operations

## Safety Features

- **Debug Mode**: Test configuration without placing real trades
- **Account Validation**: Verify account access before trading
- **Balance Checks**: Ensure sufficient funds before placing orders
- **Change Detection**: Only trade when actual changes are detected

## Troubleshooting

### Common Issues

1. **API Connection Failures**:
   - Verify API keys are correct
   - Check network connectivity
   - Ensure API endpoints are accessible

2. **Authentication Errors**:
   - Verify API credentials
   - Check token expiration (Schwab)
   - Ensure proper permissions

3. **Configuration Issues**:
   - Run `python validate_config.py` to check setup
   - Verify all required environment variables are set
   - Check account numbers and formats

### Getting Help

If you encounter issues:

1. Check the logs in the `logs/` directory
2. Run the validation script: `python validate_config.py`
3. Test individual components separately
4. Review the configuration documentation

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions:

- Check the documentation above
- Review the logs for error details
- Test with the validation script
- Consider contributing improvements

---

**Note**: This tool involves automated trading. Use at your own risk and ensure you understand the implications of automated trading before using this software.

## Acknowledgments

This project is based on the excellent work by [TheLeetTaco](https://github.com/TheLeetTaco) and their original [alpaca_to_schwab repository](https://github.com/TheLeetTaco/alpaca_to_schwab). 

If you find this project useful, consider:
- Starring the [original repository](https://github.com/TheLeetTaco/alpaca_to_schwab)
- Contributing to the original project

The original project requirements can be found at: [Schwab-py Documentation](https://schwab-py.readthedocs.io/en/latest/)
