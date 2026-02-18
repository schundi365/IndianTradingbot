"""
Web Dashboard for GEM Trading
Modern UI for configuration, monitoring, and analysis
"""

from flask import Flask, render_template, request, jsonify, send_file
import MetaTrader5 as mt5
from datetime import datetime, timedelta
import json
import os
import sys
import threading
import time
import logging
from pathlib import Path
from src.config_manager import get_config_manager, get_config

app = Flask(__name__)

# Determine base directory (works for both script and executable)
if getattr(sys, 'frozen', False):
    # Running as executable
    BASE_DIR = Path(sys.executable).parent
else:
    # Running as script
    BASE_DIR = Path(__file__).parent

# Ensure logs directory exists
LOG_FILE = BASE_DIR / 'trading_bot.log'

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Global state
bot_running = False
bot_thread = None
config_manager = get_config_manager()
current_config = config_manager.get_config()


@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/debug')
def debug():
    """Debug dashboard page"""
    return render_template('dashboard_debug.html')

@app.route('/favicon.ico')
def favicon():
    """Serve favicon to prevent 404 errors"""
    from flask import Response
    # Simple response to prevent 404 errors
    return Response(status=204)  # No Content


@app.route('/api/config', methods=['GET', 'POST'])
def config_api():
    """Get or update configuration"""
    global current_config
    
    if request.method == 'GET':
        return jsonify(current_config)
    
    elif request.method == 'POST':
        # Update configuration
        new_config = request.json
        
        # Validate configuration
        try:
            # Validate risk
            risk = new_config.get('risk_percent', 0)
            if risk < 0.1 or risk > 5:
                return jsonify({'status': 'error', 'message': 'Risk must be between 0.1% and 5%'})
            
            # Validate confidence
            try:
                confidence = float(new_config.get('min_trade_confidence', 0))
                if confidence < 0.2 or confidence > 0.9:
                    return jsonify({'status': 'error', 'message': 'Confidence must be between 20% and 90%'})
            except (ValueError, TypeError):
                return jsonify({'status': 'error', 'message': 'Confidence must be a valid number between 20% and 90%'})
            
            # Validate symbols
            symbols = new_config.get('symbols', [])
            if not symbols or len(symbols) == 0:
                return jsonify({'status': 'error', 'message': 'At least one symbol must be selected'})
            
            # Validate timeframe
            timeframe = new_config.get('timeframe')
            valid_timeframes = [1, 5, 15, 30, 16385, 16388, 16408]
            if timeframe not in valid_timeframes:
                return jsonify({'status': 'error', 'message': 'Invalid timeframe selected'})
            
            # Validate reward ratio
            reward_ratio = new_config.get('reward_ratio', 1.0)
            if reward_ratio < 1.0 or reward_ratio > 5.0:
                return jsonify({'status': 'error', 'message': 'Reward ratio must be between 1.0 and 5.0'})
            
            # Validate max daily loss percentage
            try:
                max_daily_loss_percent = float(new_config.get('max_daily_loss_percent', 0))
                if max_daily_loss_percent < 1 or max_daily_loss_percent > 20:
                    return jsonify({'status': 'error', 'message': 'Max daily loss must be between 1% and 20% of equity'})
            except (ValueError, TypeError):
                return jsonify({'status': 'error', 'message': 'Max daily loss must be a valid number between 1% and 20%'})
            
            # Validate indicator periods
            fast_ma = new_config.get('fast_ma_period', 20)
            slow_ma = new_config.get('slow_ma_period', 50)
            if fast_ma >= slow_ma:
                return jsonify({'status': 'error', 'message': 'Fast MA must be less than Slow MA'})
            
            # Validate RSI
            rsi_overbought = new_config.get('rsi_overbought', 75)
            rsi_oversold = new_config.get('rsi_oversold', 25)
            if rsi_oversold >= rsi_overbought:
                return jsonify({'status': 'error', 'message': 'RSI oversold must be less than overbought'})
            
            # Validate MACD
            macd_fast = new_config.get('macd_fast', 12)
            macd_slow = new_config.get('macd_slow', 26)
            if macd_fast >= macd_slow:
                return jsonify({'status': 'error', 'message': 'MACD fast must be less than slow'})
            
            # Validate trading hours
            if new_config.get('enable_trading_hours', False):
                start_hour = new_config.get('trading_start_hour', 0)
                end_hour = new_config.get('trading_end_hour', 23)
                if start_hour < 0 or start_hour > 23 or end_hour < 0 or end_hour > 23:
                    return jsonify({'status': 'error', 'message': 'Trading hours must be between 0 and 23'})
            
            # Validate hour filter
            if 'dead_hours' in new_config:
                dead_hours = new_config.get('dead_hours', [])
                if not isinstance(dead_hours, list):
                    return jsonify({'status': 'error', 'message': 'Dead hours must be a list'})
                for hour in dead_hours:
                    if not isinstance(hour, int) or hour < 0 or hour > 23:
                        return jsonify({'status': 'error', 'message': 'Dead hours must be integers between 0 and 23'})
            
            if 'golden_hours' in new_config:
                golden_hours = new_config.get('golden_hours', [])
                if not isinstance(golden_hours, list):
                    return jsonify({'status': 'error', 'message': 'Golden hours must be a list'})
                for hour in golden_hours:
                    if not isinstance(hour, int) or hour < 0 or hour > 23:
                        return jsonify({'status': 'error', 'message': 'Golden hours must be integers between 0 and 23'})
            
            if 'roc_threshold' in new_config:
                try:
                    roc_threshold = float(new_config.get('roc_threshold', 0.15))
                    if roc_threshold < 0.05 or roc_threshold > 1.0:
                        return jsonify({'status': 'error', 'message': 'ROC threshold must be between 0.05 and 1.0'})
                except (ValueError, TypeError):
                    return jsonify({'status': 'error', 'message': 'ROC threshold must be a valid number'})
            
            # Validate position management
            num_positions = new_config.get('num_positions', 1)
            if num_positions < 1 or num_positions > 5:
                return jsonify({'status': 'error', 'message': 'Number of positions must be between 1 and 5'})
            
            # Validate TP levels
            tp1 = new_config.get('tp_level_1', 1.0)
            tp2 = new_config.get('tp_level_2', 2.0)
            tp3 = new_config.get('tp_level_3', 3.0)
            if not (tp1 < tp2 < tp3):
                return jsonify({'status': 'error', 'message': 'TP levels must be in ascending order'})
            
            # Validate risk multipliers
            max_risk_mult = new_config.get('max_risk_multiplier', 1.5)
            min_risk_mult = new_config.get('min_risk_multiplier', 0.5)
            if min_risk_mult >= max_risk_mult:
                return jsonify({'status': 'error', 'message': 'Min risk multiplier must be less than max'})
            
            # Validate max lot per order
            max_lot_per_order = new_config.get('max_lot_per_order', 0.5)
            if max_lot_per_order < 0.01 or max_lot_per_order > 10:
                return jsonify({'status': 'error', 'message': 'Max lot per order must be between 0.01 and 10'})
            
            # Validate analysis bars
            analysis_bars = new_config.get('analysis_bars', 200)
            if analysis_bars < 50 or analysis_bars > 1000:
                return jsonify({'status': 'error', 'message': 'Analysis bars must be between 50 and 1000'})
            
            # Validate trailing stop parameters
            if 'trail_activation' in new_config:
                trail_activation = new_config.get('trail_activation', 1.0)
                if trail_activation < 0.1 or trail_activation > 5.0:
                    return jsonify({'status': 'error', 'message': 'Trail activation must be between 0.1 and 5.0 ATR'})
            
            if 'trail_distance' in new_config:
                trail_distance = new_config.get('trail_distance', 0.8)
                if trail_distance < 0.1 or trail_distance > 3.0:
                    return jsonify({'status': 'error', 'message': 'Trail distance must be between 0.1 and 3.0 ATR'})
            
            # Validate time-based exit parameters
            if 'max_hold_minutes' in new_config:
                max_hold_minutes = new_config.get('max_hold_minutes', 45)
                if max_hold_minutes < 5 or max_hold_minutes > 480:
                    return jsonify({'status': 'error', 'message': 'Max hold time must be between 5 and 480 minutes (8 hours)'})
            
            # Validate breakeven threshold
            if 'breakeven_atr_threshold' in new_config:
                try:
                    be_threshold = float(new_config.get('breakeven_atr_threshold', 0.3))
                    if be_threshold < 0.1 or be_threshold > 2.0:
                        return jsonify({'status': 'error', 'message': 'Breakeven ATR threshold must be between 0.1 and 2.0'})
                except (ValueError, TypeError):
                    return jsonify({'status': 'error', 'message': 'Breakeven ATR threshold must be a valid number'})
            
            # Validate volume filter settings
            if 'min_volume_ma' in new_config:
                min_vol_ma = new_config.get('min_volume_ma', 0.7)
                if min_vol_ma < 0.5 or min_vol_ma > 2.0:
                    return jsonify({'status': 'error', 'message': 'Min volume multiplier must be between 0.5 and 2.0'})
            
            if 'volume_ma_period' in new_config:
                vol_ma_period = new_config.get('volume_ma_period', 20)
                if vol_ma_period < 10 or vol_ma_period > 50:
                    return jsonify({'status': 'error', 'message': 'Volume MA period must be between 10 and 50'})
            
            if 'obv_period' in new_config:
                obv_period = new_config.get('obv_period', 20)
                if obv_period < 10 or obv_period > 50:
                    return jsonify({'status': 'error', 'message': 'OBV period must be between 10 and 50'})
            
            # Validate trend detection settings
            if 'trend_detection_sensitivity' in new_config:
                sensitivity = new_config.get('trend_detection_sensitivity', 5)
                if sensitivity < 1 or sensitivity > 10:
                    return jsonify({'status': 'error', 'message': 'Trend detection sensitivity must be between 1 and 10'})
            
            if 'min_trend_confidence' in new_config:
                try:
                    trend_confidence = float(new_config.get('min_trend_confidence', 0.6))
                    if trend_confidence < 0.2 or trend_confidence > 0.9:
                        return jsonify({'status': 'error', 'message': 'Min trend confidence must be between 20% and 90%'})
                except (ValueError, TypeError):
                    return jsonify({'status': 'error', 'message': 'Min trend confidence must be a valid number between 20% and 90%'})
            
            # Validate EMA settings
            if 'ema_fast_period' in new_config and 'ema_slow_period' in new_config:
                ema_fast = new_config.get('ema_fast_period', 20)
                ema_slow = new_config.get('ema_slow_period', 50)
                if ema_fast >= ema_slow:
                    return jsonify({'status': 'error', 'message': 'Fast EMA period must be less than Slow EMA period'})
                if ema_fast < 5 or ema_fast > 50:
                    return jsonify({'status': 'error', 'message': 'Fast EMA period must be between 5 and 50'})
                if ema_slow < 20 or ema_slow > 100:
                    return jsonify({'status': 'error', 'message': 'Slow EMA period must be between 20 and 100'})
            
            # Validate Aroon settings
            if 'aroon_period' in new_config:
                aroon_period = new_config.get('aroon_period', 25)
                if aroon_period < 14 or aroon_period > 50:
                    return jsonify({'status': 'error', 'message': 'Aroon period must be between 14 and 50'})
            
            if 'aroon_threshold' in new_config:
                aroon_threshold = new_config.get('aroon_threshold', 70)
                if aroon_threshold < 50 or aroon_threshold > 90:
                    return jsonify({'status': 'error', 'message': 'Aroon threshold must be between 50 and 90'})
            
            # Validate market structure settings
            if 'min_swing_strength' in new_config:
                swing_strength = new_config.get('min_swing_strength', 3)
                if swing_strength < 2 or swing_strength > 10:
                    return jsonify({'status': 'error', 'message': 'Min swing strength must be between 2 and 10'})
            
            if 'structure_break_threshold' in new_config:
                try:
                    break_threshold = float(new_config.get('structure_break_threshold', 0.001))
                    if break_threshold < 0.0005 or break_threshold > 0.005:
                        return jsonify({'status': 'error', 'message': 'Structure break threshold must be between 0.05% and 0.5%'})
                except (ValueError, TypeError):
                    return jsonify({'status': 'error', 'message': 'Structure break threshold must be a valid number'})
            
            # Validate divergence settings
            if 'divergence_lookback' in new_config:
                div_lookback = new_config.get('divergence_lookback', 50)
                if div_lookback < 20 or div_lookback > 100:
                    return jsonify({'status': 'error', 'message': 'Divergence lookback must be between 20 and 100'})
            
            if 'min_divergence_strength' in new_config:
                try:
                    div_strength = float(new_config.get('min_divergence_strength', 0.3))
                    if div_strength < 0.1 or div_strength > 0.8:
                        return jsonify({'status': 'error', 'message': 'Min divergence strength must be between 0.1 and 0.8'})
                except (ValueError, TypeError):
                    return jsonify({'status': 'error', 'message': 'Min divergence strength must be a valid number'})
            
            # Validate trendline settings
            if 'max_trendlines' in new_config:
                max_trendlines = new_config.get('max_trendlines', 5)
                if max_trendlines < 2 or max_trendlines > 10:
                    return jsonify({'status': 'error', 'message': 'Max trendlines must be between 2 and 10'})
            
            if 'min_trendline_touches' in new_config:
                min_touches = new_config.get('min_trendline_touches', 2)
                if min_touches < 2 or min_touches > 5:
                    return jsonify({'status': 'error', 'message': 'Min trendline touches must be between 2 and 5'})
            
            if 'trendline_angle_min' in new_config and 'trendline_angle_max' in new_config:
                angle_min = new_config.get('trendline_angle_min', 10)
                angle_max = new_config.get('trendline_angle_max', 80)
                if angle_min >= angle_max:
                    return jsonify({'status': 'error', 'message': 'Min trendline angle must be less than max angle'})
                if angle_min < 5 or angle_min > 30:
                    return jsonify({'status': 'error', 'message': 'Min trendline angle must be between 5 and 30 degrees'})
                if angle_max < 60 or angle_max > 85:
                    return jsonify({'status': 'error', 'message': 'Max trendline angle must be between 60 and 85 degrees'})
            
            # Validate multi-timeframe settings
            if 'mtf_weight' in new_config:
                try:
                    mtf_weight = float(new_config.get('mtf_weight', 0.3))
                    if mtf_weight < 0.1 or mtf_weight > 0.5:
                        return jsonify({'status': 'error', 'message': 'MTF weight must be between 0.1 and 0.5'})
                except (ValueError, TypeError):
                    return jsonify({'status': 'error', 'message': 'MTF weight must be a valid number'})
            
            if 'mtf_alignment_threshold' in new_config:
                try:
                    mtf_threshold = float(new_config.get('mtf_alignment_threshold', 0.6))
                    if mtf_threshold < 0.3 or mtf_threshold > 0.9:
                        return jsonify({'status': 'error', 'message': 'MTF alignment threshold must be between 0.3 and 0.9'})
                except (ValueError, TypeError):
                    return jsonify({'status': 'error', 'message': 'MTF alignment threshold must be a valid number'})
            
            if 'mtf_contradiction_penalty' in new_config:
                try:
                    mtf_penalty = float(new_config.get('mtf_contradiction_penalty', 0.4))
                    if mtf_penalty < 0.1 or mtf_penalty > 0.8:
                        return jsonify({'status': 'error', 'message': 'MTF contradiction penalty must be between 0.1 and 0.8'})
                except (ValueError, TypeError):
                    return jsonify({'status': 'error', 'message': 'MTF contradiction penalty must be a valid number'})
            
            # Validate volume pattern settings
            if 'volume_spike_threshold' in new_config:
                try:
                    vol_spike = float(new_config.get('volume_spike_threshold', 1.5))
                    if vol_spike < 1.2 or vol_spike > 3.0:
                        return jsonify({'status': 'error', 'message': 'Volume spike threshold must be between 1.2 and 3.0'})
                except (ValueError, TypeError):
                    return jsonify({'status': 'error', 'message': 'Volume spike threshold must be a valid number'})
            
            # Validate MACD histogram threshold
            if 'macd_min_histogram' in new_config:
                try:
                    macd_threshold = float(new_config.get('macd_min_histogram', 0.0005))
                    if macd_threshold < 0.0001 or macd_threshold > 0.01:
                        return jsonify({'status': 'error', 'message': 'MACD min histogram must be between 0.0001 and 0.01'})
                except (ValueError, TypeError):
                    return jsonify({'status': 'error', 'message': 'MACD min histogram must be a valid number between 0.0001 and 0.01'})
            
            # Validate logging level
            if 'logging_level' in new_config:
                logging_level = new_config.get('logging_level', 'standard')
                valid_levels = ['minimal', 'standard', 'detailed', 'debug']
                if logging_level not in valid_levels:
                    return jsonify({'status': 'error', 'message': 'Invalid logging level'})
            
            # Validate update interval
            if 'update_interval' in new_config:
                update_interval = new_config.get('update_interval', 60)
                if update_interval < 30 or update_interval > 300:
                    return jsonify({'status': 'error', 'message': 'Update interval must be between 30 and 300 seconds'})
            
            # Validate pip-based TP/SL settings
            if 'use_pip_based_sl' in new_config and 'use_pip_based_tp' in new_config:
                use_pip_sl = new_config.get('use_pip_based_sl', False)
                use_pip_tp = new_config.get('use_pip_based_tp', False)
                
                # CRITICAL: Both must use the same method
                if use_pip_sl != use_pip_tp:
                    return jsonify({
                        'status': 'error', 
                        'message': 'TP and SL must use the same calculation method! Mixing methods causes SL > TP (negative risk/reward).'
                    })
                
                # Validate pip values if pip-based is enabled
                if use_pip_sl:
                    sl_pips = new_config.get('sl_pips', 50)
                    if sl_pips < 10 or sl_pips > 500:
                        return jsonify({'status': 'error', 'message': 'SL pips must be between 10 and 500'})
                
                if use_pip_tp:
                    tp_pips = new_config.get('tp_pips', 100)
                    if tp_pips < 20 or tp_pips > 1000:
                        return jsonify({'status': 'error', 'message': 'TP pips must be between 20 and 1000'})
                    
                    # Validate that TP base is greater than SL
                    if use_pip_sl:
                        sl_pips = new_config.get('sl_pips', 50)
                        if tp_pips <= sl_pips:
                            return jsonify({
                                'status': 'error', 
                                'message': f'TP base ({tp_pips} pips) must be greater than SL ({sl_pips} pips)'
                            })
            
            # Update configuration using config manager
            if config_manager.update_config(new_config):
                # Reload current_config from config manager
                current_config = config_manager.get_config()
                
                logger.info(f"Configuration updated: Risk={risk}%, Confidence={confidence*100}%, Timeframe={timeframe}")
                logger.info(f"Configuration saved to: {config_manager.config_file}")
                
                # Apply logging level change immediately if bot is running
                if 'logging_level' in new_config and bot_running:
                    apply_logging_level(new_config['logging_level'])
                
                # If bot is running, it needs to be restarted to apply new config
                restart_needed = bot_running
                
                return jsonify({
                    'status': 'success', 
                    'message': 'Configuration saved successfully. Restart bot to apply changes.' if restart_needed else 'Configuration saved successfully',
                    'config_file': str(config_manager.config_file),
                    'restart_needed': restart_needed
                })
            else:
                return jsonify({'status': 'error', 'message': 'Failed to save configuration'})
        
        except Exception as e:
            logger.error(f"Failed to update configuration: {str(e)}")
            return jsonify({'status': 'error', 'message': f'Failed to update: {str(e)}'})


