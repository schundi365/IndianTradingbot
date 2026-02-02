#!/usr/bin/env python3
"""
Comprehensive ADX Data Diagnostic Tool
Analyzes why ADX data might be missing and provides solutions
"""

import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

def diagnose_adx_data():
    """Comprehensive diagnosis of ADX data availability"""
    
    print("=" * 80)
    print("🔍 ADX DATA DIAGNOSTIC TOOL")
    print("=" * 80)
    
    # Initialize MT5
    if not mt5.initialize():
        print("❌ Failed to initialize MT5")
        return False
    
    # Load configuration to get symbols
    try:
        with open('bot_config.json', 'r') as f:
            config = json.load(f)
        symbols = config.get('symbols', ['EURUSD', 'GBPUSD', 'XAUUSD'])
        timeframe = config.get('timeframe', 16385)  # H1
    except:
        symbols = ['EURUSD', 'GBPUSD', 'XAUUSD', 'XAGUSD']
        timeframe = mt5.TIMEFRAME_H1
    
    print(f"📊 Testing ADX calculation for {len(symbols)} symbols")
    print(f"⏰ Timeframe: {timeframe}")
    print()
    
    # Map timeframe values
    timeframe_map = {
        1: mt5.TIMEFRAME_M1,
        5: mt5.TIMEFRAME_M5,
        15: mt5.TIMEFRAME_M15,
        30: mt5.TIMEFRAME_M30,
        16385: mt5.TIMEFRAME_H1,
        16388: mt5.TIMEFRAME_H4,
        16408: mt5.TIMEFRAME_D1
    }
    
    mt5_timeframe = timeframe_map.get(timeframe, mt5.TIMEFRAME_H1)
    
    results = []
    
    for symbol in symbols:
        print(f"\n🔍 ANALYZING {symbol}")
        print("-" * 50)
        
        result = {
            'symbol': symbol,
            'data_available': False,
            'bars_count': 0,
            'adx_calculated': False,
            'issues': [],
            'recommendations': []
        }
        
        try:
            # 1. Check symbol availability
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                result['issues'].append("Symbol not found in MT5")
                result['recommendations'].append("Check symbol name spelling")
                print(f"❌ Symbol not found: {symbol}")
                results.append(result)
                continue
            
            # 2. Ensure symbol is visible
            if not symbol_info.visible:
                if not mt5.symbol_select(symbol, True):
                    result['issues'].append("Cannot select symbol in Market Watch")
                    result['recommendations'].append("Add symbol to Market Watch manually")
                    print(f"❌ Cannot select symbol: {symbol}")
                    results.append(result)
                    continue
            
            print(f"✅ Symbol available: {symbol}")
            
            # 3. Get historical data
            bars_needed = 200  # Sufficient for ADX calculation
            rates = mt5.copy_rates_from_pos(symbol, mt5_timeframe, 0, bars_needed)
            
            if rates is None or len(rates) == 0:
                result['issues'].append("No historical data available")
                result['recommendations'].append("Check broker data feed or try different timeframe")
                print(f"❌ No historical data for {symbol}")
                results.append(result)
                continue
            
            result['bars_count'] = len(rates)
            result['data_available'] = True
            print(f"✅ Historical data: {len(rates)} bars")
            
            # 4. Convert to DataFrame
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            
            # 5. Check data quality
            print(f"📊 Data Quality Check:")
            print(f"   Date range: {df['time'].iloc[0]} to {df['time'].iloc[-1]}")
            print(f"   Price range: {df['low'].min():.5f} - {df['high'].max():.5f}")
            
            # Check for missing or invalid data
            missing_data = df[['open', 'high', 'low', 'close']].isnull().sum().sum()
            if missing_data > 0:
                result['issues'].append(f"Missing OHLC data: {missing_data} values")
                result['recommendations'].append("Request fresh data from broker")
                print(f"⚠️  Missing OHLC data: {missing_data} values")
            
            # Check for zero values
            zero_values = (df[['open', 'high', 'low', 'close']] == 0).sum().sum()
            if zero_values > 0:
                result['issues'].append(f"Zero price values: {zero_values} occurrences")
                result['recommendations'].append("Check data feed quality")
                print(f"⚠️  Zero price values: {zero_values} occurrences")
            
            # Check for identical OHLC (flat candles)
            flat_candles = ((df['open'] == df['high']) & 
                           (df['high'] == df['low']) & 
                           (df['low'] == df['close'])).sum()
            if flat_candles > len(df) * 0.1:  # More than 10% flat candles
                result['issues'].append(f"Too many flat candles: {flat_candles} ({flat_candles/len(df)*100:.1f}%)")
                result['recommendations'].append("Market may be closed or data feed issue")
                print(f"⚠️  Flat candles: {flat_candles} ({flat_candles/len(df)*100:.1f}%)")
            
            # 6. Attempt ADX calculation
            print(f"\n🧮 ADX Calculation Test:")
            
            try:
                # Calculate True Range components
                df['high_low'] = df['high'] - df['low']
                df['high_close'] = np.abs(df['high'] - df['close'].shift())
                df['low_close'] = np.abs(df['low'] - df['close'].shift())
                df['tr'] = df[['high_low', 'high_close', 'low_close']].max(axis=1)
                
                print(f"   ✅ True Range calculated")
                
                # Calculate Directional Movement
                df['up_move'] = df['high'] - df['high'].shift()
                df['down_move'] = df['low'].shift() - df['low']
                
                df['plus_dm'] = np.where((df['up_move'] > df['down_move']) & (df['up_move'] > 0), df['up_move'], 0)
                df['minus_dm'] = np.where((df['down_move'] > df['up_move']) & (df['down_move'] > 0), df['down_move'], 0)
                
                print(f"   ✅ Directional Movement calculated")
                
                # Calculate smoothed values (14-period)
                period = 14
                df['tr_smooth'] = df['tr'].rolling(window=period).mean()
                df['plus_dm_smooth'] = df['plus_dm'].rolling(window=period).mean()
                df['minus_dm_smooth'] = df['minus_dm'].rolling(window=period).mean()
                
                print(f"   ✅ Smoothed values calculated")
                
                # Calculate Directional Indicators
                df['plus_di'] = 100 * (df['plus_dm_smooth'] / df['tr_smooth'])
                df['minus_di'] = 100 * (df['minus_dm_smooth'] / df['tr_smooth'])
                
                print(f"   ✅ Directional Indicators calculated")
                
                # Calculate DX and ADX
                df['dx'] = 100 * np.abs(df['plus_di'] - df['minus_di']) / (df['plus_di'] + df['minus_di'])
                df['adx'] = df['dx'].rolling(window=period).mean()
                
                print(f"   ✅ ADX calculated successfully!")
                
                # Check ADX values
                valid_adx = df['adx'].dropna()
                if len(valid_adx) == 0:
                    result['issues'].append("ADX calculation produced no valid values")
                    result['recommendations'].append("Increase historical data period or check calculation logic")
                    print(f"   ❌ No valid ADX values produced")
                else:
                    result['adx_calculated'] = True
                    latest_adx = valid_adx.iloc[-1]
                    avg_adx = valid_adx.mean()
                    
                    print(f"   📈 ADX Statistics:")
                    print(f"      Valid values: {len(valid_adx)}")
                    print(f"      Latest ADX: {latest_adx:.2f}")
                    print(f"      Average ADX: {avg_adx:.2f}")
                    print(f"      Range: {valid_adx.min():.2f} - {valid_adx.max():.2f}")
                    
                    # Check ADX quality
                    if latest_adx < 10:
                        result['issues'].append(f"Very low ADX value: {latest_adx:.2f}")
                        result['recommendations'].append("Market may be in low volatility/ranging phase")
                    elif latest_adx > 50:
                        print(f"   💪 Strong trend detected (ADX: {latest_adx:.2f})")
                    else:
                        print(f"   📊 Normal ADX range (ADX: {latest_adx:.2f})")
            
            except Exception as e:
                result['issues'].append(f"ADX calculation error: {str(e)}")
                result['recommendations'].append("Check calculation logic or data quality")
                print(f"   ❌ ADX calculation failed: {str(e)}")
        
        except Exception as e:
            result['issues'].append(f"General error: {str(e)}")
            result['recommendations'].append("Check MT5 connection and symbol availability")
            print(f"❌ Error analyzing {symbol}: {str(e)}")
        
        results.append(result)
    
    # Summary report
    print("\n" + "=" * 80)
    print("📋 DIAGNOSTIC SUMMARY")
    print("=" * 80)
    
    total_symbols = len(results)
    working_symbols = len([r for r in results if r['adx_calculated']])
    data_available = len([r for r in results if r['data_available']])
    
    print(f"📊 Overall Statistics:")
    print(f"   Total symbols tested: {total_symbols}")
    print(f"   Symbols with data: {data_available}")
    print(f"   Symbols with working ADX: {working_symbols}")
    print(f"   Success rate: {working_symbols/total_symbols*100:.1f}%")
    
    # Common issues
    all_issues = []
    for result in results:
        all_issues.extend(result['issues'])
    
    if all_issues:
        print(f"\n🚨 Common Issues Found:")
        issue_counts = {}
        for issue in all_issues:
            issue_counts[issue] = issue_counts.get(issue, 0) + 1
        
        for issue, count in sorted(issue_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"   • {issue} ({count} symbols)")
    
    # Recommendations
    print(f"\n💡 Recommendations:")
    if working_symbols == 0:
        print(f"   🔧 No ADX data available - Check:")
        print(f"      1. MT5 connection and login")
        print(f"      2. Broker data feed quality")
        print(f"      3. Symbol availability in Market Watch")
        print(f"      4. Historical data permissions")
    elif working_symbols < total_symbols:
        print(f"   ⚠️  Partial ADX availability - Consider:")
        print(f"      1. Using only symbols with working ADX")
        print(f"      2. Implementing ADX-optional trading logic")
        print(f"      3. Switching to different timeframe")
    else:
        print(f"   ✅ All symbols have working ADX - System is healthy!")
    
    mt5.shutdown()
    return results

