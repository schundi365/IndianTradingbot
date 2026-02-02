#!/usr/bin/env python3
"""
Fix ADX KeyError in Enhanced Signal Generation

The enhanced signal generation code is trying to access 'adx' column
that doesn't exist because ADX is not calculated in calculate_indicators.
We need to fix the ADX filter section to handle missing ADX properly.
"""

import os
import shutil
from datetime import datetime

def backup_file(filepath):
    """Create backup of file before modification"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{filepath}_backup_adx_fix_{timestamp}"
    shutil.copy2(filepath, backup_path)
    print(f"✅ Backup created: {backup_path}")
    return backup_path

def fix_adx_error():
    """
    Fix the ADX KeyError by properly handling missing ADX column
    """
    filepath = "src/mt5_trading_bot.py"
    
    # Create backup
    backup_path = backup_file(filepath)
    
    # Read current file
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the problematic ADX section
    old_adx_code = '''            if not pd.isna(latest['adx']):
                adx = latest['adx']
                plus_di = latest.get('plus_di', 0)
                minus_di = latest.get('minus_di', 0)'''
    
    # Replace with safe ADX access
    new_adx_code = '''            if 'adx' in df.columns and not pd.isna(latest['adx']):
                adx = latest['adx']
                plus_di = latest.get('plus_di', 0)
                minus_di = latest.get('minus_di', 0)'''
    
    if old_adx_code in content:
        content = content.replace(old_adx_code, new_adx_code)
        print("✅ Fixed ADX column access")
    else:
        print("⚠️ ADX access pattern not found, trying alternative fix...")
        
        # Alternative fix - look for the broader pattern
        old_pattern = '''        # Apply ADX trend direction filter (MISSING FROM ORIGINAL - NOW ADDED)
        logging.info("-"*80)
        logging.info("🔍 ADX TREND DIRECTION FILTER:")
        if self.config.get('use_adx', True):
            # Calculate ADX and directional indicators if not already present
            if 'adx' not in df.columns:'''
        
        new_pattern = '''        # Apply ADX trend direction filter (MISSING FROM ORIGINAL - NOW ADDED)
        logging.info("-"*80)
        logging.info("🔍 ADX TREND DIRECTION FILTER:")
        if self.config.get('use_adx', True):
            # Calculate ADX and directional indicators if not already present
            if 'adx' not in df.columns:'''
        
        # The issue is that we're calculating ADX but not storing it properly
        # Let's find the ADX calculation section and fix it
        adx_calc_section = '''                # Calculate DX and ADX
                dx = 100 * np.abs(df['plus_di'] - df['minus_di']) / (df['plus_di'] + df['minus_di'])
                df['adx'] = dx.rolling(window=adx_period).mean()'''
        
        if adx_calc_section in content:
            print("✅ ADX calculation section found")
            # The calculation is there, the issue is with accessing it
            # Let's fix the access pattern more broadly
            
            # Find and replace the problematic line
            problematic_line = "if not pd.isna(latest['adx']):"
            safe_line = "if 'adx' in df.columns and not pd.isna(latest['adx']):"
            
            if problematic_line in content:
                content = content.replace(problematic_line, safe_line)
                print("✅ Fixed ADX access pattern")
            else:
                print("❌ Could not find problematic ADX access line")
                return False
        else:
            print("❌ ADX calculation section not found")
            return False
    
    # Also fix any other potential ADX column access issues
    other_adx_patterns = [
        ("latest['plus_di']", "latest.get('plus_di', 0)"),
        ("latest['minus_di']", "latest.get('minus_di', 0)")
    ]
    
    for old_pattern, new_pattern in other_adx_patterns:
        if old_pattern in content:
            content = content.replace(old_pattern, new_pattern)
            print(f"✅ Fixed {old_pattern} access")
    
    # Write the updated content
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ ADX error fix applied to {filepath}")
    return True

def add_adx_to_indicators():
    """
    Alternative solution: Add ADX calculation to calculate_indicators method
    """
    filepath = "src/mt5_trading_bot.py"
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the end of calculate_indicators method
    # Look for the return statement
    indicators_end_pattern = '''        return df'''
    
    if indicators_end_pattern in content:
        # Add ADX calculation before the return
        adx_calculation = '''
        # ADX (Average Directional Index) for trend strength
        if self.config.get('use_adx', True):
            try:
                # Calculate True Range components
                high_low = df['high'] - df['low']
                high_close = np.abs(df['high'] - df['close'].shift())
                low_close = np.abs(df['low'] - df['close'].shift())
                tr = df[['high_low', 'high_close', 'low_close']].max(axis=1)
                
                # Directional Movement
                plus_dm = np.where((df['high'] - df['high'].shift()) > (df['low'].shift() - df['low']), 
                                 np.maximum(df['high'] - df['high'].shift(), 0), 0)
                minus_dm = np.where((df['low'].shift() - df['low']) > (df['high'] - df['high'].shift()), 
                                  np.maximum(df['low'].shift() - df['low'], 0), 0)
                
                # Smooth the values
                adx_period = self.config.get('adx_period', 14)
                tr_smooth = pd.Series(tr).rolling(window=adx_period).mean()
                plus_dm_smooth = pd.Series(plus_dm).rolling(window=adx_period).mean()
                minus_dm_smooth = pd.Series(minus_dm).rolling(window=adx_period).mean()
                
                # Calculate DI
                df['plus_di'] = 100 * (plus_dm_smooth / tr_smooth)
                df['minus_di'] = 100 * (minus_dm_smooth / tr_smooth)
                
                # Calculate DX and ADX
                dx = 100 * np.abs(df['plus_di'] - df['minus_di']) / (df['plus_di'] + df['minus_di'])
                df['adx'] = dx.rolling(window=adx_period).mean()
                
                # Fill NaN values with 0 for safety
                df['adx'] = df['adx'].fillna(0)
                df['plus_di'] = df['plus_di'].fillna(0)
                df['minus_di'] = df['minus_di'].fillna(0)
                
            except Exception as e:
                logging.warning(f"ADX calculation failed: {e}")
                # Set default values if calculation fails
                df['adx'] = 0
                df['plus_di'] = 0
                df['minus_di'] = 0

        return df'''
        
        content = content.replace(indicators_end_pattern, adx_calculation)
        
        # Write the updated content
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Added ADX calculation to calculate_indicators method")
        return True
    else:
        print("❌ Could not find calculate_indicators return statement")
        return False

if __name__ == "__main__":
    print("🔧 Fixing ADX KeyError...")
    print("="*50)
    
    # Try the safe access fix first
    if fix_adx_error():
        print("\n✅ ADX ERROR FIX COMPLETE!")
        print("The bot should now handle missing ADX columns safely.")
        
        # Also add ADX calculation to prevent the issue
        print("\n🔧 Adding ADX calculation to indicators...")
        if add_adx_to_indicators():
            print("✅ ADX calculation added to calculate_indicators")
        else:
            print("⚠️ Could not add ADX calculation, but safe access is implemented")
            
    else:
        print("\n❌ ADX ERROR FIX FAILED!")
        print("Please check the file manually")
    
    print("\n🔄 Restart the bot to apply the fix")
    print("The enhanced signal generation should now work without ADX errors.")