def apply_logging_level(level):
    """Apply logging level change to the running bot and trend detection system"""
    try:
        if level == 'minimal':
            logging.getLogger().setLevel(logging.WARNING)
            logger.info("🔧 Logging level changed to MINIMAL (warnings and errors only)")
        elif level == 'standard':
            logging.getLogger().setLevel(logging.INFO)
            logger.info("🔧 Logging level changed to STANDARD (normal operation)")
        elif level == 'detailed':
            logging.getLogger().setLevel(logging.INFO)
            logger.info("🔧 Logging level changed to DETAILED (full indicator calculations)")
        elif level == 'debug':
            logging.getLogger().setLevel(logging.DEBUG)
            logger.info("🔧 Logging level changed to DEBUG (everything)")
        
        # Apply logging level to trend detection system if available
        try:
            # Import and update trend detection logging
            from src.trend_detection_engine import trend_logger
            trend_logger.set_logging_level(level)
            logger.info(f"🔍 Trend detection logging level updated to: {level}")
        except ImportError:
            logger.debug("Trend detection system not available for logging level update")
        except Exception as e:
            logger.warning(f"Failed to update trend detection logging level: {e}")
        
        # Store the level for the bot to use
        current_config['logging_level'] = level
        
    except Exception as e:
        logger.error(f"Failed to apply logging level: {e}")


