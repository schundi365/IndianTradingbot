#!/usr/bin/env python3
"""
Force MACD Configuration Update with Complete Config
"""

import json
import requests
import time

def force_complete_config_update():
    """Force complete configuration update to ensure MACD value is applied"""
    print("🔄 FORCING COMPLETE CONFIGURATION UPDATE")
    print("=" * 50)
    
    try:
        # Read the current bot_config.json
        with open('bot_config.json', 'r') as f:
            bot_config = json.load(f)
        
        print(f"✅ Bot config MACD: {bot_config.get('macd_min_histogram', 'NOT_FOUND')}")
        
        # Create complete configuration for dashboard update
        complete_config = {
            # Basic settings
            'symbols': bot_config.get('symbols', ['XAUUSD', 'XAGUSD']),
            'timeframe': bot_config.get('timeframe', 15),
            'risk_percent': bot_config.get('risk_percent', 1.0),
            'reward_ratio': bot_config.get('reward_ratio', 2.0),
            'min_trade_confidence': bot_config.get('min_trade_confidence', 0.4),
            
            # MACD settings - THE CRITICAL FIX
            'macd_fast': bot_config.get('macd_fast', 12),
            'macd_slow': bot_config.get('macd_slow', 26),
            'macd_signal': bot_config.get('macd_signal', 9),
            'macd_min_histogram': bot_config.get('macd_min_histogram', 0.0003),  # CRITICAL
            
            # RSI settings
            'rsi_period': bot_config.get('rsi_period', 14),
            'rsi_overbought': bot_config.get('rsi_overbought', 75),
            'rsi_oversold': bot_config.get('rsi_oversold', 25),
            
            # Trading hours
            'enable_trading_hours': bot_config.get('enable_trading_hours', False),
            'trading_start_hour': bot_config.get('trading_start_hour', 0),
            'trading_end_hour': bot_config.get('trading_end_hour', 23),
            
            # Volume filter
            'use_volume_filter': bot_config.get('use_volume_filter', False),
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
            'atr_multiplier': bot_config.get('atr_multiplier', 1.8),
            
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
            'news_buffer_minutes': bot_config.get('news_buffer_minutes', 30),
            
            # MA settings
            'fast_ma_period': bot_config.get('fast_ma_period', 5),
            'slow_ma_period': bot_config.get('slow_ma_period', 15)
        }
        
        print(f"🎯 Updating MACD histogram to: {complete_config['macd_min_histogram']}")
        
        # Update dashboard configuration
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
                    
                    print(f"\n🔍 VERIFICATION RESULTS:")
                    print(f"   MACD histogram: {macd_value} (expected: 0.0003)")
                    
                    if macd_value == 0.0003:
                        print("\n🎉 MACD VALUE SUCCESSFULLY UPDATED!")
                        print("   • Dashboard now shows 0.0003")
                        print("   • Configuration is synchronized")
                        print("   • Bot should use new value after restart")
                        return True
                    else:
                        print(f"\n⚠️ MACD still shows {macd_value} instead of 0.0003")
                        return False
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
        print(f"❌ Error updating configuration: {e}")
        return False

def clear_config_cache():
    """Clear any configuration cache"""
    print(f"\n🧹 CLEARING CONFIGURATION CACHE:")
    print("-" * 40)
    
    try:
        # Clear Python cache
        import sys
        if 'src.config_manager' in sys.modules:
            del sys.modules['src.config_manager']
            print("✅ Cleared config_manager from Python cache")
        
        # Force garbage collection
        import gc
        gc.collect()
        print("✅ Forced garbage collection")
        
        return True
        
    except Exception as e:
        print(f"❌ Error clearing cache: {e}")
        return False

if __name__ == "__main__":
    # Clear cache first
    clear_config_cache()
    
    # Force configuration update
    success = force_complete_config_update()
    
    if success:
        print(f"\n🎉 MACD CONFIGURATION UPDATE COMPLETE!")
        print("The dashboard now shows the correct MACD value (0.0003)")
        print("\n📋 NEXT STEPS:")
        print("1. Restart the bot to ensure it uses the new value")
        print("2. Monitor logs for MACD threshold 0.0003")
        print("3. Verify increased signal generation")
    else:
        print(f"\n❌ MACD CONFIGURATION UPDATE FAILED!")
        print("Try restarting the dashboard and bot manually")