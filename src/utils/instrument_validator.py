"""
Instrument Validator Module

This module provides functionality to validate instruments configured for trading.
It checks if instruments exist, are tradable, and have valid parameters.

Validates: Requirement 8.3
"""

import logging
from typing import Dict, List, Optional, Tuple
from src.adapters.broker_adapter import BrokerAdapter


class InstrumentValidator:
    """
    Validates trading instruments against broker requirements.
    
    Validates: Requirement 8.3
    """
    
    def __init__(self, broker_adapter: BrokerAdapter, logger: Optional[logging.Logger] = None):
        """
        Initialize the instrument validator.
        
        Args:
            broker_adapter: Broker adapter instance for fetching instrument info
            logger: Optional logger instance
        """
        self.broker = broker_adapter
        self.logger = logger or logging.getLogger(__name__)
    
    def validate_instrument(self, symbol: str) -> Tuple[bool, Optional[str], Optional[Dict]]:
        """
        Validate a single instrument.
        
        Validates: Requirement 8.3
        
        Args:
            symbol: Instrument symbol to validate
        
        Returns:
            Tuple of (is_valid, error_message, instrument_info)
            - is_valid: True if instrument is valid, False otherwise
            - error_message: Error description if invalid, None if valid
            - instrument_info: Instrument details if valid, None if invalid
        """
        try:
            # Check if broker is connected
            if not self.broker.is_connected():
                return False, "Broker not connected", None
            
            # Fetch instrument info
            instrument_info = self.broker.get_instrument_info(symbol)
            
            if instrument_info is None:
                return False, f"Instrument '{symbol}' does not exist or is not available", None
            
            # Validate instrument parameters
            lot_size = instrument_info.get('lot_size')
            tick_size = instrument_info.get('tick_size')
            instrument_token = instrument_info.get('instrument_token')
            
            # Check lot size
            if lot_size is None or lot_size <= 0:
                return False, f"Invalid lot size for '{symbol}': {lot_size}", None
            
            # Check tick size
            if tick_size is None or tick_size <= 0:
                return False, f"Invalid tick size for '{symbol}': {tick_size}", None
            
            # Check instrument token
            if not instrument_token:
                return False, f"Missing instrument token for '{symbol}'", None
            
            self.logger.info(f"Instrument '{symbol}' validated successfully")
            return True, None, instrument_info
            
        except Exception as e:
            error_msg = f"Error validating instrument '{symbol}': {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg, None
    
    def validate_instruments(self, symbols: List[str]) -> Dict[str, Dict]:
        """
        Validate multiple instruments.
        
        Validates: Requirement 8.3
        
        Args:
            symbols: List of instrument symbols to validate
        
        Returns:
            Dictionary with validation results:
            {
                'valid': {symbol: instrument_info, ...},
                'invalid': {symbol: error_message, ...},
                'summary': {
                    'total': int,
                    'valid_count': int,
                    'invalid_count': int
                }
            }
        """
        results = {
            'valid': {},
            'invalid': {},
            'summary': {
                'total': len(symbols),
                'valid_count': 0,
                'invalid_count': 0
            }
        }
        
        for symbol in symbols:
            is_valid, error_msg, instrument_info = self.validate_instrument(symbol)
            
            if is_valid:
                results['valid'][symbol] = instrument_info
                results['summary']['valid_count'] += 1
            else:
                results['invalid'][symbol] = error_msg
                results['summary']['invalid_count'] += 1
        
        return results
    
    def validate_config_instruments(self, config: Dict) -> Tuple[bool, List[str]]:
        """
        Validate all instruments in a configuration.
        
        Validates: Requirement 8.3
        
        Args:
            config: Trading bot configuration dictionary
        
        Returns:
            Tuple of (all_valid, error_messages)
            - all_valid: True if all instruments are valid, False otherwise
            - error_messages: List of error messages for invalid instruments
        """
        symbols = config.get('symbols', [])
        
        if not symbols:
            return False, ["No symbols configured"]
        
        validation_results = self.validate_instruments(symbols)
        
        if validation_results['summary']['invalid_count'] > 0:
            error_messages = [
                f"{symbol}: {error}" 
                for symbol, error in validation_results['invalid'].items()
            ]
            return False, error_messages
        
        return True, []
    
    def is_instrument_tradable(self, symbol: str) -> bool:
        """
        Check if an instrument is tradable.
        
        Validates: Requirement 8.3
        
        Args:
            symbol: Instrument symbol
        
        Returns:
            True if instrument is tradable, False otherwise
        """
        is_valid, _, _ = self.validate_instrument(symbol)
        return is_valid