@app.route('/api/logging/level', methods=['POST'])
def set_logging_level():
    """Change logging level without restarting bot"""
    try:
        data = request.json
        level = data.get('level', 'standard')
        
        valid_levels = ['minimal', 'standard', 'detailed', 'debug']
        if level not in valid_levels:
            return jsonify({'status': 'error', 'message': 'Invalid logging level'})
        
        apply_logging_level(level)
        
        return jsonify({
            'status': 'success',
            'message': f'Logging level changed to {level.upper()}',
            'level': level
        })
        
    except Exception as e:
        logger.error(f"Failed to change logging level: {e}")
        return jsonify({'status': 'error', 'message': str(e)})


@app.route('/api/bot/start', methods=['POST'])
def start_bot():
    """Start the trading bot"""
    global bot_running, bot_thread, current_config
    
    if bot_running:
        return jsonify({'status': 'error', 'message': 'Bot already running'})
    
    # CRITICAL: Reload configuration from config manager before starting
    current_config = config_manager.get_config()
    logger.info("=" * 80)
    logger.info("STARTING BOT WITH CONFIGURATION:")
    logger.info(f"Config file: {config_manager.config_file}")
    logger.info(f"Symbols: {current_config.get('symbols')}")
    logger.info(f"Timeframe: {current_config.get('timeframe')}")
    logger.info(f"Risk: {current_config.get('risk_percent')}%")
    logger.info(f"Min Confidence: {current_config.get('min_trade_confidence', 0.6)*100}%")
    logger.info(f"Use Volume Filter: {current_config.get('use_volume_filter', True)}")
    logger.info("=" * 80)
    
    # Test MT5 connection first
    if not mt5.initialize():
        logger.error("Failed to start bot: MT5 not connected")
        return jsonify({'status': 'error', 'message': 'MT5 not connected. Please check MT5 is running.'})
    
    account_info = mt5.account_info()
    if account_info is None:
        mt5.shutdown()
        logger.error("Failed to start bot: No account info")
        return jsonify({'status': 'error', 'message': 'Cannot access MT5 account. Check login.'})
    
    mt5.shutdown()
    
    bot_running = True
    bot_thread = threading.Thread(target=run_bot_background, daemon=True)  # Make daemon thread
    bot_thread.start()
    
    logger.info("Trading bot started successfully")
    return jsonify({'status': 'success', 'message': 'Bot started successfully'})


@app.route('/api/bot/stop', methods=['POST'])
def stop_bot():
    """Stop the trading bot"""
    global bot_running, bot_thread
    
    if not bot_running:
        return jsonify({'status': 'warning', 'message': 'Bot is not running'})
    
    logger.info("=" * 80)
    logger.info("STOPPING TRADING BOT...")
    logger.info("=" * 80)
    
    bot_running = False
    
    # Wait for thread to finish (max 10 seconds)
    if bot_thread and bot_thread.is_alive():
        logger.info("Waiting for bot thread to stop...")
        bot_thread.join(timeout=10)
        if bot_thread.is_alive():
            logger.warning("Bot thread did not stop gracefully within 10 seconds")
        else:
            logger.info("Bot thread stopped successfully")
    
    # Force MT5 shutdown to ensure clean state
    try:
        mt5.shutdown()
        logger.info("MT5 connection closed")
    except Exception as e:
        logger.warning(f"Error closing MT5: {e}")
    
    logger.info("=" * 80)
    logger.info("TRADING BOT STOPPED")
    logger.info("=" * 80)
    
    return jsonify({'status': 'success', 'message': 'Bot stopped successfully'})


@app.route('/api/bot/status', methods=['GET'])
def bot_status():
    """Get bot status"""
    try:
        # Check if bot is running
        global bot_running
        
        # Don't auto-detect running status from log file
        # Only trust the bot_running flag set by start/stop buttons
        
        if not mt5.initialize():
            logger.warning("MT5 not connected for status check")
            return jsonify({
                'running': bot_running,
                'balance': 0,
                'equity': 0,
                'profit': 0,
                'profit_today': 0,
                'profit_mtd': 0,
                'profit_ytd': 0,
                'open_positions': 0,
                'margin_free': 0,
                'currency': 'USD',
                'error': 'MT5 not connected'
            })
        
        account_info = mt5.account_info()
        positions = mt5.positions_get()
        
        # Get account currency
        currency = account_info.currency if account_info else 'USD'
        
        # Calculate profit for different periods
        now = datetime.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        year_start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Get deals for different periods
        today_deals = mt5.history_deals_get(today_start, now)
        month_deals = mt5.history_deals_get(month_start, now)
        year_deals = mt5.history_deals_get(year_start, now)
        
        # Calculate profits
        profit_today = sum([d.profit for d in today_deals if d.entry == mt5.DEAL_ENTRY_OUT]) if today_deals else 0
        profit_mtd = sum([d.profit for d in month_deals if d.entry == mt5.DEAL_ENTRY_OUT]) if month_deals else 0
        profit_ytd = sum([d.profit for d in year_deals if d.entry == mt5.DEAL_ENTRY_OUT]) if year_deals else 0
        
        status = {
            'running': bot_running,
            'balance': account_info.balance if account_info else 0,
            'equity': account_info.equity if account_info else 0,
            'profit': account_info.profit if account_info else 0,
            'profit_today': profit_today,
            'profit_mtd': profit_mtd,
            'profit_ytd': profit_ytd,
            'open_positions': len(positions) if positions else 0,
            'margin_free': account_info.margin_free if account_info else 0,
            'currency': currency
        }
        
        mt5.shutdown()
        return jsonify(status)
    
    except Exception as e:
        logger.error(f"Error getting bot status: {str(e)}")
        mt5.shutdown()
        return jsonify({
            'running': bot_running,
            'balance': 0,
            'equity': 0,
            'profit': 0,
            'profit_today': 0,
            'profit_mtd': 0,
            'profit_ytd': 0,
            'open_positions': 0,
            'margin_free': 0,
            'currency': 'USD',
            'error': str(e)
        })


@app.route('/api/mt5/test', methods=['GET'])
def test_mt5():
    """Test MT5 connection"""
    if not mt5.initialize():
        return jsonify({
            'connected': False,
            'error': 'Failed to initialize MT5. Make sure MT5 is running.'
        })
    
    account_info = mt5.account_info()
    
    if account_info is None:
        mt5.shutdown()
        return jsonify({
            'connected': False,
            'error': 'No account info available. Check MT5 login.'
        })
    
    result = {
        'connected': True,
        'account_name': account_info.name,
        'account_number': account_info.login,
        'server': account_info.server,
        'balance': account_info.balance,
        'currency': account_info.currency,
        'leverage': account_info.leverage
    }
    
    mt5.shutdown()
    return jsonify(result)


