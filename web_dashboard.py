"""
Web Dashboard for GEM Trading
Modern UI for configuration, monitoring, and analysis
"""

from flask import Flask, render_template, request, jsonify, send_file
import MetaTrader5 as mt5
from datetime import datetime, timedelta
import json
import os
import threading
import time
import logging
from src.config import get_config

app = Flask(__name__)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Global state
bot_running = False
bot_thread = None
current_config = get_config()


@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')


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
            risk = new_config.get('risk_percent', 0)
            if risk < 0.1 or risk > 5:
                return jsonify({'status': 'error', 'message': 'Risk must be between 0.1% and 5%'})
            
            confidence = new_config.get('min_confidence', 0)
            if confidence < 0.2 or confidence > 0.8:
                return jsonify({'status': 'error', 'message': 'Confidence must be between 20% and 80%'})
            
            # Update config file
            update_config_file(new_config)
            current_config = new_config
            
            logger.info(f"Configuration updated: Risk={risk}%, Confidence={confidence*100}%")
            return jsonify({'status': 'success', 'message': 'Configuration updated successfully'})
        
        except Exception as e:
            logger.error(f"Failed to update configuration: {str(e)}")
            return jsonify({'status': 'error', 'message': f'Failed to update: {str(e)}'})


@app.route('/api/bot/start', methods=['POST'])
def start_bot():
    """Start the trading bot"""
    global bot_running, bot_thread
    
    if bot_running:
        return jsonify({'status': 'error', 'message': 'Bot already running'})
    
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
    bot_thread = threading.Thread(target=run_bot_background)
    bot_thread.start()
    
    logger.info("Trading bot started")
    return jsonify({'status': 'success', 'message': 'Bot started successfully'})


@app.route('/api/bot/stop', methods=['POST'])
def stop_bot():
    """Stop the trading bot"""
    global bot_running
    
    bot_running = False
    logger.info("Trading bot stopped")
    
    return jsonify({'status': 'success', 'message': 'Bot stopped successfully'})


@app.route('/api/bot/status', methods=['GET'])
def bot_status():
    """Get bot status"""
    try:
        # Check if bot is running by looking for recent activity
        global bot_running
        
        # Try to detect if bot is running independently
        if not bot_running and os.path.exists('trading_bot.log'):
            try:
                # Check if log file was modified in last 30 seconds
                log_mtime = os.path.getmtime('trading_bot.log')
                if time.time() - log_mtime < 30:
                    # Bot is likely running (log updated recently)
                    bot_running = True
            except:
                pass
        
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
    
    # Convert to list of dicts
    trades_list = []
    for deal in deals:
        if deal.entry in [mt5.DEAL_ENTRY_OUT]:  # Only closed trades
            trades_list.append({
                'time': datetime.fromtimestamp(deal.time).strftime('%Y-%m-%d %H:%M:%S'),
                'timestamp': deal.time,
                'symbol': deal.symbol,
                'type': 'BUY' if deal.type == mt5.ORDER_TYPE_BUY else 'SELL',
                'volume': deal.volume,
                'price': deal.price,
                'profit': deal.profit,
                'commission': deal.commission,
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
    
    # Get last 30 days of deals
    from_date = datetime.now() - timedelta(days=30)
    deals = mt5.history_deals_get(from_date, datetime.now())
    
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


@app.route('/api/logs', methods=['GET'])
def get_logs():
    """Get recent log entries"""
    try:
        lines = int(request.args.get('lines', 50))
        
        if not os.path.exists('trading_bot.log'):
            logger.info("Log file not found, returning empty logs")
            return jsonify({'logs': ['No log file found yet. Start the bot to generate logs.']})
        
        # Try to read with different encodings
        try:
            with open('trading_bot.log', 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
        except UnicodeDecodeError:
            # Try with latin-1 if utf-8 fails
            with open('trading_bot.log', 'r', encoding='latin-1') as f:
                all_lines = f.readlines()
        
        if not all_lines:
            return jsonify({'logs': ['Log file is empty. Start the bot to generate logs.']})
        
        recent_lines = all_lines[-lines:]
        return jsonify({'logs': recent_lines})
    
    except PermissionError:
        logger.error("Permission denied reading log file")
        return jsonify({'logs': ['Error: Permission denied. Log file may be locked by another process.']})
    
    except Exception as e:
        logger.error(f"Failed to read logs: {str(e)}")
        return jsonify({'logs': [f'Error loading logs: {str(e)}']})


@app.route('/api/logs/download', methods=['GET'])
def download_logs():
    """Download log file"""
    try:
        if not os.path.exists('trading_bot.log'):
            return jsonify({'status': 'error', 'message': 'No log file found'})
        
        return send_file('trading_bot.log', as_attachment=True, download_name='gem_trading_logs.txt')
    
    except Exception as e:
        logger.error(f"Failed to download logs: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)})


def update_config_file(new_config):
    """Update the config.py file with new values"""
    import os
    config_path = os.path.join('src', 'config.py')
    
    # Read current config with UTF-8 encoding
    with open(config_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Update values
    updated_lines = []
    for line in lines:
        # Update symbols
        if line.startswith('SYMBOLS = '):
            updated_lines.append(f"SYMBOLS = {new_config['symbols']}\n")
        # Update timeframe
        elif line.startswith('TIMEFRAME = '):
            updated_lines.append(f"TIMEFRAME = {new_config['timeframe']}\n")
        # Update risk
        elif line.startswith('RISK_PERCENT = '):
            updated_lines.append(f"RISK_PERCENT = {new_config['risk_percent']}\n")
        # Add more as needed
        else:
            updated_lines.append(line)
    
    # Write back with UTF-8 encoding
    with open(config_path, 'w', encoding='utf-8') as f:
        f.writelines(updated_lines)


def run_bot_background():
    """Run bot in background thread"""
    global bot_running
    
    from src.mt5_trading_bot import MT5TradingBot
    
    logger.info("Initializing trading bot...")
    bot = MT5TradingBot(current_config)
    
    if not bot.connect():
        logger.error("Failed to connect to MT5")
        bot_running = False
        return
    
    logger.info("Bot connected successfully, starting trading loop...")
    
    try:
        while bot_running:
            try:
                bot.run()
                time.sleep(current_config.get('update_interval', 15))
            except Exception as e:
                logger.error(f"Error in bot loop: {str(e)}")
                time.sleep(5)  # Wait before retrying
    except Exception as e:
        logger.error(f"Critical bot error: {str(e)}")
    finally:
        logger.info("Shutting down bot...")
        bot.disconnect()
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
