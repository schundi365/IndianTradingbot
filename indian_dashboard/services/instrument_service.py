"""
Instrument Service
Manages instrument data with caching
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class InstrumentService:
    """Manages instrument data with caching"""
    
    def __init__(self, cache_dir: Path, cache_ttl: int = 86400):
        """
        Initialize instrument service
        
        Args:
            cache_dir: Directory to store cached instrument data
            cache_ttl: Cache time-to-live in seconds (default: 24 hours)
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_ttl = cache_ttl
        self.instruments_cache = {}
        self.cache_timestamp = None
    
    def get_cache_file(self, broker: str) -> Path:
        """Get cache file path for broker"""
        return self.cache_dir / f"instruments_{broker}.json"
    
    def is_cache_valid(self, broker: str) -> bool:
        """
        Check if cache is valid
        
        Args:
            broker: Broker ID
            
        Returns:
            True if cache is valid, False otherwise
        """
        cache_file = self.get_cache_file(broker)
        
        if not cache_file.exists():
            return False
        
        # Check file modification time
        mtime = datetime.fromtimestamp(cache_file.stat().st_mtime)
        age = datetime.now() - mtime
        
        return age.total_seconds() < self.cache_ttl

    def load_from_cache(self, broker: str) -> Optional[List[Dict]]:
        """
        Load instruments from cache
        
        Args:
            broker: Broker ID
            
        Returns:
            List of instruments or None if cache invalid
        """
        try:
            if not self.is_cache_valid(broker):
                logger.info(f"Cache invalid or expired for {broker}")
                return None
            
            cache_file = self.get_cache_file(broker)
            
            with open(cache_file, 'r') as f:
                data = json.load(f)
            
            logger.info(f"Loaded {len(data)} instruments from cache for {broker}")
            return data
            
        except Exception as e:
            logger.error(f"Error loading from cache: {e}", exc_info=True)
            return None
    
    def save_to_cache(self, broker: str, instruments: List[Dict]) -> bool:
        """
        Save instruments to cache
        
        Args:
            broker: Broker ID
            instruments: List of instrument dictionaries
            
        Returns:
            True if successful, False otherwise
        """
        try:
            cache_file = self.get_cache_file(broker)
            
            with open(cache_file, 'w') as f:
                json.dump(instruments, f, indent=2)
            
            logger.info(f"Saved {len(instruments)} instruments to cache for {broker}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving to cache: {e}", exc_info=True)
            return False
    
    def get_instruments(self, broker_adapter, broker: str, force_refresh: bool = False) -> List[Dict]:
        """
        Get instruments with caching
        
        Args:
            broker_adapter: Broker adapter instance
            broker: Broker ID
            force_refresh: Force refresh from broker
            
        Returns:
            List of instrument dictionaries
        """
        try:
            # Try cache first if not forcing refresh
            if not force_refresh:
                cached = self.load_from_cache(broker)
                if cached is not None:
                    return cached
            
            # Fetch from broker
            logger.info(f"Fetching instruments from {broker}...")
            instruments = broker_adapter.get_instruments()
            
            if not instruments:
                logger.warning(f"No instruments returned from {broker}")
                return []
            
            # Convert to standard format
            formatted_instruments = []
            for inst in instruments:
                formatted_instruments.append({
                    'token': inst.get('instrument_token') or inst.get('token'),
                    'symbol': inst.get('tradingsymbol') or inst.get('symbol'),
                    'name': inst.get('name', ''),
                    'exchange': inst.get('exchange', ''),
                    'instrument_type': inst.get('instrument_type', ''),
                    'segment': inst.get('segment', ''),
                    'expiry': inst.get('expiry', ''),
                    'strike': inst.get('strike', 0),
                    'lot_size': inst.get('lot_size', 1),
                    'tick_size': inst.get('tick_size', 0.05),
                })
            
            # Save to cache
            self.save_to_cache(broker, formatted_instruments)
            
            logger.info(f"Fetched {len(formatted_instruments)} instruments from {broker}")
            return formatted_instruments
            
        except Exception as e:
            logger.error(f"Error getting instruments: {e}", exc_info=True)
            # Try to return cached data as fallback
            cached = self.load_from_cache(broker)
            return cached if cached else []
    
    def refresh_instruments(self, broker_adapter, broker: str) -> List[Dict]:
        """
        Force refresh instruments from broker
        
        Args:
            broker_adapter: Broker adapter instance
            broker: Broker ID
            
        Returns:
            List of instrument dictionaries
        """
        return self.get_instruments(broker_adapter, broker, force_refresh=True)
    
    def search_instruments(self, instruments: List[Dict], query: str) -> List[Dict]:
        """
        Search instruments by symbol or name
        
        Args:
            instruments: List of instruments
            query: Search query
            
        Returns:
            Filtered list of instruments
        """
        if not query:
            return instruments
        
        query = query.upper()
        
        results = []
        for inst in instruments:
            symbol = inst.get('symbol', '').upper()
            name = inst.get('name', '').upper()
            
            if query in symbol or query in name:
                results.append(inst)
        
        return results
    
    def filter_instruments(self, instruments: List[Dict], filters: Dict) -> List[Dict]:
        """
        Filter instruments by exchange, type, etc.
        
        Args:
            instruments: List of instruments
            filters: Dictionary of filters
                - exchange: List of exchanges (e.g., ['NSE', 'BSE'])
                - instrument_type: List of types (e.g., ['EQ', 'FUT'])
                - segment: List of segments
                
        Returns:
            Filtered list of instruments
        """
        results = instruments
        
        # Filter by exchange
        if filters.get('exchange'):
            exchanges = [e.upper() for e in filters['exchange']]
            results = [inst for inst in results if inst.get('exchange', '').upper() in exchanges]
        
        # Filter by instrument type
        if filters.get('instrument_type'):
            types = [t.upper() for t in filters['instrument_type']]
            results = [inst for inst in results if inst.get('instrument_type', '').upper() in types]
        
        # Filter by segment
        if filters.get('segment'):
            segments = [s.upper() for s in filters['segment']]
            results = [inst for inst in results if inst.get('segment', '').upper() in segments]
        
        return results
    
    def get_instrument_by_token(self, instruments: List[Dict], token: int) -> Optional[Dict]:
        """
        Get instrument by token
        
        Args:
            instruments: List of instruments
            token: Instrument token
            
        Returns:
            Instrument dictionary or None
        """
        for inst in instruments:
            if inst.get('token') == token:
                return inst
        
        return None
    
    def get_instrument_by_symbol(self, instruments: List[Dict], symbol: str, exchange: str = None) -> Optional[Dict]:
        """
        Get instrument by symbol
        
        Args:
            instruments: List of instruments
            symbol: Trading symbol
            exchange: Optional exchange filter
            
        Returns:
            Instrument dictionary or None
        """
        symbol = symbol.upper()
        
        for inst in instruments:
            if inst.get('symbol', '').upper() == symbol:
                if exchange is None or inst.get('exchange', '').upper() == exchange.upper():
                    return inst
        
        return None
    
    def get_cache_info(self, broker: str) -> Dict:
        """
        Get cache information
        
        Args:
            broker: Broker ID
            
        Returns:
            Dictionary with cache info
        """
        cache_file = self.get_cache_file(broker)
        
        if not cache_file.exists():
            return {
                'exists': False,
                'valid': False,
                'timestamp': None,
                'age_seconds': None,
                'count': 0
            }
        
        mtime = datetime.fromtimestamp(cache_file.stat().st_mtime)
        age = datetime.now() - mtime
        
        # Count instruments
        try:
            with open(cache_file, 'r') as f:
                data = json.load(f)
                count = len(data)
        except:
            count = 0
        
        return {
            'exists': True,
            'valid': self.is_cache_valid(broker),
            'timestamp': mtime.isoformat(),
            'age_seconds': int(age.total_seconds()),
            'count': count
        }