@app.route('/api/trades/history', methods=['GET'])
def trades_history():
    """Get trade history"""
    days = int(request.args.get('days', 7))
    
    if not mt5.initialize():
        return jsonify({'status': 'error', 'message': 'MT5 not connected'})
    
    from_date = datetime.now() - timedelta(days=days)
    deals = mt5.history_deals_get(from_date, datetime.now())
    
    if deals is None or len(deals) == 0:
        mt5.shutdown()
        return jsonify({'trades': []})
    
    # Group deals by position to match entry and exit
    positions_dict = {}
    for deal in deals:
        position_id = deal.position_id
        if position_id not in positions_dict:
            positions_dict[position_id] = {'entry': None, 'exit': None}
        
        if deal.entry == mt5.DEAL_ENTRY_IN:
            positions_dict[position_id]['entry'] = deal
        elif deal.entry == mt5.DEAL_ENTRY_OUT:
            positions_dict[position_id]['exit'] = deal
    
    # Convert to list of completed trades
    trades_list = []
    for position_id, deals_pair in positions_dict.items():
        entry_deal = deals_pair['entry']
        exit_deal = deals_pair['exit']
        
        # Only include completed trades (have both entry and exit)
        if entry_deal and exit_deal:
            symbol = exit_deal.symbol
            price_diff = abs(exit_deal.price - entry_deal.price)
            
            # Calculate pips based on instrument type
            if 'XAU' in symbol or 'GOLD' in symbol:
                # Gold: 1 pip = 0.01
                pips = price_diff * 100
            elif 'XAG' in symbol or 'SILVER' in symbol:
                # Silver: 1 pip = 0.001
                pips = price_diff * 1000
            elif 'BTC' in symbol:
                # Bitcoin: 1 pip = 1.0 (whole dollar moves)
                pips = price_diff
            elif 'ETH' in symbol:
                # Ethereum: 1 pip = 0.1
                pips = price_diff * 10
            elif any(crypto in symbol for crypto in ['LTC', 'XRP', 'BCH', 'ADA', 'DOT', 'LINK', 'XLM', 'UNI', 'SOL', 'MATIC', 'AVAX']):
                # Major altcoins: 1 pip = 0.01
                pips = price_diff * 100
            elif any(crypto in symbol for crypto in ['DOGE', 'SHIB']):
                # Meme coins: 1 pip = 0.0001 (smaller moves)
                pips = price_diff * 10000
            elif 'JPY' in symbol:
                # JPY pairs: 1 pip = 0.01
                pips = price_diff * 100
            else:
                # Standard forex pairs: 1 pip = 0.0001
                pips = price_diff * 10000
            
            trades_list.append({
                'time': datetime.fromtimestamp(exit_deal.time).strftime('%Y-%m-%d %H:%M:%S'),
                'timestamp': exit_deal.time,
                'symbol': symbol,
                'type': 'BUY' if entry_deal.type == mt5.ORDER_TYPE_BUY else 'SELL',
                'volume': exit_deal.volume,
                'price_open': entry_deal.price,  # Entry price
                'price_close': exit_deal.price,  # Exit price
                'profit': exit_deal.profit,
                'commission': exit_deal.commission,
                'pips': pips,
            })
    
    # Sort by timestamp descending (latest first)
    trades_list.sort(key=lambda x: x['timestamp'], reverse=True)
    
    mt5.shutdown()
    return jsonify({'trades': trades_list})


@app.route('/api/trades/open', methods=['GET'])
def trades_open():
    """Get open positions"""
    if not mt5.initialize():
        return jsonify({'status': 'error', 'message': 'MT5 not connected'})
    
    positions = mt5.positions_get()
    
    if positions is None or len(positions) == 0:
        mt5.shutdown()
        return jsonify({'positions': []})
    
    positions_list = []
    for pos in positions:
        positions_list.append({
            'ticket': pos.ticket,
            'time': datetime.fromtimestamp(pos.time).strftime('%Y-%m-%d %H:%M:%S'),
            'symbol': pos.symbol,
            'type': 'BUY' if pos.type == mt5.ORDER_TYPE_BUY else 'SELL',
            'volume': pos.volume,
            'price_open': pos.price_open,
            'price_current': pos.price_current,
            'sl': pos.sl,
            'tp': pos.tp,
            'profit': pos.profit,
        })
    
    mt5.shutdown()
    return jsonify({'positions': positions_list})


@app.route('/api/trades/close/<int:ticket>', methods=['POST'])
def close_position(ticket):
    """Close a specific position by ticket number"""
    if not mt5.initialize():
        return jsonify({'status': 'error', 'message': 'MT5 not connected'})
    
    try:
        # Get the position
        positions = mt5.positions_get(ticket=ticket)
        
        if positions is None or len(positions) == 0:
            mt5.shutdown()
            return jsonify({'status': 'error', 'message': f'Position {ticket} not found'})
        
        position = positions[0]
        
        # Determine order type for closing (opposite of position type)
        if position.type == mt5.ORDER_TYPE_BUY:
            order_type = mt5.ORDER_TYPE_SELL
            price = mt5.symbol_info_tick(position.symbol).bid
        else:
            order_type = mt5.ORDER_TYPE_BUY
            price = mt5.symbol_info_tick(position.symbol).ask
        
        # Create close request
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": position.symbol,
            "volume": position.volume,
            "type": order_type,
            "position": ticket,
            "price": price,
            "deviation": 20,
            "magic": current_config.get('magic_number', 123456),
            "comment": "Closed from dashboard",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        # Send close order
        result = mt5.order_send(request)
        
        if result is None:
            mt5.shutdown()
            return jsonify({'status': 'error', 'message': 'Failed to send close order'})
        
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            error_msg = f'Close order failed: {result.retcode} - {result.comment}'
            logger.error(error_msg)
            mt5.shutdown()
            return jsonify({'status': 'error', 'message': error_msg})
        
        logger.info(f"Position {ticket} closed successfully from dashboard. Profit: {position.profit}")
        mt5.shutdown()
        
        return jsonify({
            'status': 'success',
            'message': f'Position {ticket} closed successfully',
            'profit': position.profit,
            'symbol': position.symbol
        })
    
    except Exception as e:
        logger.error(f"Error closing position {ticket}: {str(e)}")
        mt5.shutdown()
        return jsonify({'status': 'error', 'message': str(e)})


