"""
Web Dashboard for MT5 Trading Bot
Modern UI for configuration, monitoring, and analysis
"""

from flask import Flask, render_template, request, jsonify, send_file
import MetaTrader5 as mt5
from datetime import datetime, timedelta
import json
import os
import threading
import time
from src.config import get_config

app = Flask(__name__)

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
        
        # Update config file
        update_config_file(new_config)
        current_config = new_config
        
        return jsonify({'status': 'success', 'message': 'Configuration updated'})


@app.route('/api/bot/start', methods=['POST'])
def start_bot():
    """Start the trading bot"""
    global bot_running, bot_thread
    
    if bot_running:
        return jsonify({'status': 'error', 'message': 'Bot already running'})
    
    bot_running = True
    bot_thread = threading.Thread(target=run_bot_background)
    bot_thread.start()
    
    return jsonify({'status': 'success', 'message': 'Bot started'})


@app.route('/api/bot/stop', methods=['POST'])
def stop_bot():
    """Stop the trading bot"""
    global bot_running
    
    bot_running = False
    
    return jsonify({'status': 'success', 'message': 'Bot stopped'})


@app.route('/api/bot/status', methods=['GET'])
def bot_status():
    """Get bot status"""
    if not mt5.initialize():
        return jsonify({'status': 'error', 'message': 'MT5 not connected'})
    
    account_info = mt5.account_info()
    positions = mt5.positions_get()
    
    status = {
        'running': bot_running,
        'balance': account_info.balance if account_info else 0,
        'equity': account_info.equity if account_info else 0,
        'profit': account_info.profit if account_info else 0,
        'open_positions': len(positions) if positions else 0,
        'margin_free': account_info.margin_free if account_info else 0,
    }
    
    mt5.shutdown()
    return jsonify(status)


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
                'symbol': deal.symbol,
                'type': 'BUY' if deal.type == mt5.ORDER_TYPE_BUY else 'SELL',
                'volume': deal.volume,
                'price': deal.price,
                'profit': deal.profit,
                'commission': deal.commission,
            })
    
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
        return jsonify({'status': 'error', 'message': 'MT5 not connected'})
    
    from_date = datetime.now() - timedelta(days=days)
    deals = mt5.history_deals_get(from_date, datetime.now())
    
    if deals is None or len(deals) == 0:
        mt5.shutdown()
        return jsonify({'status': 'error', 'message': 'No trades found'})
    
    # Calculate statistics
    total_profit = sum([d.profit for d in deals if d.entry == mt5.DEAL_ENTRY_OUT])
    wins = len([d for d in deals if d.entry == mt5.DEAL_ENTRY_OUT and d.profit > 0])
    losses = len([d for d in deals if d.entry == mt5.DEAL_ENTRY_OUT and d.profit < 0])
    total_trades = wins + losses
    
    win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
    
    analysis = {
        'total_trades': total_trades,
        'wins': wins,
        'losses': losses,
        'win_rate': round(win_rate, 1),
        'total_profit': round(total_profit, 2),
        'avg_win': round(sum([d.profit for d in deals if d.entry == mt5.DEAL_ENTRY_OUT and d.profit > 0]) / wins, 2) if wins > 0 else 0,
        'avg_loss': round(sum([d.profit for d in deals if d.entry == mt5.DEAL_ENTRY_OUT and d.profit < 0]) / losses, 2) if losses > 0 else 0,
    }
    
    mt5.shutdown()
    return jsonify(analysis)


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


def update_config_file(new_config):
    """Update the config.py file with new values"""
    config_path = 'src/config.py'
    
    # Read current config
    with open(config_path, 'r') as f:
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
    
    # Write back
    with open(config_path, 'w') as f:
        f.writelines(updated_lines)


def run_bot_background():
    """Run bot in background thread"""
    global bot_running
    
    from src.mt5_trading_bot import MT5TradingBot
    
    bot = MT5TradingBot(current_config)
    
    if not bot.connect():
        bot_running = False
        return
    
    try:
        while bot_running:
            bot.run()
            time.sleep(current_config.get('update_interval', 15))
    except Exception as e:
        print(f"Bot error: {e}")
    finally:
        bot.disconnect()
        bot_running = False


if __name__ == '__main__':
    print("=" * 80)
    print("MT5 TRADING BOT - WEB DASHBOARD")
    print("=" * 80)
    print()
    print("Starting web server...")
    print("Dashboard will be available at: http://localhost:5000")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 80)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
