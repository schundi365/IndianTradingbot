#!/usr/bin/env python3
"""
Sync Dashboard Configuration with Optimized Settings
This script updates the dashboard configuration to use the optimized settings from bot_config.json
"""

import json
import requests
import time
import sys
from pathlib import Path

def load_bot_config():
    """Load the optimized configuration from bot_config.json"""
    config_path = Path("bot_config.json")
    if not config_path.exists():
        print("❌ bot_config.json not found!")
        return None
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    print("✅ Loaded optimized configuration from bot_config.json")
    print(f"   Timeframe: {config.get('timeframe')} (M15)")
    print(f"   MACD Min Histogram: {config.get('macd_min_histogram')}")
    print(f"   Min Volume MA: {config.get('min_volume_ma')}")
    print(f"   Min Trade Confidence: {config.get('min_trade_confidence')}")
    
    return config

def update_dashboard_config(config):
    """Update the dashboard configuration via API"""
    dashboard_url = "http://localhost:5000/api/config"
    
    # Prepare the configuration for dashboard API
    dashboard_config = {
        "symbols": config.get("symbols", ["BTCUSD", "ETHUSD", "LTCUSD", "XRPUSD", "XLMUSD"]),
        "timeframe": config.get("timeframe", 15),  # M15
        "risk_percent": config.get("risk_percent", 1),
        "reward_ratio": config.get("reward_ratio", 1.2),
        "min_trade_confidence": config.get("min_trade_confidence", 0.6),
        "max_daily_loss_percent": config.get("max_daily_loss_percent", 5),
        "fast_ma_period": config.get("fast_ma_period", 10),
        "slow_ma_period": config.get("slow_ma_period", 30),
        "rsi_period": config.get("rsi_period", 14),
        "rsi_overbought": config.get("rsi_overbought", 75),
        "rsi_oversold": config.get("rsi_oversold", 25),
        "macd_fast": config.get("macd_fast", 12),
        "macd_slow": config.get("macd_slow", 26),
        "macd_signal": config.get("macd_signal", 9),
        "macd_min_histogram": config.get("macd_min_histogram", 0.0005),  # Optimized
        "atr_period": config.get("atr_period", 14),
        "atr_multiplier": config.get("atr_multiplier", 2),
        "adx_min_strength": config.get("adx_min_strength", 20),
        "use_rsi": config.get("use_rsi", True),
        "use_macd": config.get("use_macd", True),
        "use_adx": config.get("use_adx", False),
        "use_trend_filter": config.get("use_trend_filter", False),
        "trend_ma_period": config.get("trend_ma_period", 50),
        "enable_trading_hours": config.get("enable_trading_hours", True),
        "trading_start_hour": config.get("trading_start_hour", 0),
        "trading_end_hour": config.get("trading_end_hour", 23),
        "avoid_news_trading": config.get("avoid_news_trading", False),
        "news_buffer_minutes": config.get("news_buffer_minutes", 30),
        "use_split_orders": config.get("use_split_orders", True),
        "num_positions": config.get("num_positions", 3),
        "tp_level_1": config.get("tp_level_1", 1),
        "tp_level_2": config.get("tp_level_2", 1.3),
        "tp_level_3": config.get("tp_level_3", 2),
        "max_lot_per_order": config.get("max_lot_per_order", 1),
        "max_trades_total": config.get("max_trades_total", 50),
        "max_trades_per_symbol": config.get("max_trades_per_symbol", 10),
        "enable_trailing_stop": config.get("enable_trailing_stop", True),
        "trail_activation": config.get("trail_activation", 1),
        "trail_distance": config.get("trail_distance", 0.8),
        "use_adaptive_risk": config.get("use_adaptive_risk", True),
        "max_risk_multiplier": config.get("max_risk_multiplier", 2),
        "min_risk_multiplier": config.get("min_risk_multiplier", 0.5),
        "max_drawdown_percent": config.get("max_drawdown_percent", 15),
        "max_daily_trades": config.get("max_daily_trades", 100),
        "use_volume_filter": config.get("use_volume_filter", True),
        "min_volume_ma": config.get("min_volume_ma", 0.7),  # Optimized
        "volume_ma_period": config.get("volume_ma_period", 20),
        "obv_period": config.get("obv_period", 20),
        "update_interval": config.get("update_interval", 60),
        "analysis_bars": config.get("analysis_bars", 150),
        "use_dynamic_tp": config.get("use_dynamic_tp", True),
        "use_dynamic_sl": config.get("use_dynamic_sl", True),
        "logging_level": config.get("logging_level", "debug")
    }
    
    try:
        print("🔄 Updating dashboard configuration...")
        response = requests.post(dashboard_url, json=dashboard_config, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'success':
                print("✅ Dashboard configuration updated successfully!")
                print("📊 Key optimized settings applied:")
                print(f"   ⏱️  Timeframe: M15 ({dashboard_config['timeframe']})")
                print(f"   📈 MACD Threshold: {dashboard_config['macd_min_histogram']}")
                print(f"   📊 Volume Filter: {dashboard_config['min_volume_ma']}x")
                print(f"   🎯 Min Confidence: {dashboard_config['min_trade_confidence']*100}%")
                return True
            else:
                print(f"❌ Dashboard API error: {result.get('message', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to dashboard. Is the web dashboard running?")
        print("💡 Start the dashboard with: python web_dashboard.py")
        return False
    except Exception as e:
        print(f"❌ Error updating dashboard: {e}")
        return False

def restart_bot():
    """Restart the bot to apply new configuration"""
    dashboard_url = "http://localhost:5000/api/bot"
    
    try:
        print("🔄 Restarting bot to apply new configuration...")
        
        # Stop bot first
        stop_response = requests.post(f"{dashboard_url}/stop", timeout=10)
        if stop_response.status_code == 200:
            print("⏹️  Bot stopped")
            time.sleep(2)  # Wait for clean shutdown
        
        # Start bot with new config
        start_response = requests.post(f"{dashboard_url}/start", timeout=10)
        if start_response.status_code == 200:
            result = start_response.json()
            if result.get('status') == 'success':
                print("✅ Bot restarted with optimized configuration!")
                return True
            else:
                print(f"❌ Failed to start bot: {result.get('message', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP error starting bot: {start_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error restarting bot: {e}")
        return False

def main():
    print("🚀 Synchronizing Dashboard with Optimized Configuration")
    print("=" * 60)
    
    # Load optimized configuration
    config = load_bot_config()
    if not config:
        sys.exit(1)
    
    # Update dashboard configuration
    if not update_dashboard_config(config):
        print("\n❌ Failed to update dashboard configuration")
        sys.exit(1)
    
    # Restart bot to apply changes
    if not restart_bot():
        print("\n⚠️  Configuration updated but bot restart failed")
        print("💡 Please restart the bot manually from the dashboard")
        sys.exit(1)
    
    print("\n🎉 Configuration sync completed successfully!")
    print("📊 The bot is now running with optimized settings:")
    print("   • M15 timeframe for better signal frequency")
    print("   • MACD threshold 0.0005 for better sensitivity")
    print("   • Volume filter 0.7x for better signal quality")
    print("   • Enhanced logging for transparency")
    
    print("\n💡 Monitor the logs to see improved signal generation!")

if __name__ == "__main__":
    main()