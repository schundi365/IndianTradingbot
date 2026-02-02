#!/usr/bin/env python3
"""
Fix Dashboard MACD Precision - Complete Configuration Update
"""

import json
import requests
import time

def fix_dashboard_macd():
    """Fix dashboard MACD precision with complete configuration"""
    print("🔧 FIXING DASHBOARD MACD PRECISION")
    print("=" * 50)
    
    # Read the current bot_config.json
    try:
        with open('bot_config.json', 'r') as f:
            bot_config = json.load(f)
        
        print(f"✅ Bot config loaded - MACD: {bot_config.get('macd_min_histogram', 'NOT_FOUND')}")
        
    except Exception as e:
        print(f"❌ Error reading bot_config.json: {e}")
        return False
    
    # Create complete configuration update
    complete_config = {
        # Basic settings
        'symbols': bot_config.get('symbols', ['XAUUSD', 'XAGUSD']),
        'timeframe': bot_config.get('timeframe', 15),
        'risk_percent': bot_config.get('risk_percent', 1.0),
        'reward_ratio': bot_config.get('reward_ratio', 2.0),
        'min_trade_confidence': bot_config.get('min_trade_confidence', 0.5),
        
        # MACD settings - THE MAIN FIX
        'macd_fast': bot_config.get('macd_fast', 12),
        'macd_slow': bot_config.get('macd_slow', 26),
        'macd_signal': bot_config.get('macd_signal', 9),
        'macd_min_histogram': bot_config.get('macd_min_histogram', 0.0005),  # CRITICAL FIX
        
        # RSI settings
        'rsi_period': bot_config.get('rsi_period', 14),
        'rsi_overbought': bot_config.get('rsi_overbought', 70),
        'rsi_oversold': bot_config.get('rsi_oversold', 30),
        
        # Trading hours - 24/7 enabled
        'enable_trading_hours': bot_config.get('enable_trading_hours', False),
        'trading_start_hour': bot_config.get('trading_start_hour', 0),
        'trading_end_hour': bot_config.get('trading_end_hour', 23),
        
        # Volume filter
        'use_volume_filter': bot_config.get('use_volume_filter', True),
        'min_volume_ma': bot_config.get('min_volume_ma', 0.7),
        
        # Trading limits
        'max_daily_trades': bot_config.get('max_daily_trades', 999),
        'max_daily_loss_percent': bot_config.get('max_daily_loss_percent', 5),
        
        # Other indicators
        'use_rsi': bot_config.get('use_rsi', True),
        'use_macd': bot_config.get('use_macd', True),
        'use_adx': bot_config.get('use_adx', True),
        'adx_min_strength': bot_config.get('adx_min_strength', 20),
        
        # ATR settings
        'atr_period': bot_config.get('atr_period', 14),
        'atr_multiplier': bot_config.get('atr_multiplier', 1.5),
        
        # Split orders
        'use_split_orders': bot_config.get('use_split_orders', True),
        'num_positions': bot_config.get('num_positions', 3),
        
        # Trailing
        'enable_trailing_stop': bot_config.get('enable_trailing_stop', True),
        'trail_activation': bot_config.get('trail_activation', 1.0),
        'trail_distance': bot_config.get('trail_distance', 0.8),
        
        # Adaptive risk
        'use_adaptive_risk': bot_config.get('use_adaptive_risk', True),
        'max_risk_multiplier': bot_config.get('max_risk_multiplier', 2.0),
        'min_risk_multiplier': bot_config.get('min_risk_multiplier', 0.5),
        
        # News trading
        'avoid_news_trading': bot_config.get('avoid_news_trading', False),
        'news_buffer_minutes': bot_config.get('news_buffer_minutes', 30)
    }
    
    print(f"🎯 Updating MACD histogram to: {complete_config['macd_min_histogram']}")
    print(f"🎯 Setting 24/7 trading: {not complete_config['enable_trading_hours']}")
    print(f"🎯 Setting max trades: {complete_config['max_daily_trades']}")
    
    # Update dashboard configuration
    try:
        response = requests.post("http://localhost:5000/api/config", 
                               json=complete_config, 
                               timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'success':
                print("✅ Dashboard configuration updated successfully!")
                
                # Verify the update
                time.sleep(2)
                response = requests.get("http://localhost:5000/api/config", timeout=5)
                if response.status_code == 200:
                    updated_config = response.json()
                    macd_value = updated_config.get('macd_min_histogram', 'NOT_FOUND')
                    trading_hours = updated_config.get('enable_trading_hours', True)
                    max_trades = updated_config.get('max_daily_trades', 0)
                    confidence = updated_config.get('min_trade_confidence', 0)
                    
                    print("\n🔍 VERIFICATION RESULTS:")
                    print(f"   MACD histogram: {macd_value} (expected: 0.0005)")
                    print(f"   24/7 trading: {not trading_hours} (expected: True)")
                    print(f"   Max trades: {max_trades} (expected: 999)")
                    print(f"   Confidence: {confidence} (expected: 0.5)")
                    
                    success = (macd_value == 0.0005 and 
                             not trading_hours and 
                             max_trades == 999 and 
                             confidence == 0.5)
                    
                    if success:
                        print("\n🎉 ALL FIXES SUCCESSFUL!")
                        print("   • MACD precision: ✅ 0.0005")
                        print("   • 24/7 trading: ✅ Enabled")
                        print("   • Max trades: ✅ 999")
                        print("   • Confidence: ✅ 0.5")
                    else:
                        print("\n⚠️ Some values still incorrect")
                        
                    return success
                else:
                    print("❌ Failed to verify update")
                    return False
            else:
                print(f"❌ Update failed: {result.get('message', 'Unknown error')}")
                return False
        else:
            print(f"❌ API update failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error updating dashboard: {e}")
        return False

if __name__ == "__main__":
    success = fix_dashboard_macd()
    if success:
        print("\n🎉 MACD PRECISION FIX COMPLETE!")
        print("Dashboard now accepts 0.0005 without rounding")
    else:
        print("\n❌ FIX FAILED - Try restarting dashboard")
        print("Command: python web_dashboard.py")