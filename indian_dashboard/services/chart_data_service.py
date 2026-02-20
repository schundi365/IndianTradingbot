"""
Chart Data Service
Prepares historical price data and indicators for charting
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class ChartDataService:
    """Service for preparing chart data with technical indicators"""
    
    def __init__(self, broker_manager=None):
        self.broker_manager = broker_manager
        self.cache = {}
        self.cache_timeout = 300  # Cache for 5 minutes
    
    def get_price_data(
        self,
        symbol: str,
        timeframe: str = '15min',
        bars: int = 200,
        indicators: List[str] = None
    ) -> Dict:
        """
        Get historical price data with optional indicators
        
        Args:
            symbol: Trading symbol
            timeframe: Timeframe (1min, 5min, 15min, 1h, 1d)
            bars: Number of bars to fetch
            indicators: List of indicators to calculate
            
        Returns:
            Dictionary with OHLCV data and indicators
        """
        try:
            # Get historical data from broker
            df = self._fetch_historical_data(symbol, timeframe, bars)
            
            if df is None or len(df) == 0:
                return {'error': 'No data available'}
            
            # Calculate indicators if requested
            if indicators:
                df = self._calculate_indicators(df, indicators)
            
            # Format for frontend
            result = {
                'symbol': symbol,
                'timeframe': timeframe,
                'data': self._format_ohlcv(df),
                'indicators': {}
            }
            
            # Add indicator data
            if indicators:
                for indicator in indicators:
                    if indicator in df.columns:
                        result['indicators'][indicator] = df[indicator].fillna(0).tolist()
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting price data for {symbol}: {e}", exc_info=True)
            return {'error': str(e)}
    
    def get_indicator_data(
        self,
        symbol: str,
        indicator: str,
        timeframe: str = '15min',
        bars: int = 200,
        params: Dict = None
    ) -> Dict:
        """
        Get specific indicator data
        
        Args:
            symbol: Trading symbol
            indicator: Indicator name (ma, macd, rsi, atr, bollinger)
            timeframe: Timeframe
            bars: Number of bars
            params: Indicator parameters
            
        Returns:
            Dictionary with indicator data
        """
        try:
            df = self._fetch_historical_data(symbol, timeframe, bars)
            
            if df is None or len(df) == 0:
                return {'error': 'No data available'}
            
            # Calculate specific indicator
            df = self._calculate_single_indicator(df, indicator, params or {})
            
            result = {
                'symbol': symbol,
                'indicator': indicator,
                'timeframe': timeframe,
                'data': {}
            }
            
            # Extract indicator columns
            for col in df.columns:
                if col.lower().startswith(indicator.lower()) or col in ['close', 'time']:
                    result['data'][col] = df[col].fillna(0).tolist()
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting indicator data: {e}", exc_info=True)
            return {'error': str(e)}
    
    def get_trade_markers(self, symbol: str, trades: List[Dict]) -> List[Dict]:
        """
        Get trade entry/exit markers for chart overlay
        
        Args:
            symbol: Trading symbol
            trades: List of trades for this symbol
            
        Returns:
            List of marker dictionaries
        """
        try:
            markers = []
            
            for trade in trades:
                if trade.get('symbol') != symbol:
                    continue
                
                # Entry marker
                entry_time = trade.get('entry_time') or trade.get('timestamp')
                entry_price = trade.get('entry_price')
                
                if entry_time and entry_price:
                    markers.append({
                        'time': entry_time,
                        'price': float(entry_price),
                        'type': 'entry',
                        'side': trade.get('transaction_type', 'BUY'),
                        'quantity': trade.get('quantity', 0)
                    })
                
                # Exit marker
                exit_time = trade.get('exit_time')
                exit_price = trade.get('exit_price') or trade.get('close_price')
                
                if exit_time and exit_price:
                    pnl = trade.get('pnl', 0)
                    markers.append({
                        'time': exit_time,
                        'price': float(exit_price),
                        'type': 'exit',
                        'pnl': float(pnl),
                        'quantity': trade.get('quantity', 0)
                    })
            
            return markers
            
        except Exception as e:
            logger.error(f"Error getting trade markers: {e}", exc_info=True)
            return []
    
    # Private methods
    
    def _fetch_historical_data(self, symbol: str, timeframe: str, bars: int) -> Optional[pd.DataFrame]:
        """Fetch historical data from broker"""
        try:
            if not self.broker_manager or not self.broker_manager.is_connected():
                # Return mock data for testing
                return self._generate_mock_data(bars)
            
            adapter = self.broker_manager.get_adapter()
            if not adapter:
                return self._generate_mock_data(bars)
            
            # Convert timeframe to minutes
            timeframe_minutes = self._timeframe_to_minutes(timeframe)
            
            # Fetch data from broker
            if hasattr(adapter, 'get_historical_data'):
                df = adapter.get_historical_data(symbol, timeframe_minutes, bars)
                return df
            
            return self._generate_mock_data(bars)
            
        except Exception as e:
            logger.error(f"Error fetching historical data: {e}", exc_info=True)
            return self._generate_mock_data(bars)
    
    def _calculate_indicators(self, df: pd.DataFrame, indicators: List[str]) -> pd.DataFrame:
        """Calculate multiple indicators"""
        for indicator in indicators:
            df = self._calculate_single_indicator(df, indicator, {})
        return df
    
    def _calculate_single_indicator(self, df: pd.DataFrame, indicator: str, params: Dict) -> pd.DataFrame:
        """Calculate a single indicator"""
        try:
            indicator = indicator.lower()
            
            if indicator == 'ma' or indicator == 'sma':
                period = params.get('period', 20)
                df[f'ma_{period}'] = df['close'].rolling(window=period).mean()
            
            elif indicator == 'ema':
                period = params.get('period', 20)
                df[f'ema_{period}'] = df['close'].ewm(span=period, adjust=False).mean()
            
            elif indicator == 'macd':
                fast = params.get('fast', 12)
                slow = params.get('slow', 26)
                signal = params.get('signal', 9)
                
                ema_fast = df['close'].ewm(span=fast, adjust=False).mean()
                ema_slow = df['close'].ewm(span=slow, adjust=False).mean()
                df['macd'] = ema_fast - ema_slow
                df['macd_signal'] = df['macd'].ewm(span=signal, adjust=False).mean()
                df['macd_histogram'] = df['macd'] - df['macd_signal']
            
            elif indicator == 'rsi':
                period = params.get('period', 14)
                delta = df['close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
                rs = gain / loss
                df['rsi'] = 100 - (100 / (1 + rs))
            
            elif indicator == 'atr':
                period = params.get('period', 14)
                high_low = df['high'] - df['low']
                high_close = np.abs(df['high'] - df['close'].shift())
                low_close = np.abs(df['low'] - df['close'].shift())
                ranges = pd.concat([high_low, high_close, low_close], axis=1)
                true_range = np.max(ranges, axis=1)
                df['atr'] = true_range.rolling(window=period).mean()
            
            elif indicator == 'bollinger' or indicator == 'bb':
                period = params.get('period', 20)
                std_dev = params.get('std_dev', 2)
                
                df['bb_middle'] = df['close'].rolling(window=period).mean()
                std = df['close'].rolling(window=period).std()
                df['bb_upper'] = df['bb_middle'] + (std * std_dev)
                df['bb_lower'] = df['bb_middle'] - (std * std_dev)
            
            return df
            
        except Exception as e:
            logger.error(f"Error calculating indicator {indicator}: {e}", exc_info=True)
            return df
    
    def _format_ohlcv(self, df: pd.DataFrame) -> List[Dict]:
        """Format OHLCV data for frontend"""
        try:
            data = []
            
            for idx, row in df.iterrows():
                data.append({
                    'time': idx.isoformat() if isinstance(idx, datetime) else str(idx),
                    'open': float(row['open']),
                    'high': float(row['high']),
                    'low': float(row['low']),
                    'close': float(row['close']),
                    'volume': float(row.get('volume', 0))
                })
            
            return data
            
        except Exception as e:
            logger.error(f"Error formatting OHLCV data: {e}", exc_info=True)
            return []
    
    def _timeframe_to_minutes(self, timeframe: str) -> int:
        """Convert timeframe string to minutes"""
        timeframe = timeframe.lower()
        
        if 'min' in timeframe:
            return int(timeframe.replace('min', ''))
        elif 'h' in timeframe:
            return int(timeframe.replace('h', '')) * 60
        elif 'd' in timeframe:
            return int(timeframe.replace('d', '')) * 1440
        
        return 15  # Default to 15 minutes
    
    def _generate_mock_data(self, bars: int) -> pd.DataFrame:
        """Generate mock OHLCV data for testing"""
        try:
            dates = pd.date_range(end=datetime.now(), periods=bars, freq='15min')
            
            # Generate random walk price data
            np.random.seed(42)
            close_prices = 100 + np.cumsum(np.random.randn(bars) * 0.5)
            
            data = {
                'open': close_prices + np.random.randn(bars) * 0.2,
                'high': close_prices + np.abs(np.random.randn(bars) * 0.5),
                'low': close_prices - np.abs(np.random.randn(bars) * 0.5),
                'close': close_prices,
                'volume': np.random.randint(1000, 10000, bars)
            }
            
            df = pd.DataFrame(data, index=dates)
            return df
            
        except Exception as e:
            logger.error(f"Error generating mock data: {e}", exc_info=True)
            return pd.DataFrame()
