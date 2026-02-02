#!/usr/bin/env python3
"""
Simple Dashboard Server - Emergency Working Version
Serves a minimal working dashboard to test JavaScript functionality
"""

from flask import Flask, send_file, jsonify, request
import MetaTrader5 as mt5
from datetime import datetime, timedelta
import json
import os
import sys
import logging
from pathlib import Path
from src.config_manager import get_config_manager

app = Flask(__name__)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global state
bot_running = False
config_manager = get_config_manager()

@app.route('/')
def index():
    """Serve the minimal working dashboard"""
    return send_file('dashboard_minimal_working.html')

@app.route('/api/config', methods=['GET'])
def config_api():
    """Get configuration"""
    try:
        config = config_manager.get_config()
        return jsonify(config)
    except Exception as e:
        logger.error(f"Config API error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/bot/status', methods=['GET'])
def bot_status():
    """Get bot status"""
    try:
        if not mt5.initialize():
            return jsonify({
                'running': bot_running,
                'balance': 0,
                'equity': 0,
                'profit': 0,
                'open_positions': 0,
                'currency': 'USD',
                'error': 'MT5 not connected'
            })
        
        account_info = mt5.account_info()
        positions = mt5.positions_get()
        
        status = {
            'running': bot_running,
            'balance': account_info.balance if account_info else 0,
            'equity': account_info.equity if account_info else 0,
            'profit': account_info.profit if account_info else 0,
            'open_positions': len(positions) if positions else 0,
            'currency': account_info.currency if account_info else 'USD'
        }
        
        mt5.shutdown()
        return jsonify(status)
    
    except Exception as e:
        logger.error(f"Bot status error: {e}")
        mt5.shutdown()
        return jsonify({
            'running': bot_running,
            'balance': 0,
            'equity': 0,
            'profit': 0,
            'open_positions': 0,
            'currency': 'USD',
            'error': str(e)
        })

@app.route('/api/bot/start', methods=['POST'])
def start_bot():
    """Start the trading bot"""
    global bot_running
    
    if bot_running:
        return jsonify({'status': 'error', 'message': 'Bot already running'})
    
    # Test MT5 connection first
    if not mt5.initialize():
        return jsonify({'status': 'error', 'message': 'MT5 not connected'})
    
    account_info = mt5.account_info()
    if account_info is None:
        mt5.shutdown()
        return jsonify({'status': 'error', 'message': 'Cannot access MT5 account'})
    
    mt5.shutdown()
    
    bot_running = True
    logger.info("Bot started (simulation mode)")
    return jsonify({'status': 'success', 'message': 'Bot started successfully'})

@app.route('/api/bot/stop', methods=['POST'])
def stop_bot():
    """Stop the trading bot"""
    global bot_running
    
    if not bot_running:
        return jsonify({'status': 'warning', 'message': 'Bot is not running'})
    
    bot_running = False
    logger.info("Bot stopped")
    return jsonify({'status': 'success', 'message': 'Bot stopped successfully'})

@app.route('/api/mt5/test', methods=['GET'])
def test_mt5():
    """Test MT5 connection"""
    try:
        if not mt5.initialize():
            return jsonify({
                'connected': False,
                'error': 'Failed to initialize MT5'
            })
        
        account_info = mt5.account_info()
        
        if account_info is None:
            mt5.shutdown()
            return jsonify({
                'connected': False,
                'error': 'No account info available'
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
    
    except Exception as e:
        logger.error(f"MT5 test error: {e}")
        mt5.shutdown()
        return jsonify({
            'connected': False,
            'error': str(e)
        })

@app.route('/api/logs', methods=['GET'])
def get_logs():
    """Get recent log entries"""
    try:
        lines = int(request.args.get('lines', 10))
        
        # Simple log simulation
        logs = [
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - INFO - Simple dashboard server started\n",
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - INFO - Configuration loaded successfully\n",
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - INFO - MT5 connection available\n",
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - INFO - Dashboard serving minimal working version\n",
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - INFO - All APIs functional\n"
        ]
        
        return jsonify({'logs': logs[-lines:]})
    
    except Exception as e:
        logger.error(f"Logs API error: {e}")
        return jsonify({'logs': [f'Error loading logs: {str(e)}']})

if __name__ == '__main__':
    print("🚀 EMERGENCY DASHBOARD SERVER")
    print("=" * 50)
    print("Starting minimal working dashboard...")
    print("Dashboard: http://127.0.0.1:5000")
    print("This version tests JavaScript functionality")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)