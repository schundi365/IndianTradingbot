"""
Test indicator calculation methods for Indian Trading Bot
Verifies that indicators work correctly with broker data
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.indian_trading_bot import IndianTradingBot
from src.broker_adapter import BrokerAdapter


class MockBrokerAdapter(BrokerAdapter):
    """Mock broker adapter for testing"""
    
    def connect(self) -> bool:
        return True
    
    def disconnect(self) -> None:
        pass
    
    def is_connected(self) -> bool:
        return True
    
    def get_historical_data(self, symbol: str, timeframe: str, bars: int):
        # Return mock data
        dates = pd.date_range(end=datetime.now(), periods=bars, freq='30min')
        data = {
            'time': dates,
            'open': np.random.uniform(100, 110, bars),
            'high': np.random.uniform(110, 120, bars),
            'low': np.random.uniform(90, 100, bars),
            'close': np.random.uniform(100, 110, bars),
            'volume': np.random.randint(1000, 10000, bars)
        }
        return pd.DataFrame(data)
    
    def place_order(self, symbol: str, direction: int, quantity: float, 
                   order_type: str, price=None, trigger_price=None, 
                   stop_loss=None, take_profit=None, product_type="MIS"):
        return "ORDER123"
    
    def modify_order(self, order_id: str, quantity=None, price=None, trigger_price=None):
        return True
    
    def cancel_order(self, order_id: str):
        return True
    
    def get_positions(self, symbol=None):
        return []
    
    def get_account_info(self):
        return {
            'balance': 100000,
            'equity': 100000,
            'margin_available': 80000,
            'margin_used': 20000
        }
    
    def get_instrument_info(self, symbol: str):
        return {
            'symbol': symbol,
            'lot_size': 50,
            'tick_size': 0.05,
            'instrument_token': '12345'
        }
    
    def convert_timeframe(self, mt5_timeframe: int):
        return "30minute"


def create_test_data(bars=100):
    """Create test price data"""
    dates = pd.date_range(end=datetime.now(), periods=bars, freq='30min')
    
    # Create realistic price data with trend
    base_price = 100
    trend = np.linspace(0, 10, bars)
    noise = np.random.normal(0, 2, bars)
    
    close_prices = base_price + trend + noise
    
    data = {
        'time': dates,
        'open': close_prices + np.random.uniform(-1, 1, bars),
        'high': close_prices + np.random.uniform(1, 3, bars),
        'low': close_prices - np.random.uniform(1, 3, bars),
        'close': close_prices,
        'volume': np.random.randint(1000, 10000, bars)
    }
    
    return pd.DataFrame(data)


class TestIndicatorCalculation:
    """Test indicator calculation methods"""
    
    def test_calculate_indicators_basic(self):
        """Test that calculate_indicators adds all required indicators"""
        # Setup
        config = {
            'symbols': ['NIFTY50'],
            'timeframe': 30,
            'risk_percent': 1.0,
            'fast_ma_period': 10,
            'slow_ma_period': 21,
            'atr_period': 14,
            'macd_fast': 12,
            'macd_slow': 26,
            'macd_signal': 9
        }
        
        broker = MockBrokerAdapter()
        bot = IndianTradingBot(config, broker)
        
        # Create test data
        df = create_test_data(100)
        
        # Calculate indicators
        result = bot.calculate_indicators(df)
        
        # Verify all indicators are present
        expected_indicators = [
            'fast_ma', 'slow_ma', 'ema6', 'ema12', 'roc3',
            'atr', 'rsi', 'macd', 'macd_signal', 'macd_histogram',
            'ma_trend', 'ma_cross'
        ]
        
        for indicator in expected_indicators:
            assert indicator in result.columns, f"Missing indicator: {indicator}"
        
        # Verify data types
        assert result['fast_ma'].dtype == np.float64
        assert result['slow_ma'].dtype == np.float64
        assert result['rsi'].dtype == np.float64
        assert result['atr'].dtype == np.float64
        
        print("✅ All indicators calculated correctly")
    
    def test_calculate_indicators_values(self):
        """Test that indicator values are reasonable"""
        config = {
            'symbols': ['NIFTY50'],
            'timeframe': 30,
            'risk_percent': 1.0,
            'fast_ma_period': 10,
            'slow_ma_period': 21,
            'atr_period': 14
        }
        
        broker = MockBrokerAdapter()
        bot = IndianTradingBot(config, broker)
        
        # Create test data
        df = create_test_data(100)
        
        # Calculate indicators
        result = bot.calculate_indicators(df)
        
        # Check RSI is between 0 and 100
        rsi_values = result['rsi'].dropna()
        assert (rsi_values >= 0).all(), "RSI values below 0"
        assert (rsi_values <= 100).all(), "RSI values above 100"
        
        # Check ATR is positive
        atr_values = result['atr'].dropna()
        assert (atr_values > 0).all(), "ATR values not positive"
        
        # Check MA trend is 1 or -1
        ma_trend_values = result['ma_trend'].dropna()
        assert set(ma_trend_values.unique()).issubset({1, -1}), "MA trend not 1 or -1"
        
        # Check MA cross is 0, 1, or -1
        ma_cross_values = result['ma_cross'].unique()
        assert set(ma_cross_values).issubset({0, 1, -1}), "MA cross not 0, 1, or -1"
        
        print("✅ Indicator values are reasonable")
    
    def test_calculate_indicators_with_broker_data(self):
        """Test that indicators work with broker-fetched data"""
        config = {
            'symbols': ['NIFTY50'],
            'timeframe': 30,
            'risk_percent': 1.0
        }
        
        broker = MockBrokerAdapter()
        bot = IndianTradingBot(config, broker)
        
        # Fetch data using broker adapter (mocked)
        df = bot.get_historical_data('NIFTY50', 30, 100)
        
        assert df is not None, "Failed to fetch data"
        assert len(df) > 0, "No data returned"
        
        # Calculate indicators
        result = bot.calculate_indicators(df)
        
        # Verify indicators calculated
        assert 'fast_ma' in result.columns
        assert 'slow_ma' in result.columns
        assert 'rsi' in result.columns
        assert 'atr' in result.columns
        
        # Verify no errors in calculation
        assert not result['fast_ma'].isna().all(), "Fast MA all NaN"
        assert not result['slow_ma'].isna().all(), "Slow MA all NaN"
        
        print("✅ Indicators work with broker data")
    
    def test_calculate_indicators_preserves_data(self):
        """Test that original price data is preserved"""
        config = {
            'symbols': ['NIFTY50'],
            'timeframe': 30,
            'risk_percent': 1.0
        }
        
        broker = MockBrokerAdapter()
        bot = IndianTradingBot(config, broker)
        
        # Create test data
        df = create_test_data(100)
        original_close = df['close'].copy()
        
        # Calculate indicators
        result = bot.calculate_indicators(df)
        
        # Verify original data preserved
        assert (result['close'] == original_close).all(), "Close prices modified"
        assert 'open' in result.columns, "Open column missing"
        assert 'high' in result.columns, "High column missing"
        assert 'low' in result.columns, "Low column missing"
        assert 'volume' in result.columns, "Volume column missing"
        
        print("✅ Original data preserved")


if __name__ == "__main__":
    # Run tests
    test = TestIndicatorCalculation()
    
    print("="*60)
    print("Testing Indicator Calculation")
    print("="*60)
    
    try:
        test.test_calculate_indicators_basic()
        test.test_calculate_indicators_values()
        test.test_calculate_indicators_with_broker_data()
        test.test_calculate_indicators_preserves_data()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED")
        print("="*60)
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
