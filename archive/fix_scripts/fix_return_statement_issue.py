#!/usr/bin/env python3
"""
Fix Return Statement Issue

The ADX calculation was inserted after a return statement,
causing indentation errors. We need to fix the function structure.
"""

import os
import shutil
from datetime import datetime

def backup_file(filepath):
    """Create backup of file before modification"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{filepath}_backup_return_fix_{timestamp}"
    shutil.copy2(filepath, backup_path)
    print(f"✅ Backup created: {backup_path}")
    return backup_path

def fix_return_statement_issue():
    """
    Fix the return statement issue in calculate_indicators
    """
    filepath = "src/mt5_trading_bot.py"
    
    # Create backup
    backup_path = backup_file(filepath)
    
    # Read current file
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the problematic section
    # Look for the pattern where return df is followed by more code
    problem_pattern = '''        return df
            
            # Check error type
            error = mt5.last_error()'''
    
    if problem_pattern in content:
        print("🔍 Found the problematic return statement pattern")
        
        # Remove everything after the return df in calculate_indicators
        # Find the calculate_indicators method
        calc_indicators_start = content.find('def calculate_indicators(self, df):')
        if calc_indicators_start == -1:
            print("❌ Could not find calculate_indicators method")
            return False
        
        # Find the return df statement
        return_df_pos = content.find('        return df', calc_indicators_start)
        if return_df_pos == -1:
            print("❌ Could not find return df statement")
            return False
        
        # Find the next method definition after return df
        next_method_pos = content.find('\n    def ', return_df_pos)
        if next_method_pos == -1:
            print("❌ Could not find next method")
            return False
        
        # Extract the problematic code between return df and next method
        problematic_code = content[return_df_pos + len('        return df'):next_method_pos]
        
        print("🗑️ Removing problematic code after return df:")
        print(f"   Length: {len(problematic_code)} characters")
        print(f"   Preview: {problematic_code[:100]}...")
        
        # Remove the problematic code
        fixed_content = (content[:return_df_pos + len('        return df')] + 
                        content[next_method_pos:])
        
        # Write the fixed content
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        print("✅ Fixed return statement issue")
        return True
    else:
        print("❌ Could not find the problematic pattern")
        return False

def add_adx_calculation_properly():
    """
    Add ADX calculation properly before the return statement
    """
    filepath = "src/mt5_trading_bot.py"
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the return df statement in calculate_indicators
    return_pattern = '        return df'
    
    if return_pattern in content:
        # Add ADX calculation before the return
        adx_code = '''
        # ADX (Average Directional Index) for trend strength
        if self.config.get('use_adx', True):
            try:
                # Calculate True Range components (reuse existing TR if available)
                if 'tr' not in df.columns:
                    high_low = df['high'] - df['low']
                    high_close = np.abs(df['high'] - df['close'].shift())
                    low_close = np.abs(df['low'] - df['close'].shift())
                    df['tr'] = df[['high_low', 'high_close', 'low_close']].max(axis=1)
                
                # Directional Movement
                plus_dm = np.where((df['high'] - df['high'].shift()) > (df['low'].shift() - df['low']), 
                                 np.maximum(df['high'] - df['high'].shift(), 0), 0)
                minus_dm = np.where((df['low'].shift() - df['low']) > (df['high'] - df['high'].shift()), 
                                  np.maximum(df['low'].shift() - df['low'], 0), 0)
                
                # Smooth the values
                adx_period = self.config.get('adx_period', 14)
                tr_smooth = df['tr'].rolling(window=adx_period).mean()
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
        
        # Replace the return statement with ADX calculation + return
        content = content.replace(return_pattern, adx_code)
        
        # Write the updated content
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Added ADX calculation properly before return statement")
        return True
    else:
        print("❌ Could not find return df statement")
        return False

if __name__ == "__main__":
    print("🔧 Fixing Return Statement Issue...")
    print("="*60)
    
    # First fix the return statement issue
    if fix_return_statement_issue():
        print("\n✅ RETURN STATEMENT ISSUE FIXED!")
        
        # Now add ADX calculation properly
        print("\n🔧 Adding ADX calculation properly...")
        if add_adx_calculation_properly():
            print("✅ ADX calculation added correctly")
        else:
            print("❌ Failed to add ADX calculation")
            
    else:
        print("\n❌ RETURN STATEMENT FIX FAILED!")
    
    print("\n🔄 Test the fix with: python test_adx_fix.py")