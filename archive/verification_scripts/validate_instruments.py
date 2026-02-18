"""
Instrument Validation Utility

This script validates configured instruments against the broker API.
It checks if instruments exist, are tradable, and have valid parameters.

Validates: Requirement 8.3

Usage:
    python validate_instruments.py --config config.json
    python validate_instruments.py --symbols RELIANCE TCS INFY
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from src.kite_adapter import KiteAdapter
from src.instrument_validator import InstrumentValidator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def load_config(config_path: str) -> dict:
    """Load configuration from JSON file"""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Failed to load config: {e}")
        sys.exit(1)


def validate_from_config(config_path: str):
    """Validate instruments from a configuration file"""
    logging.info(f"Loading configuration from {config_path}")
    config = load_config(config_path)
    
    # Initialize broker adapter
    broker = KiteAdapter(config)
    
    # Connect to broker
    if not broker.connect():
        logging.error("Failed to connect to broker")
        sys.exit(1)
    
    # Create validator
    validator = InstrumentValidator(broker)
    
    # Validate instruments
    all_valid, errors = validator.validate_config_instruments(config)
    
    if all_valid:
        logging.info("✅ All instruments are valid!")
        
        # Display instrument details
        symbols = config.get('symbols', [])
        logging.info("\nInstrument Details:")
        logging.info("-" * 80)
        
        for symbol in symbols:
            _, _, info = validator.validate_instrument(symbol)
            if info:
                logging.info(f"Symbol: {info['symbol']}")
                logging.info(f"  Lot Size: {info['lot_size']}")
                logging.info(f"  Tick Size: {info['tick_size']}")
                logging.info(f"  Instrument Token: {info['instrument_token']}")
                logging.info("-" * 80)
        
        return True
    else:
        logging.error("❌ Validation failed!")
        logging.error("\nErrors:")
        for error in errors:
            logging.error(f"  - {error}")
        return False


def validate_symbols(symbols: list, api_key: str, token_file: str):
    """Validate a list of symbols"""
    # Create minimal config
    config = {
        'kite_api_key': api_key,
        'kite_token_file': token_file,
        'default_exchange': 'NSE',
        'symbols': symbols
    }
    
    # Initialize broker adapter
    broker = KiteAdapter(config)
    
    # Connect to broker
    if not broker.connect():
        logging.error("Failed to connect to broker")
        sys.exit(1)
    
    # Create validator
    validator = InstrumentValidator(broker)
    
    # Validate each symbol
    logging.info(f"Validating {len(symbols)} symbols...")
    logging.info("-" * 80)
    
    results = validator.validate_instruments(symbols)
    
    # Display results
    if results['valid']:
        logging.info("\n✅ Valid Instruments:")
        for symbol, info in results['valid'].items():
            logging.info(f"  {symbol}:")
            logging.info(f"    Lot Size: {info['lot_size']}")
            logging.info(f"    Tick Size: {info['tick_size']}")
            logging.info(f"    Token: {info['instrument_token']}")
    
    if results['invalid']:
        logging.error("\n❌ Invalid Instruments:")
        for symbol, error in results['invalid'].items():
            logging.error(f"  {symbol}: {error}")
    
    logging.info("\n" + "=" * 80)
    logging.info(f"Summary: {results['summary']['valid_count']}/{results['summary']['total']} valid")
    logging.info("=" * 80)
    
    return results['summary']['invalid_count'] == 0


def main():
    parser = argparse.ArgumentParser(
        description='Validate trading instruments against broker API'
    )
    
    # Config file option
    parser.add_argument(
        '--config',
        type=str,
        help='Path to configuration JSON file'
    )
    
    # Individual symbols option
    parser.add_argument(
        '--symbols',
        nargs='+',
        help='List of symbols to validate'
    )
    
    parser.add_argument(
        '--api-key',
        type=str,
        help='Kite API key (required with --symbols)'
    )
    
    parser.add_argument(
        '--token-file',
        type=str,
        default='kite_token.json',
        help='Path to token file (default: kite_token.json)'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.config and not args.symbols:
        parser.error("Either --config or --symbols must be provided")
    
    if args.symbols and not args.api_key:
        parser.error("--api-key is required when using --symbols")
    
    # Run validation
    try:
        if args.config:
            success = validate_from_config(args.config)
        else:
            success = validate_symbols(args.symbols, args.api_key, args.token_file)
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        logging.info("\nValidation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Validation failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
