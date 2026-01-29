"""
Test Volume Analyzer with Real MT5 Data
"""

import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta
from src.volume_analyzer import VolumeAnalyzer

def test_volume_analyzer():
    """Test volume analyzer with real MT5 data"""
    
    print("=" * 80)
    print("VOLUME ANALYZER TEST")
    print("=" * 80)
    print()
    
    # Initialize MT5
    if not mt5.initialize():
        print("❌ Failed to initialize MT5")
        return
    
    print("✅ MT5 Connected")
    print()
    
    # Get data
    symbol = "XAUUSD"
    timeframe = mt5.TIMEFRAME_M30
    bars = 100
    
    print(f"Fetching {bars} bars of {symbol} on M30...")
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, bars)
    
    if rates is None or len(rates) == 0:
        print("❌ Failed to get data")
        mt5.shutdown()
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    
    print(f"✅ Got {len(df)} bars")
    print()
    
    # Initialize analyzer
    config = {
        'use_volume_filter': True,
        'min_volume_ma': 1.2,
        'volume_ma_period': 20,
        'obv_period': 14
    }
    
    analyzer = VolumeAnalyzer(config)
    
    # Test 1: Volume MA
    print("=" * 80)
    print("TEST 1: VOLUME MOVING AVERAGE")
    print("=" * 80)
    current_volume = df['tick_volume'].iloc[-1]
    volume_ma = df['tick_volume'].rolling(20).mean().iloc[-1]
    is_above = analyzer.is_above_average_volume(df)
    
    print(f"Current Volume: {current_volume:,.0f}")
    print(f"20-Period MA:   {volume_ma:,.0f}")
    print(f"Ratio:          {current_volume/volume_ma:.2f}x")
    print(f"Above Average:  {'✅ YES' if is_above else '❌ NO'}")
    print()
    
    # Test 2: Volume Trend
    print("=" * 80)
    print("TEST 2: VOLUME TREND")
    print("=" * 80)
    trend = analyzer.get_volume_trend(df, periods=5)
    print(f"Volume Trend (5 bars): {trend.upper()}")
    
    recent_volumes = df['tick_volume'].iloc[-5:].values
    print(f"Recent volumes: {[f'{v:,.0f}' for v in recent_volumes]}")
    print()
    
    # Test 3: OBV
    print("=" * 80)
    print("TEST 3: ON-BALANCE VOLUME (OBV)")
    print("=" * 80)
    obv_signal = analyzer.get_obv_signal(df)
    obv = analyzer.calculate_obv(df)
    obv_ma = obv.rolling(14).mean()
    
    print(f"OBV Signal:     {obv_signal.upper()}")
    print(f"Current OBV:    {obv.iloc[-1]:,.0f}")
    print(f"OBV MA (14):    {obv_ma.iloc[-1]:,.0f}")
    print()
    
    # Test 4: Divergence
    print("=" * 80)
    print("TEST 4: VOLUME DIVERGENCE")
    print("=" * 80)
    divergence = analyzer.check_volume_divergence(df, periods=10)
    print(f"Divergence:     {divergence.upper()}")
    print()
    
    # Test 5: Volume Profile
    print("=" * 80)
    print("TEST 5: VOLUME PROFILE")
    print("=" * 80)
    profile = analyzer.calculate_volume_profile(df, num_bins=10)
    if profile:
        print(f"Point of Control (POC):")
        print(f"  Price:  ${profile['poc_price']:.2f}")
        print(f"  Volume: {profile['poc_volume']:,.0f}")
        print(f"Price Range: ${profile['price_range'][0]:.2f} - ${profile['price_range'][1]:.2f}")
    print()
    
    # Test 6: Buy Signal Confirmation
    print("=" * 80)
    print("TEST 6: BUY SIGNAL CONFIRMATION")
    print("=" * 80)
    should_trade_buy, confidence_buy = analyzer.should_trade(df, 'buy')
    confirmation_buy = analyzer.get_volume_confirmation(df, 'buy')
    
    print(f"Should Trade:        {'✅ YES' if should_trade_buy else '❌ NO'}")
    print(f"Confidence Boost:    {confidence_buy:+.1%}")
    print(f"Above Average:       {'✅' if confirmation_buy['above_average'] else '❌'}")
    print(f"Volume Trend:        {confirmation_buy['volume_trend']}")
    print(f"OBV Signal:          {confirmation_buy['obv_signal']}")
    print(f"Divergence:          {confirmation_buy['divergence']}")
    print()
    
    # Test 7: Sell Signal Confirmation
    print("=" * 80)
    print("TEST 7: SELL SIGNAL CONFIRMATION")
    print("=" * 80)
    should_trade_sell, confidence_sell = analyzer.should_trade(df, 'sell')
    confirmation_sell = analyzer.get_volume_confirmation(df, 'sell')
    
    print(f"Should Trade:        {'✅ YES' if should_trade_sell else '❌ NO'}")
    print(f"Confidence Boost:    {confidence_sell:+.1%}")
    print(f"Above Average:       {'✅' if confirmation_sell['above_average'] else '❌'}")
    print(f"Volume Trend:        {confirmation_sell['volume_trend']}")
    print(f"OBV Signal:          {confirmation_sell['obv_signal']}")
    print(f"Divergence:          {confirmation_sell['divergence']}")
    print()
    
    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Symbol:              {symbol}")
    print(f"Timeframe:           M30")
    print(f"Bars Analyzed:       {len(df)}")
    print(f"Current Price:       ${df['close'].iloc[-1]:.2f}")
    print(f"Current Volume:      {current_volume:,.0f}")
    print(f"Volume Status:       {'✅ Above Average' if is_above else '❌ Below Average'}")
    print(f"Volume Trend:        {trend.upper()}")
    print(f"OBV Signal:          {obv_signal.upper()}")
    print(f"Buy Confirmation:    {'✅ CONFIRMED' if should_trade_buy else '❌ NOT CONFIRMED'}")
    print(f"Sell Confirmation:   {'✅ CONFIRMED' if should_trade_sell else '❌ NOT CONFIRMED'}")
    print()
    
    # Cleanup
    mt5.shutdown()
    
    print("=" * 80)
    print("✅ VOLUME ANALYZER TEST COMPLETE!")
    print("=" * 80)


if __name__ == "__main__":
    test_volume_analyzer()