def create_adx_fix_recommendations():
    """Create specific fix recommendations based on diagnosis"""
    
    print(f"\n🔧 ADX FIX RECOMMENDATIONS:")
    print("-" * 50)
    
    fixes = [
        {
            'issue': 'No historical data',
            'fix': 'Increase bars_needed or check broker connection',
            'code': 'bars_needed = 500  # Increase from 200'
        },
        {
            'issue': 'Insufficient data for calculation',
            'fix': 'Ensure minimum 28 bars for ADX calculation',
            'code': 'if len(df) < 28: return None  # Skip ADX'
        },
        {
            'issue': 'ADX calculation errors',
            'fix': 'Add error handling and fallback logic',
            'code': '''
try:
    # ADX calculation
    df['adx'] = calculate_adx(df)
except Exception as e:
    logger.warning(f"ADX calculation failed: {e}")
    df['adx'] = np.nan  # Set as NaN
'''
        },
        {
            'issue': 'Market conditions (low volatility)',
            'fix': 'Make ADX filter optional in ranging markets',
            'code': '''
# Skip ADX filter if market is ranging
if 'adx' not in df.columns or df['adx'].iloc[-1] < 15:
    logger.info("Skipping ADX filter - low volatility market")
    return signal  # Continue without ADX filter
'''
        }
    ]
    
    for i, fix in enumerate(fixes, 1):
        print(f"{i}. {fix['issue']}:")
        print(f"   Solution: {fix['fix']}")
        print(f"   Code: {fix['code']}")
        print()

if __name__ == "__main__":
    results = diagnose_adx_data()
    create_adx_fix_recommendations()
    
    print(f"\n📝 Next Steps:")
    print(f"1. Review the diagnostic results above")
    print(f"2. Apply recommended fixes for identified issues")
    print(f"3. Test ADX calculation with fixed code")
    print(f"4. Consider making ADX filter optional for problematic symbols")