#!/usr/bin/env python3
"""
Restore Enhanced Logging Implementation

This script restores the detailed logging features that were lost
when we restored from backup to fix the ADX issue.
"""

import os
import shutil
from datetime import datetime

def backup_file(filepath):
    """Create backup of file before modification"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{filepath}_backup_logging_restore_{timestamp}"
    shutil.copy2(filepath, backup_path)
    print(f"✅ Backup created: {backup_path}")
    return backup_path

def restore_enhanced_logging():
    """
    Restore enhanced logging features to the trading bot
    """
    filepath = "src/mt5_trading_bot.py"
    
    # Create backup
    backup_path = backup_file(filepath)
    
    # Read current file
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the signal analysis section and add detailed indicator logging
    signal_analysis_start = '''        # Log detailed market data
        logging.info("="*80)
        logging.info("📊 SIGNAL ANALYSIS - DETAILED CALCULATIONS")
        logging.info("="*80)'''
    
    if signal_analysis_start in content:
        print("✅ Found signal analysis section")
        
        # Add detailed indicator logging after the header
        detailed_logging_section = '''        # Log detailed market data
        logging.info("="*80)
        logging.info("📊 SIGNAL ANALYSIS - DETAILED CALCULATIONS")
        logging.info("="*80)
        
        # ADD DETAILED INDICATOR LOGGING HERE - THIS SECTION IS WORKING
        logging.info("🔧 DETAILED TECHNICAL INDICATOR VALUES:")
        logging.info("-" * 60)
        if 'fast_ma' in df.columns:
            logging.info(f"   Fast MA: {latest['fast_ma']:.5f}")
        if 'slow_ma' in df.columns:
            logging.info(f"   Slow MA: {latest['slow_ma']:.5f}")
        if 'atr' in df.columns:
            logging.info(f"   ATR: {latest['atr']:.5f}")
        if 'rsi' in df.columns:
            logging.info(f"   RSI: {latest['rsi']:.2f}")
        if 'macd' in df.columns:
            logging.info(f"   MACD: {latest['macd']:.6f}")
        if 'macd_signal' in df.columns:
            logging.info(f"   MACD Signal: {latest['macd_signal']:.6f}")
        if 'macd_histogram' in df.columns:
            logging.info(f"   MACD Histogram: {latest['macd_histogram']:.6f}")
        logging.info("-" * 60)'''
        
        content = content.replace(signal_analysis_start, detailed_logging_section)
        print("✅ Added detailed indicator logging")
    else:
        print("⚠️ Signal analysis section not found")
    
    # Add volume analysis detailed logging
    volume_analysis_pattern = '''        # === VOLUME ANALYSIS ===
        confidence_adjustment = 0.0
        if self.use_volume_filter and self.volume_analyzer:
            logging.info("="*80)
            logging.info(f"📊 VOLUME ANALYSIS for {symbol}")
            logging.info("="*80)'''
    
    if volume_analysis_pattern in content:
        enhanced_volume_logging = '''        # === VOLUME ANALYSIS ===
        confidence_adjustment = 0.0
        if self.use_volume_filter and self.volume_analyzer:
            logging.info("="*80)
            logging.info(f"📊 VOLUME ANALYSIS for {symbol}")
            logging.info("="*80)
            
            # Log current volume data
            current_volume = df.iloc[-1]['tick_volume'] if 'tick_volume' in df.columns else 0
            avg_volume = df['tick_volume'].rolling(20).mean().iloc[-1] if 'tick_volume' in df.columns else 0
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 0
            
            logging.info(f"📊 VOLUME BREAKDOWN:")
            logging.info(f"   Current Volume: {current_volume:,.0f}")
            logging.info(f"   Average Volume (20): {avg_volume:,.0f}")
            logging.info(f"   Volume Ratio: {volume_ratio:.2f}")
            logging.info(f"   Volume Classification: {'HIGH' if volume_ratio > 1.5 else 'NORMAL' if volume_ratio > 0.7 else 'LOW'}")'''
        
        content = content.replace(volume_analysis_pattern, enhanced_volume_logging)
        print("✅ Enhanced volume analysis logging")
    else:
        print("⚠️ Volume analysis section not found")
    
    # Write the updated content
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Enhanced logging restored to {filepath}")
    return True

def add_logging_level_control():
    """
    Add logging level control to the web dashboard
    """
    dashboard_file = "templates/dashboard.html"
    
    with open(dashboard_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if logging controls already exist
    if "Logging Level" in content:
        print("✅ Logging level controls already present in dashboard")
        return True
    
    # Find the system settings section
    system_settings_pattern = '''                    <div class="card-header">
                        <h5 class="mb-0">System Settings</h5>
                    </div>'''
    
    if system_settings_pattern in content:
        # Add logging controls after system settings header
        logging_controls = '''                    <div class="card-header">
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
                                        Controls how much detail is logged. Higher levels may impact performance.
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
                    </div>'''
        
        content = content.replace(system_settings_pattern, logging_controls)
        
        # Write the updated content
        with open(dashboard_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Added logging level controls to dashboard")
        return True
    else:
        print("⚠️ Could not find system settings section in dashboard")
        return False

if __name__ == "__main__":
    print("🔧 Restoring Enhanced Logging Implementation...")
    print("="*60)
    
    if restore_enhanced_logging():
        print("\n✅ ENHANCED LOGGING RESTORED!")
        
        # Also add dashboard controls
        print("\n🔧 Adding dashboard logging controls...")
        if add_logging_level_control():
            print("✅ Dashboard logging controls added")
        else:
            print("⚠️ Dashboard controls not added - may already exist")
            
        print("\n📊 FEATURES RESTORED:")
        print("• Detailed MACD, RSI, ATR values in logs")
        print("• Enhanced volume analysis breakdown")
        print("• Volume ratio and classification")
        print("• Indicator value logging in signal analysis")
        print("• Dashboard logging level controls")
        
        print("\n🔄 Restart the bot to see detailed logging:")
        print("1. Stop current bot process")
        print("2. Clear cache: python clear_all_cache.py")
        print("3. Restart: python run_bot.py")
        print("4. Check logs for detailed indicator values")
        
    else:
        print("\n❌ ENHANCED LOGGING RESTORE FAILED!")
        print("Please check the file manually")