@app.route('/api/trend-detection/status', methods=['GET'])
def trend_detection_status():
    """Get current trend detection analysis status and signals"""
    try:
        if not mt5.initialize():
            return jsonify({'status': 'error', 'message': 'MT5 not connected'})
        
        # Get current configuration
        config = config_manager.get_config()
        
        # Check if trend detection is enabled
        if not config.get('use_trend_detection', False):
            mt5.shutdown()
            return jsonify({
                'status': 'success',
                'enabled': False,
                'message': 'Trend detection is disabled in configuration'
            })
        
        # Get symbols from config
        symbols = config.get('symbols', ['XAUUSD'])
        timeframe = config.get('timeframe', 30)
        
        # Initialize trend detection engine
        try:
            from src.trend_detection_engine import TrendDetectionEngine
            trend_engine = TrendDetectionEngine(config)
        except ImportError as e:
            mt5.shutdown()
            return jsonify({
                'status': 'error',
                'message': f'Trend detection engine not available: {str(e)}'
            })
        
        # Analyze each symbol
        symbol_analyses = {}
        
        for symbol in symbols[:3]:  # Limit to first 3 symbols for performance
            try:
                # Get market data
                import pandas as pd
                from datetime import datetime, timedelta
                
                # Map timeframe to MT5 constant
                timeframe_map = {
                    1: mt5.TIMEFRAME_M1,
                    5: mt5.TIMEFRAME_M5,
                    15: mt5.TIMEFRAME_M15,
                    30: mt5.TIMEFRAME_M30,
                    16385: mt5.TIMEFRAME_H1,
                    16388: mt5.TIMEFRAME_H4,
                    16408: mt5.TIMEFRAME_D1
                }
                
                mt5_timeframe = timeframe_map.get(timeframe, mt5.TIMEFRAME_M30)
                
                # Get historical data
                bars = 200  # Sufficient for analysis
                rates = mt5.copy_rates_from_pos(symbol, mt5_timeframe, 0, bars)
                
                if rates is None or len(rates) < 50:
                    symbol_analyses[symbol] = {
                        'status': 'error',
                        'message': 'Insufficient data'
                    }
                    continue
                
                # Convert to DataFrame
                df = pd.DataFrame(rates)
                df['time'] = pd.to_datetime(df['time'], unit='s')
                df.set_index('time', inplace=True)
                
                # Add basic indicators needed for trend detection
                # Calculate EMAs
                df['ema_20'] = df['close'].ewm(span=20).mean()
                df['ema_50'] = df['close'].ewm(span=50).mean()
                
                # Calculate RSI
                delta = df['close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                df['rsi'] = 100 - (100 / (1 + rs))
                
                # Calculate MACD
                exp1 = df['close'].ewm(span=12).mean()
                exp2 = df['close'].ewm(span=26).mean()
                df['macd'] = exp1 - exp2
                df['macd_signal'] = df['macd'].ewm(span=9).mean()
                df['macd_histogram'] = df['macd'] - df['macd_signal']
                
                # Perform trend analysis
                analysis_result = trend_engine.analyze_trend_change(df, symbol)
                
                # Extract key information
                current_price = df['close'].iloc[-1]
                
                # Summarize signals
                signals_summary = []
                for signal in analysis_result.signals:
                    signals_summary.append({
                        'type': signal.signal_type,
                        'strength': round(signal.strength, 3),
                        'confidence': round(signal.confidence, 3),
                        'source': signal.source,
                        'price_level': round(signal.price_level, 5),
                        'factors': signal.supporting_factors
                    })
                
                # Market structure info
                structure_info = None
                if analysis_result.market_structure:
                    structure_info = {
                        'break_type': analysis_result.market_structure.break_type,
                        'break_level': round(analysis_result.market_structure.break_level, 5),
                        'volume_confirmed': analysis_result.market_structure.volume_confirmation,
                        'strength': round(analysis_result.market_structure.strength, 3),
                        'confirmed': analysis_result.market_structure.confirmed
                    }
                
                # Divergences info
                divergences_info = []
                for div in analysis_result.divergences:
                    divergences_info.append({
                        'type': div.divergence_type,
                        'indicator': div.indicator,
                        'strength': round(div.strength, 3),
                        'validated': div.validated
                    })
                
                # Aroon signal info
                aroon_info = None
                if analysis_result.aroon_signal:
                    aroon_info = {
                        'aroon_up': round(analysis_result.aroon_signal.aroon_up, 2),
                        'aroon_down': round(analysis_result.aroon_signal.aroon_down, 2),
                        'oscillator': round(analysis_result.aroon_signal.oscillator, 2),
                        'signal_type': analysis_result.aroon_signal.signal_type,
                        'trend_strength': round(analysis_result.aroon_signal.trend_strength, 3)
                    }
                
                # EMA signal info
                ema_info = None
                if analysis_result.ema_signal:
                    ema_info = {
                        'fast_ema': round(analysis_result.ema_signal.fast_ema, 5),
                        'slow_ema': round(analysis_result.ema_signal.slow_ema, 5),
                        'separation': round(analysis_result.ema_signal.separation, 3),
                        'signal_type': analysis_result.ema_signal.signal_type,
                        'momentum_strength': round(analysis_result.ema_signal.momentum_strength, 3),
                        'crossover_confirmed': analysis_result.ema_signal.crossover_confirmed
                    }
                
                # Multi-timeframe info
                mtf_info = None
                if analysis_result.timeframe_alignment:
                    mtf_info = {
                        'primary_timeframe': analysis_result.timeframe_alignment.primary_timeframe,
                        'higher_timeframe': analysis_result.timeframe_alignment.higher_timeframe,
                        'alignment_score': round(analysis_result.timeframe_alignment.alignment_score, 3),
                        'confirmation_level': analysis_result.timeframe_alignment.confirmation_level
                    }
                
                # Volume confirmation info
                volume_info = None
                if analysis_result.volume_confirmation:
                    volume_info = {
                        'volume_spike': analysis_result.volume_confirmation.volume_spike,
                        'volume_ratio': round(analysis_result.volume_confirmation.volume_ratio, 2),
                        'strength': round(analysis_result.volume_confirmation.strength, 3)
                    }
                
                # Early warnings
                early_warnings = []
                for warning in analysis_result.early_warnings:
                    early_warnings.append({
                        'type': warning.warning_type,
                        'confidence': round(warning.confidence, 3),
                        'probability_score': round(warning.probability_score, 3),
                        'description': warning.description,
                        'factors': warning.factors,
                        'strength': round(warning.strength, 3)
                    })
                
                symbol_analyses[symbol] = {
                    'status': 'success',
                    'current_price': round(current_price, 5),
                    'overall_confidence': round(analysis_result.confidence, 3),
                    'signals_count': len(signals_summary),
                    'signals': signals_summary,
                    'market_structure': structure_info,
                    'divergences': divergences_info,
                    'aroon_signal': aroon_info,
                    'ema_signal': ema_info,
                    'trendline_breaks': len(analysis_result.trendline_breaks),
                    'mtf_alignment': mtf_info,
                    'volume_confirmation': volume_info,
                    'early_warnings': early_warnings,
                    'timestamp': datetime.now().isoformat()
                }
                
            except Exception as e:
                logger.error(f"Error analyzing {symbol}: {str(e)}")
                symbol_analyses[symbol] = {
                    'status': 'error',
                    'message': str(e)
                }
        
        mt5.shutdown()
        
        return jsonify({
            'status': 'success',
            'enabled': True,
            'config': {
                'sensitivity': config.get('trend_detection_sensitivity', 5),
                'min_confidence': config.get('min_trend_confidence', 0.6),
                'early_signals': config.get('enable_early_signals', True),
                'mtf_confirmation': config.get('enable_mtf_confirmation', True)
            },
            'symbols': symbol_analyses,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in trend detection status: {str(e)}")
        mt5.shutdown()
        return jsonify({
            'status': 'error',
            'message': f'Failed to get trend detection status: {str(e)}'
        })


@app.route('/api/analysis/performance', methods=['GET'])
def analysis_performance():
    """Get performance analysis"""
    days = int(request.args.get('days', 7))
    
    if not mt5.initialize():
        logger.error("MT5 not connected for performance analysis")
        # Return default values instead of error
        return jsonify({
            'total_trades': 0,
            'wins': 0,
            'losses': 0,
            'today_wins': 0,
            'today_losses': 0,
            'win_rate': 0,
            'total_profit': 0,
            'avg_win': 0,
            'avg_loss': 0,
        })
    
    try:
        from_date = datetime.now() - timedelta(days=days)
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        deals = mt5.history_deals_get(from_date, datetime.now())
        
        if deals is None or len(deals) == 0:
            logger.info("No trades found for performance analysis")
            mt5.shutdown()
            # Return zeros instead of error
            return jsonify({
                'total_trades': 0,
                'wins': 0,
                'losses': 0,
                'today_wins': 0,
                'today_losses': 0,
                'win_rate': 0,
                'total_profit': 0,
                'avg_win': 0,
                'avg_loss': 0,
            })
        
        # Calculate statistics
        total_profit = sum([d.profit for d in deals if d.entry == mt5.DEAL_ENTRY_OUT])
        wins = len([d for d in deals if d.entry == mt5.DEAL_ENTRY_OUT and d.profit > 0])
        losses = len([d for d in deals if d.entry == mt5.DEAL_ENTRY_OUT and d.profit < 0])
        total_trades = wins + losses
        
        # Today's statistics
        today_wins = len([d for d in deals if d.entry == mt5.DEAL_ENTRY_OUT and d.profit > 0 and d.time >= today_start.timestamp()])
        today_losses = len([d for d in deals if d.entry == mt5.DEAL_ENTRY_OUT and d.profit < 0 and d.time >= today_start.timestamp()])
        
        win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
        
        analysis = {
            'total_trades': total_trades,
            'wins': wins,
            'losses': losses,
            'today_wins': today_wins,
            'today_losses': today_losses,
            'win_rate': round(win_rate, 1),
            'total_profit': round(total_profit, 2),
            'avg_win': round(sum([d.profit for d in deals if d.entry == mt5.DEAL_ENTRY_OUT and d.profit > 0]) / wins, 2) if wins > 0 else 0,
            'avg_loss': round(sum([d.profit for d in deals if d.entry == mt5.DEAL_ENTRY_OUT and d.profit < 0]) / losses, 2) if losses > 0 else 0,
        }
        
        mt5.shutdown()
        return jsonify(analysis)
    
    except Exception as e:
        logger.error(f"Error in performance analysis: {str(e)}")
        mt5.shutdown()
        # Return zeros on error
        return jsonify({
            'total_trades': 0,
            'wins': 0,
            'losses': 0,
            'today_wins': 0,
            'today_losses': 0,
            'win_rate': 0,
            'total_profit': 0,
            'avg_win': 0,
            'avg_loss': 0,
        })


@app.route('/api/analysis/recommendations', methods=['GET'])
def analysis_recommendations():
    """Get AI recommendations based on trade history"""
    # This would call your comprehensive_trade_analysis.py
    # For now, return sample recommendations
    
    recommendations = [
        {
            'priority': 1,
            'title': 'Tighten Stop Losses',
            'description': 'Your average loss is 332 pips. Reduce ATR_MULTIPLIER_SL to 0.8',
            'impact': 'Potential savings: $2,525',
            'action': 'Update configuration'
        },
        {
            'priority': 1,
            'title': 'Avoid 19:00 Hour',
            'description': '100% of losses occurred at 19:00. Enable trading hours filter.',
            'impact': 'Potential savings: $825',
            'action': 'Enable TRADING_HOURS'
        },
        {
            'priority': 2,
            'title': 'Cut Losers Faster',
            'description': 'Average hold time for losses is 35 minutes. Reduce to 20 minutes.',
            'impact': 'Potential savings: $547',
            'action': 'Update SCALP_MAX_HOLD_MINUTES'
        }
    ]
    
    return jsonify({'recommendations': recommendations})


@app.route('/api/charts/data', methods=['GET'])
def charts_data():
    """Get data for charts"""
    if not mt5.initialize():
        return jsonify({'status': 'error', 'message': 'MT5 not connected'})
    
    # Get date range from query parameter (default: last 30 days)
    date_range = request.args.get('range', 'last30days')
    
    # Calculate from_date based on range
    now = datetime.now()
    if date_range == 'today':
        from_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif date_range == 'last7days':
        from_date = now - timedelta(days=7)
    elif date_range == 'last30days':
        from_date = now - timedelta(days=30)
    elif date_range == 'thisweek':
        # Monday of current week
        days_since_monday = now.weekday()
        from_date = (now - timedelta(days=days_since_monday)).replace(hour=0, minute=0, second=0, microsecond=0)
    elif date_range == 'lastweek':
        # Monday of last week
        days_since_monday = now.weekday()
        from_date = (now - timedelta(days=days_since_monday + 7)).replace(hour=0, minute=0, second=0, microsecond=0)
        now = (now - timedelta(days=days_since_monday)).replace(hour=0, minute=0, second=0, microsecond=0)
    elif date_range == 'thismonth':
        from_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    elif date_range == 'lastmonth':
        # First day of last month
        first_of_this_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        from_date = (first_of_this_month - timedelta(days=1)).replace(day=1)
        now = first_of_this_month
    else:  # 'all' or unknown
        from_date = now - timedelta(days=365)  # Last year for 'all'
    
    deals = mt5.history_deals_get(from_date, now)
    
    if deals is None or len(deals) == 0:
        mt5.shutdown()
        return jsonify({'status': 'error', 'message': 'No trades found'})
    
    # Profit by symbol
    symbol_profits = {}
    symbol_trades = {}
    for deal in deals:
        if deal.entry == mt5.DEAL_ENTRY_OUT:
            symbol = deal.symbol
            if symbol not in symbol_profits:
                symbol_profits[symbol] = 0
                symbol_trades[symbol] = 0
            symbol_profits[symbol] += deal.profit
            symbol_trades[symbol] += 1
    
    # Win/Loss by symbol
    symbol_wins = {}
    symbol_losses = {}
    for deal in deals:
        if deal.entry == mt5.DEAL_ENTRY_OUT:
            symbol = deal.symbol
            if symbol not in symbol_wins:
                symbol_wins[symbol] = 0
                symbol_losses[symbol] = 0
            if deal.profit > 0:
                symbol_wins[symbol] += 1
            else:
                symbol_losses[symbol] += 1
    
    # Daily profit trend (last 7 days)
    daily_profits = {}
    for deal in deals:
        if deal.entry == mt5.DEAL_ENTRY_OUT:
            date = datetime.fromtimestamp(deal.time).strftime('%Y-%m-%d')
            if date not in daily_profits:
                daily_profits[date] = 0
            daily_profits[date] += deal.profit
    
    # Sort daily profits by date
    sorted_daily = sorted(daily_profits.items(), key=lambda x: x[0])
    daily_labels = [item[0] for item in sorted_daily[-7:]]  # Last 7 days
    daily_values = [item[1] for item in sorted_daily[-7:]]
    
    # Hourly performance
    hourly_profits = {}
    hourly_trades = {}
    for deal in deals:
        if deal.entry == mt5.DEAL_ENTRY_OUT:
            hour = datetime.fromtimestamp(deal.time).hour
            if hour not in hourly_profits:
                hourly_profits[hour] = 0
                hourly_trades[hour] = 0
            hourly_profits[hour] += deal.profit
            hourly_trades[hour] += 1
    
    chart_data = {
        'symbol_profits': symbol_profits,
        'symbol_trades': symbol_trades,
        'symbol_wins': symbol_wins,
        'symbol_losses': symbol_losses,
        'daily_labels': daily_labels,
        'daily_values': daily_values,
        'hourly_profits': hourly_profits,
        'hourly_trades': hourly_trades
    }
    
    mt5.shutdown()
    return jsonify(chart_data)


@app.route('/api/symbols/data-availability', methods=['POST'])
def check_symbol_data_availability():
    """Check if selected symbols have sufficient historical data for analysis"""
    try:
        data = request.json
        symbols = data.get('symbols', [])
        requested_bars = data.get('bars', 200)
        timeframe = data.get('timeframe', 16385)  # Default H1
        
        if not symbols:
            return jsonify({'status': 'error', 'message': 'No symbols provided'})
        
        if not mt5.initialize():
            return jsonify({'status': 'error', 'message': 'MT5 not connected. Please check MT5 is running.'})
        
        # Map timeframe values to MT5 constants
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
            try:
                # Check if symbol exists
                symbol_info = mt5.symbol_info(symbol)
                if symbol_info is None:
                    results.append({
                        'symbol': symbol,
                        'available': False,
                        'bars_available': 0,
                        'error': 'Symbol not found'
                    })
                    continue
                
                # Ensure symbol is visible in Market Watch
                if not symbol_info.visible:
                    if not mt5.symbol_select(symbol, True):
                        results.append({
                            'symbol': symbol,
                            'available': False,
                            'bars_available': 0,
                            'error': 'Cannot select symbol'
                        })
                        continue
                
                # Get historical data to check availability
                from datetime import datetime, timedelta
                end_time = datetime.now()
                
                # Try to get the requested number of bars
                rates = mt5.copy_rates_from(symbol, mt5_timeframe, end_time, requested_bars)
                
                if rates is None or len(rates) == 0:
                    results.append({
                        'symbol': symbol,
                        'available': False,
                        'bars_available': 0,
                        'error': 'No historical data available'
                    })
                    continue
                
                bars_available = len(rates)
                is_sufficient = bars_available >= requested_bars
                
                # Additional check: ensure data is recent (not too old)
                if len(rates) > 0:
                    latest_time = datetime.fromtimestamp(rates[-1]['time'])
                    time_diff = datetime.now() - latest_time
                    
                    # If latest data is more than 1 day old for intraday or 1 week old for daily, flag as stale
                    max_age = timedelta(days=1) if timeframe < 16408 else timedelta(days=7)
                    if time_diff > max_age:
                        results.append({
                            'symbol': symbol,
                            'available': False,
                            'bars_available': bars_available,
                            'error': f'Data is stale (last update: {latest_time.strftime("%Y-%m-%d %H:%M")})'
                        })
                        continue
                
                results.append({
                    'symbol': symbol,
                    'available': is_sufficient,
                    'bars_available': bars_available,
                    'error': None if is_sufficient else f'Only {bars_available} bars available, need {requested_bars}'
                })
                
            except Exception as e:
                logger.error(f"Error checking data for {symbol}: {str(e)}")
                results.append({
                    'symbol': symbol,
                    'available': False,
                    'bars_available': 0,
                    'error': f'Check failed: {str(e)}'
                })
        
        mt5.shutdown()
        
        # Summary statistics
        total_symbols = len(results)
        available_symbols = len([r for r in results if r['available']])
        
        logger.info(f"Data availability check completed: {available_symbols}/{total_symbols} symbols have sufficient data")
        
        return jsonify({
            'status': 'success',
            'results': results,
            'summary': {
                'total_symbols': total_symbols,
                'available_symbols': available_symbols,
                'requested_bars': requested_bars,
                'timeframe': timeframe
            }
        })
        
    except Exception as e:
        logger.error(f"Error in data availability check: {str(e)}")
        mt5.shutdown()
        return jsonify({'status': 'error', 'message': f'Failed to check data availability: {str(e)}'})


@app.route('/api/logs', methods=['GET'])
def get_logs():
    """Get recent log entries"""
    try:
        lines = int(request.args.get('lines', 50))
        
        # Log the file path for debugging
        logger.info(f"Reading logs from: {LOG_FILE}")
        logger.info(f"Log file exists: {LOG_FILE.exists()}")
        
        if not LOG_FILE.exists():
            logger.warning(f"Log file not found at: {LOG_FILE}")
            return jsonify({'logs': [
                f'Log file not found at: {LOG_FILE}',
                'This may be normal on first start.',
                'Start the bot to generate logs.'
            ]})
        
        # Try to read with different encodings
        try:
            with open(LOG_FILE, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
        except UnicodeDecodeError:
            # Try with latin-1 if utf-8 fails
            with open(LOG_FILE, 'r', encoding='latin-1') as f:
                all_lines = f.readlines()
        
        if not all_lines:
            return jsonify({'logs': ['Log file is empty. Start the bot to generate logs.']})
        
        recent_lines = all_lines[-lines:]
        logger.info(f"Returning {len(recent_lines)} log lines")
        return jsonify({'logs': recent_lines})
    
    except PermissionError:
        logger.error("Permission denied reading log file")
        return jsonify({'logs': [f'Error: Permission denied reading {LOG_FILE}']})
    
    except Exception as e:
        logger.error(f"Failed to read logs: {str(e)}")
        return jsonify({'logs': [f'Error loading logs: {str(e)}', f'Log file path: {LOG_FILE}']})

@app.route('/api/logs/download', methods=['GET'])
def download_logs():
    """Download log file"""
    try:
        if not LOG_FILE.exists():
            return jsonify({'status': 'error', 'message': f'No log file found at {LOG_FILE}'})
        
        return send_file(LOG_FILE, as_attachment=True, download_name='gem_trading_logs.txt')
    
    except Exception as e:
        logger.error(f"Failed to download logs: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)})


@app.route('/api/logs/info', methods=['GET'])
def logs_info():
    """Get log file information for debugging"""
    try:
        import os
        info = {
            'log_file_path': str(LOG_FILE),
            'log_file_exists': LOG_FILE.exists(),
            'base_dir': str(BASE_DIR),
            'is_frozen': getattr(sys, 'frozen', False),
            'executable_path': sys.executable if getattr(sys, 'frozen', False) else 'N/A',
            'current_dir': os.getcwd(),
        }
        
        if LOG_FILE.exists():
            info['log_file_size'] = LOG_FILE.stat().st_size
            info['log_file_lines'] = sum(1 for _ in open(LOG_FILE, 'r', encoding='utf-8', errors='ignore'))
        
        return jsonify(info)
    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/api/ml/train', methods=['POST'])
def train_ml_model():
    """Train ML model with training data"""
    try:
        data = request.json
        training_data_path = data.get('training_data_path', 'data/training_data.csv')
        model_path = data.get('model_path', 'models/ml_signal_model.pkl')
        
        logger.info(f"Training ML model with data from: {training_data_path}")
        
        # Check if training data exists
        from pathlib import Path
        if not Path(training_data_path).exists():
            return jsonify({
                'status': 'error',
                'message': f'Training data not found: {training_data_path}'
            })
        
        # Import ML components
        try:
            from src.ml_signal_generator import MLSignalGenerator
        except ImportError as e:
            return jsonify({
                'status': 'error',
                'message': f'ML components not available: {str(e)}'
            })
        
        # Load training data
        import pandas as pd
        df = pd.read_csv(training_data_path)
        
        if len(df) < 50:
            return jsonify({
                'status': 'error',
                'message': f'Insufficient training data: {len(df)} samples (minimum 50 required)'
            })
        
        # Prepare features and labels
        feature_columns = ['rsi', 'macd', 'macd_signal', 'adx', 'atr', 'ema_fast', 'ema_slow', 'volume']
        
        # Check if all required columns exist
        missing_cols = set(feature_columns) - set(df.columns)
        if missing_cols:
            return jsonify({
                'status': 'error',
                'message': f'Missing required columns: {", ".join(missing_cols)}'
            })
        
        X = df[feature_columns]
        y = df['profitable'].values
        
        # Train model
        ml_generator = MLSignalGenerator(logger=logger)
        
        # Set model path before training
        ml_generator.model_path = model_path
        
        success = ml_generator.train_model(X, y)
        
        if success:
            # Get model statistics
            from sklearn.model_selection import train_test_split
            from sklearn.metrics import accuracy_score, precision_score, recall_score
            
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            y_pred = ml_generator.model.predict(X_test)
            
            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred, zero_division=0)
            recall = recall_score(y_test, y_pred, zero_division=0)
            
            logger.info(f"ML model trained successfully - Accuracy: {accuracy:.2%}")
            
            return jsonify({
                'status': 'success',
                'message': 'ML model trained successfully',
                'statistics': {
                    'samples': len(df),
                    'accuracy': round(accuracy * 100, 2),
                    'precision': round(precision * 100, 2),
                    'recall': round(recall * 100, 2),
                    'model_path': model_path
                }
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to train ML model'
            })
    
    except Exception as e:
        logger.error(f"Error training ML model: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Training failed: {str(e)}'
        })


@app.route('/api/ml/test', methods=['GET'])
def test_ml_features():
    """Test ML features with current market data"""
    try:
        # Get configuration
        config = config_manager.get_config()
        
        if not config.get('ml_enabled', False):
            return jsonify({
                'status': 'warning',
                'message': 'ML features are disabled in configuration'
            })
        
        # Import ML components
        try:
            from src.ml_integration import MLIntegration
        except ImportError as e:
            return jsonify({
                'status': 'error',
                'message': f'ML components not available: {str(e)}'
            })
        
        # Initialize ML integration
        ml_integration = MLIntegration(config, logger=logger)
        
        # Test with first symbol
        symbols = config.get('symbols', ['XAUUSD'])
        test_symbol = symbols[0]
        
        # Get market data
        if not mt5.initialize():
            return jsonify({
                'status': 'error',
                'message': 'MT5 not connected'
            })
        
        timeframe = config.get('timeframe', 30)
        timeframe_map = {
            1: mt5.TIMEFRAME_M1,
            5: mt5.TIMEFRAME_M5,
            15: mt5.TIMEFRAME_M15,
            30: mt5.TIMEFRAME_M30,
            16385: mt5.TIMEFRAME_H1,
            16388: mt5.TIMEFRAME_H4,
            16408: mt5.TIMEFRAME_D1
        }
        mt5_timeframe = timeframe_map.get(timeframe, mt5.TIMEFRAME_M30)
        
        rates = mt5.copy_rates_from_pos(test_symbol, mt5_timeframe, 0, 100)
        mt5.shutdown()
        
        if rates is None or len(rates) < 50:
            return jsonify({
                'status': 'error',
                'message': 'Insufficient market data'
            })
        
        # Prepare market data
        import pandas as pd
        df = pd.DataFrame(rates)
        
        market_data = {
            'close': df['close'].tolist(),
            'high': df['high'].tolist(),
            'low': df['low'].tolist(),
            'open': df['open'].tolist(),
            'volume': df['tick_volume'].tolist()
        }
        
        # Get enhanced signal
        enhanced_signals = ml_integration.get_enhanced_signal(
            symbol=test_symbol,
            market_data=market_data,
            technical_signal='NEUTRAL',
            technical_confidence=0.5
        )
        
        return jsonify({
            'status': 'success',
            'symbol': test_symbol,
            'signals': enhanced_signals,
            'message': 'ML features tested successfully'
        })
    
    except Exception as e:
        logger.error(f"Error testing ML features: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Test failed: {str(e)}'
        })


@app.route('/api/ml/stats', methods=['GET'])
def get_ml_stats():
    """Get ML model statistics"""
    try:
        config = config_manager.get_config()
        model_path = config.get('ml_model_path', 'models/ml_signal_model.pkl')
        
        from pathlib import Path
        model_file = Path(model_path)
        
        if not model_file.exists():
            return jsonify({
                'status': 'warning',
                'message': 'ML model not trained yet',
                'model_exists': False
            })
        
        # Get model file info
        import os
        from datetime import datetime
        
        stats = {
            'status': 'success',
            'model_exists': True,
            'model_path': str(model_file),
            'model_size': model_file.stat().st_size,
            'last_modified': datetime.fromtimestamp(model_file.stat().st_mtime).isoformat(),
            'ml_enabled': config.get('ml_enabled', False),
            'sentiment_enabled': config.get('sentiment_enabled', False),
            'pattern_enabled': config.get('pattern_enabled', True)
        }
        
        # Try to load model and get additional stats
        try:
            from src.ml_signal_generator import MLSignalGenerator
            ml_gen = MLSignalGenerator(logger=logger)
            
            if ml_gen.load_model(model_path):
                stats['model_loaded'] = True
                stats['is_trained'] = ml_gen.is_trained
            else:
                stats['model_loaded'] = False
        except Exception as e:
            stats['model_load_error'] = str(e)
        
        return jsonify(stats)
    
    except Exception as e:
        logger.error(f"Error getting ML stats: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to get stats: {str(e)}'
        })


@app.route('/api/ml/export', methods=['GET'])
def export_training_data():
    """Export training data from trade history"""
    try:
        days = int(request.args.get('days', 30))
        
        if not mt5.initialize():
            return jsonify({
                'status': 'error',
                'message': 'MT5 not connected'
            })
        
        from_date = datetime.now() - timedelta(days=days)
        deals = mt5.history_deals_get(from_date, datetime.now())
        
        if deals is None or len(deals) == 0:
            mt5.shutdown()
            return jsonify({
                'status': 'error',
                'message': 'No trade history found'
            })
        
        # Extract trade data
        import csv
        from io import StringIO
        
        output = StringIO()
        fieldnames = ['timestamp', 'symbol', 'close', 'rsi', 'macd', 'macd_signal', 'adx', 'atr',
                     'ema_fast', 'ema_slow', 'volume', 'profitable']
        
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        
        # Group deals by position
        positions_dict = {}
        for deal in deals:
            position_id = deal.position_id
            if position_id not in positions_dict:
                positions_dict[position_id] = {'entry': None, 'exit': None}
            
            if deal.entry == mt5.DEAL_ENTRY_IN:
                positions_dict[position_id]['entry'] = deal
            elif deal.entry == mt5.DEAL_ENTRY_OUT:
                positions_dict[position_id]['exit'] = deal
        
        # Export completed trades
        for position_id, deals_pair in positions_dict.items():
            entry_deal = deals_pair['entry']
            exit_deal = deals_pair['exit']
            
            if entry_deal and exit_deal:
                writer.writerow({
                    'timestamp': datetime.fromtimestamp(exit_deal.time).isoformat(),
                    'symbol': exit_deal.symbol,
                    'close': exit_deal.price,
                    'rsi': 0,  # Would need to calculate from historical data
                    'macd': 0,
                    'macd_signal': 0,
                    'adx': 0,
                    'atr': 0,
                    'ema_fast': 0,
                    'ema_slow': 0,
                    'volume': exit_deal.volume,
                    'profitable': 1 if exit_deal.profit > 0 else 0
                })
        
        mt5.shutdown()
        
        csv_data = output.getvalue()
        
        from flask import Response
        return Response(
            csv_data,
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=training_data.csv'}
        )
    
    except Exception as e:
        logger.error(f"Error exporting training data: {str(e)}")
        mt5.shutdown()
        return jsonify({
            'status': 'error',
            'message': f'Export failed: {str(e)}'
        })


def update_config_file(new_config):
    """Update the config.py file with new values"""
    import os
    config_path = os.path.join('src', 'config.py')
    
    # Read current config with UTF-8 encoding
    with open(config_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Mapping of config keys to file variable names
    config_mapping = {
        'symbols': 'SYMBOLS',
        'timeframe': 'TIMEFRAME',
        'risk_percent': 'RISK_PERCENT',
        'reward_ratio': 'REWARD_RATIO',
        'min_trade_confidence': 'MIN_TRADE_CONFIDENCE',
        'max_daily_loss': 'MAX_DAILY_LOSS',
        'analysis_bars': 'ANALYSIS_BARS',
        'fast_ma_period': 'FAST_MA_PERIOD',
        'slow_ma_period': 'SLOW_MA_PERIOD',
        'rsi_period': 'RSI_PERIOD',
        'rsi_overbought': 'RSI_OVERBOUGHT',
        'rsi_oversold': 'RSI_OVERSOLD',
        'macd_fast': 'MACD_FAST',
        'macd_slow': 'MACD_SLOW',
        'macd_signal': 'MACD_SIGNAL',
        'macd_min_histogram': 'MACD_MIN_HISTOGRAM',
        'atr_period': 'ATR_PERIOD',
        'atr_multiplier': 'ATR_MULTIPLIER_SL',
        'adx_min_strength': 'ADX_MIN_STRENGTH',
        'use_rsi': 'USE_RSI',
        'use_macd': 'USE_MACD',
        'use_adx': 'USE_ADX',
        'use_trend_filter': 'USE_TREND_FILTER',
        'trend_ma_period': 'TREND_MA_PERIOD',
        'enable_trading_hours': 'ENABLE_TRADING_HOURS',
        'trading_start_hour': 'TRADING_START_HOUR',
        'trading_end_hour': 'TRADING_END_HOUR',
        'avoid_news_trading': 'AVOID_NEWS_TRADING',
        'news_buffer_minutes': 'NEWS_BUFFER_MINUTES',
        'use_split_orders': 'USE_SPLIT_ORDERS',
        'num_positions': 'NUM_POSITIONS',
        'max_lot_per_order': 'MAX_LOT_PER_ORDER',
        'max_trades_total': 'MAX_TRADES_TOTAL',
        'max_trades_per_symbol': 'MAX_TRADES_PER_SYMBOL',
        'enable_trailing_stop': 'ENABLE_TRAILING_STOP',
        'trail_activation': 'TRAIL_ACTIVATION_ATR',
        'trail_distance': 'TRAIL_DISTANCE_ATR',
        'use_adaptive_risk': 'USE_ADAPTIVE_RISK',
        'max_risk_multiplier': 'MAX_RISK_MULTIPLIER',
        'min_risk_multiplier': 'MIN_RISK_MULTIPLIER',
        'max_drawdown_percent': 'MAX_DRAWDOWN_PERCENT',
        'max_daily_trades': 'MAX_DAILY_TRADES'
    }
    
    # Update values
    updated_lines = []
    for line in lines:
        updated = False
        
        for config_key, var_name in config_mapping.items():
            if config_key in new_config and line.startswith(f'{var_name} = '):
                value = new_config[config_key]
                
                # Format value based on type
                if isinstance(value, bool):
                    formatted_value = 'True' if value else 'False'
                elif isinstance(value, str):
                    formatted_value = f"'{value}'"
                elif isinstance(value, list):
                    formatted_value = str(value)
                else:
                    formatted_value = str(value)
                
                updated_lines.append(f"{var_name} = {formatted_value}\n")
                updated = True
                break
        
        # Handle TP_LEVELS specially (array of 3 values)
        if not updated and line.startswith('TP_LEVELS = '):
            if 'tp_level_1' in new_config and 'tp_level_2' in new_config and 'tp_level_3' in new_config:
                tp_levels = [new_config['tp_level_1'], new_config['tp_level_2'], new_config['tp_level_3']]
                updated_lines.append(f"TP_LEVELS = {tp_levels}\n")
                updated = True
        
        # Handle TIMEFRAME specially (needs mt5.TIMEFRAME_ prefix)
        if not updated and line.startswith('TIMEFRAME = '):
            if 'timeframe' in new_config:
                timeframe_value = new_config['timeframe']
                # Map numeric values to MT5 constants
                timeframe_map = {
                    1: 'mt5.TIMEFRAME_M1',
                    5: 'mt5.TIMEFRAME_M5',
                    15: 'mt5.TIMEFRAME_M15',
                    30: 'mt5.TIMEFRAME_M30',
                    16385: 'mt5.TIMEFRAME_H1',
                    16388: 'mt5.TIMEFRAME_H4',
                    16408: 'mt5.TIMEFRAME_D1'
                }
                formatted_timeframe = timeframe_map.get(timeframe_value, f'mt5.TIMEFRAME_H1')
                updated_lines.append(f"TIMEFRAME = {formatted_timeframe}  # {timeframe_value}\n")
                updated = True
        
        if not updated:
            updated_lines.append(line)
    
    # Write back with UTF-8 encoding
    with open(config_path, 'w', encoding='utf-8') as f:
        f.writelines(updated_lines)


def run_bot_background():
    """Run bot in background thread with proper termination handling"""
    global bot_running, current_config
    
    # Add src to path for executable compatibility
    import sys
    from pathlib import Path
    if getattr(sys, 'frozen', False):
        # Running as executable - add src to path
        src_path = Path(sys.executable).parent / 'src'
        if src_path.exists() and str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))
            logger.info(f"Added to sys.path: {src_path}")
    
    try:
        # Force reload of the module to pick up changes
        import importlib
        import sys
        if 'src.mt5_trading_bot' in sys.modules:
            importlib.reload(sys.modules['src.mt5_trading_bot'])
        
        from src.mt5_trading_bot import MT5TradingBot
    except ImportError as e:
        logger.error(f"Failed to import MT5TradingBot: {e}")
        logger.error(f"sys.path: {sys.path}")
        bot_running = False
        return
    
    # Get latest configuration from config manager
    current_config = config_manager.get_config()
    
    logger.info("Initializing trading bot...")
    logger.info(f"Configuration loaded:")
    logger.info(f"  Symbols: {current_config.get('symbols')}")
    logger.info(f"  Timeframe: {current_config.get('timeframe')}")
    logger.info(f"  Risk: {current_config.get('risk_percent')}%")
    logger.info(f"  Reward Ratio: {current_config.get('reward_ratio')}:1")
    logger.info(f"  Min Confidence: {current_config.get('min_trade_confidence', 0.6)*100}%")
    
    try:
        bot = MT5TradingBot(current_config)
    except Exception as e:
        logger.error(f"Failed to create MT5TradingBot instance: {e}")
        logger.error(f"Traceback:", exc_info=True)
        bot_running = False
        return
    
    if not bot.connect():
        logger.error("Failed to connect to MT5")
        bot_running = False
        return
    
    logger.info("Bot connected successfully, starting trading loop...")
    
    try:
        while bot_running:
            try:
                # Check if bot should still be running
                if not bot_running:
                    logger.info("Bot stop signal received, exiting loop")
                    break
                
                logger.info(f"Starting analysis cycle for {len(bot.symbols)} symbols...")
                
                # Run strategy for each symbol
                for symbol in bot.symbols:
                    if not bot_running:  # Check again before each symbol
                        break
                    try:
                        logger.info(f"Analyzing {symbol}...")
                        bot.run_strategy(symbol)
                        logger.info(f"Completed analysis for {symbol}")
                        # Small delay between symbols to avoid MT5 rate limiting
                        time.sleep(0.5)  # 500ms delay between symbols
                    except Exception as e:
                        logger.error(f"Error processing {symbol}: {str(e)}")
                        logger.error(f"Traceback:", exc_info=True)
                
                # Manage existing positions (trailing stops)
                if bot_running:
                    try:
                        bot.manage_positions()
                    except Exception as e:
                        logger.error(f"Error managing positions: {str(e)}")
                        logger.error(f"Traceback:", exc_info=True)
                
                # Sleep with frequent checks for stop signal
                update_interval = current_config.get('update_interval', 60)
                for _ in range(update_interval):
                    if not bot_running:
                        logger.info("Bot stop signal received during sleep")
                        break
                    time.sleep(1)  # Check every second
                
            except Exception as e:
                logger.error(f"Error in bot loop: {str(e)}")
                logger.error(f"Traceback:", exc_info=True)
                if not bot_running:
                    break
                time.sleep(5)  # Wait before retrying
    except Exception as e:
        logger.error(f"Critical bot error: {str(e)}")
        logger.error(f"Traceback:", exc_info=True)
    finally:
        logger.info("Shutting down bot...")
        try:
            bot.disconnect()
        except Exception as e:
            logger.error(f"Error disconnecting bot: {e}")
        bot_running = False
        logger.info("Bot shutdown complete")


if __name__ == '__main__':
    print("=" * 80)
    print("GEM TRADING DASHBOARD")
    print("=" * 80)
    print()
    print("Starting web server...")
    print("Dashboard will be available at: http://gemtrading:5000")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 80)
    
    # Run with reloader disabled to prevent crashes
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
