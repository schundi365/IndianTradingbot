#!/usr/bin/env python3
"""
Implement Enhanced Logging System
Adds detailed logging with line numbers, timestamps, and performance tracking
"""

import os
import shutil
from datetime import datetime

def backup_file(filepath):
    """Create backup of file before modification"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{filepath}_backup_enhanced_logging_{timestamp}"
    shutil.copy2(filepath, backup_path)
    print(f"✅ Backup created: {backup_path}")
    return backup_path

def implement_enhanced_logging():
    """
    Implement enhanced logging system in the trading bot
    """
    filepath = "src/mt5_trading_bot.py"
    
    # Create backup
    backup_path = backup_file(filepath)
    
    # Read current file
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Add enhanced logging imports at the top
    import_section = '''import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import logging
import sys
from pathlib import Path'''
    
    enhanced_imports = '''import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import logging
import sys
import inspect
import functools
from pathlib import Path'''
    
    content = content.replace(import_section, enhanced_imports)
    print("✅ Added enhanced logging imports")
    
    # 2. Add enhanced logging formatter class after imports
    logging_setup_pattern = '''# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)'''
    
    enhanced_logging_setup = '''# Enhanced Logging System
class EnhancedFormatter(logging.Formatter):
    """Enhanced formatter with line numbers and performance timing"""
    
    def format(self, record):
        # Add line number and filename info
        if hasattr(record, 'pathname') and hasattr(record, 'lineno'):
            filename = os.path.basename(record.pathname)
            record.location = f"[{filename}:{record.lineno}]"
        else:
            record.location = "[unknown]"
        
        # Format with enhanced info
        formatted = f"{self.formatTime(record)} - {record.levelname} - {record.location} {record.getMessage()}"
        return formatted

# Setup enhanced logging
formatter = EnhancedFormatter()
file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
file_handler.setFormatter(formatter)
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

logging.basicConfig(
    level=logging.INFO,
    handlers=[file_handler, console_handler]
)

# Performance timing decorator
def performance_timer(func):
    """Decorator to measure function execution time"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logging.info(f"⏱️ {func.__name__} completed in {execution_time:.3f}s")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logging.error(f"❌ {func.__name__} failed after {execution_time:.3f}s: {e}")
            raise
    return wrapper'''
    
    content = content.replace(logging_setup_pattern, enhanced_logging_setup)
    print("✅ Added enhanced logging system")
    
    # 3. Add performance timing to key methods
    methods_to_time = [
        'def connect(self):',
        'def get_historical_data(self, symbol, timeframe, bars=200):',
        'def calculate_indicators(self, df):'
    ]
    
    for method in methods_to_time:
        if method in content:
            enhanced_method = method.replace('def ', '@performance_timer\n    def ')
            content = content.replace(method, enhanced_method)
            print(f"✅ Added performance timing to {method.split('(')[0].replace('def ', '')}")
    
    # 4. Add detailed indicator logging to check_entry_signal method
    signal_analysis_pattern = '''        # Log detailed market data
        logging.info("="*80)
        logging.info("📊 SIGNAL ANALYSIS - DETAILED CALCULATIONS")
        logging.info("="*80)'''
    
    if signal_analysis_pattern in content:
        detailed_indicator_logging = '''        # Log detailed market data
        logging.info("="*80)
        logging.info("📊 SIGNAL ANALYSIS - DETAILED CALCULATIONS")
        logging.info("="*80)
        
        # 🔧 DETAILED TECHNICAL INDICATOR VALUES
        logging.info("🔧 DETAILED TECHNICAL INDICATOR VALUES:")
        logging.info("-" * 60)
        if 'fast_ma' in df.columns:
            logging.info(f"   Fast MA ({self.fast_ma_period}): {latest['fast_ma']:.5f}")
        if 'slow_ma' in df.columns:
            logging.info(f"   Slow MA ({self.slow_ma_period}): {latest['slow_ma']:.5f}")
        if 'atr' in df.columns:
            logging.info(f"   ATR ({self.atr_period}): {latest['atr']:.5f}")
        if 'rsi' in df.columns:
            logging.info(f"   RSI (14): {latest['rsi']:.2f}")
        if 'macd' in df.columns:
            logging.info(f"   MACD ({self.macd_fast},{self.macd_slow}): {latest['macd']:.6f}")
        if 'macd_signal' in df.columns:
            logging.info(f"   MACD Signal ({self.macd_signal}): {latest['macd_signal']:.6f}")
        if 'macd_histogram' in df.columns:
            logging.info(f"   MACD Histogram: {latest['macd_histogram']:.6f}")
        logging.info("-" * 60)'''
        
        content = content.replace(signal_analysis_pattern, detailed_indicator_logging)
        print("✅ Added detailed indicator logging")
    
    # 5. Enhance volume analysis logging
    volume_pattern = '''        # === VOLUME ANALYSIS ===
        confidence_adjustment = 0.0
        if self.use_volume_filter and self.volume_analyzer:
            logging.info("="*80)
            logging.info(f"📊 VOLUME ANALYSIS for {symbol}")
            logging.info("="*80)'''
    
    if volume_pattern in content:
        enhanced_volume_logging = '''        # === VOLUME ANALYSIS ===
        confidence_adjustment = 0.0
        if self.use_volume_filter and self.volume_analyzer:
            logging.info("="*80)
            logging.info(f"📊 VOLUME ANALYSIS for {symbol}")
            logging.info("="*80)
            
            # Enhanced volume breakdown logging
            current_volume = df.iloc[-1]['tick_volume'] if 'tick_volume' in df.columns else 0
            avg_volume = df['tick_volume'].rolling(20).mean().iloc[-1] if 'tick_volume' in df.columns else 0
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 0
            
            logging.info(f"📊 DETAILED VOLUME BREAKDOWN:")
            logging.info(f"   Current Volume: {current_volume:,.0f}")
            logging.info(f"   Average Volume (20): {avg_volume:,.0f}")
            logging.info(f"   Volume Ratio: {volume_ratio:.2f}")
            logging.info(f"   Volume Threshold: {self.volume_analyzer.min_volume_ma}")
            logging.info(f"   Volume Classification: {'HIGH' if volume_ratio > 1.5 else 'NORMAL' if volume_ratio > 0.7 else 'LOW'}")
            logging.info(f"   Volume Filter Status: {'PASS' if volume_ratio >= self.volume_analyzer.min_volume_ma else 'FAIL'}")'''
        
        content = content.replace(volume_pattern, enhanced_volume_logging)
        print("✅ Enhanced volume analysis logging")
    
    # Write the updated content
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Enhanced logging implemented in {filepath}")
    return True

def add_dashboard_logging_controls():
    """
    Add logging level controls to the web dashboard
    """
    dashboard_file = "templates/dashboard.html"
    
    with open(dashboard_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if logging controls already exist
    if "logging_level" in content:
        print("✅ Logging level controls already present in dashboard")
        return True
    
    # Find a good place to add system settings - look for the last card
    card_pattern = '''                </div>
            </div>
        </div>
    </div>

    <!-- Bootstrap JS -->'''
    
    if card_pattern in content:
        # Add logging controls before the closing div
        logging_controls_section = '''                </div>
            </div>
            
            <!-- System Settings Card -->
            <div class="card mb-4">
                <div class="card-header">
                    <h5 class="mb-0">System Settings</h5>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6">
                            <div class="form-group">
                                <label for="logging_level">Logging Level</label>
                                <select class="form-control" id="logging_level" name="logging_level">
                                    <option value="minimal">Minimal (Errors only)</option>
                                    <option value="standard" selected>Standard (Basic info)</option>
                                    <option value="detailed">Detailed (Full analysis)</option>
                                    <option value="debug">Debug (Everything)</option>
                                </select>
                                <small class="form-text text-muted">
                                    Controls how much detail is logged. Changes apply immediately.
                                </small>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="form-group">
                                <label>Performance Impact</label>
                                <div class="alert alert-info">
                                    <small>
                                        <strong>Minimal:</strong> Fastest performance<br>
                                        <strong>Standard:</strong> Good balance<br>
                                        <strong>Detailed:</strong> Full indicator values<br>
                                        <strong>Debug:</strong> Maximum detail
                                    </small>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-12">
                            <button type="button" class="btn btn-primary" onclick="updateLoggingLevel()">
                                Apply Logging Level
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Bootstrap JS -->'''
        
        content = content.replace(card_pattern, logging_controls_section)
        
        # Add JavaScript function for logging level updates
        js_pattern = '''    <script>
        // Configuration form handling'''
        
        if js_pattern in content:
            enhanced_js = '''    <script>
        // Logging level update function
        function updateLoggingLevel() {
            const level = document.getElementById('logging_level').value;
            
            fetch('/api/config/logging_level', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({logging_level: level})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showAlert('success', 'Logging level updated to: ' + level);
                } else {
                    showAlert('danger', 'Failed to update logging level: ' + data.error);
                }
            })
            .catch(error => {
                showAlert('danger', 'Error updating logging level: ' + error);
            });
        }
        
        // Configuration form handling'''
            
            content = content.replace(js_pattern, enhanced_js)
        
        # Write the updated content
        with open(dashboard_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Added logging level controls to dashboard")
        return True
    else:
        print("⚠️ Could not find insertion point in dashboard")
        return False

def add_dashboard_api_support():
    """
    Add API support for logging level control in web_dashboard.py
    """
    dashboard_py = "web_dashboard.py"
    
    with open(dashboard_py, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add logging level API endpoint
    api_pattern = '''@app.route('/api/config/save', methods=['POST'])
def save_config():'''
    
    if api_pattern in content:
        logging_api = '''@app.route('/api/config/logging_level', methods=['POST'])
def update_logging_level():
    """Update logging level dynamically"""
    try:
        data = request.get_json()
        level = data.get('logging_level', 'standard')
        
        # Update logging level in bot configuration
        if 'bot_config' in globals():
            bot_config['logging_level'] = level
            
            # Save to config file
            with open(CONFIG_FILE, 'w') as f:
                json.dump(bot_config, f, indent=4)
            
            # Update logging level in running bot if available
            if 'bot_instance' in globals() and bot_instance:
                bot_instance.logging_level = level
                logging.info(f"Logging level updated to: {level}")
        
        return jsonify({
            'success': True,
            'message': f'Logging level updated to {level}',
            'level': level
        })
        
    except Exception as e:
        logging.error(f"Error updating logging level: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/config/save', methods=['POST'])
def save_config():'''
        
        content = content.replace(api_pattern, logging_api)
        
        # Write the updated content
        with open(dashboard_py, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Added logging level API support to web dashboard")
        return True
    else:
        print("⚠️ Could not find API insertion point in web_dashboard.py")
        return False

if __name__ == "__main__":
    print("🔧 Implementing Enhanced Logging System...")
    print("="*60)
    
    success = True
    
    # 1. Implement enhanced logging in trading bot
    if implement_enhanced_logging():
        print("✅ Enhanced logging implemented in trading bot")
    else:
        print("❌ Failed to implement enhanced logging in trading bot")
        success = False
    
    # 2. Add dashboard controls
    if add_dashboard_logging_controls():
        print("✅ Dashboard logging controls added")
    else:
        print("❌ Failed to add dashboard logging controls")
        success = False
    
    # 3. Add API support
    if add_dashboard_api_support():
        print("✅ Dashboard API support added")
    else:
        print("❌ Failed to add dashboard API support")
        success = False
    
    if success:
        print("\n🎉 ENHANCED LOGGING SYSTEM IMPLEMENTED!")
        print("\n📊 FEATURES ADDED:")
        print("• Line numbers and file names in logs")
        print("• Performance timing for key methods")
        print("• Detailed MACD, RSI, ATR values")
        print("• Enhanced volume analysis breakdown")
        print("• Dashboard logging level controls")
        print("• Real-time logging level updates")
        
        print("\n🔄 NEXT STEPS:")
        print("1. Clear cache: python clear_all_cache.py")
        print("2. Restart bot: python run_bot.py")
        print("3. Restart dashboard: python web_dashboard.py")
        print("4. Check logs for enhanced output")
        print("5. Use dashboard to control logging levels")
        
    else:
        print("\n❌ ENHANCED LOGGING IMPLEMENTATION INCOMPLETE!")
        print("Some features may not work correctly.")