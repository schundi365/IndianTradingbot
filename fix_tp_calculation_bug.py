"""
Fix TP Calculation Bug for Split Orders
Adds pip-based TP support to calculate_multiple_take_profits method
"""

import re

# Read the current file
with open('src/mt5_trading_bot.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the calculate_multiple_take_profits method
old_method = '''    def calculate_multiple_take_profits(self, entry_price, stop_loss, direction, ratios=None):
        """
        Calculate multiple take profit levels for partial closing
        
        Args:
            entry_price (float): Entry price
            stop_loss (float): Stop loss price
            direction (int): 1 for buy, -1 for sell
            ratios (list): List of risk:reward ratios (uses self.tp_levels if None)
            
        Returns:
            list: List of take profit prices
        """
        if ratios is None:
            ratios = self.tp_levels
        
        risk = abs(entry_price - stop_loss)
        tp_prices = []
        
        for ratio in ratios:
            reward = risk * ratio
            
            if direction == 1:  # Buy
                tp = entry_price + reward
            else:  # Sell
                tp = entry_price - reward
            
            tp_prices.append(tp)
        
        return tp_prices'''

new_method = '''    def calculate_multiple_take_profits(self, entry_price, stop_loss, direction, ratios=None, symbol=None):
        """
        Calculate multiple take profit levels for partial closing
        
        Args:
            entry_price (float): Entry price
            stop_loss (float): Stop loss price
            direction (int): 1 for buy, -1 for sell
            ratios (list): List of risk:reward ratios (uses self.tp_levels if None)
            symbol (str): Trading symbol (required for pip-based calculation)
            
        Returns:
            list: List of take profit prices
        """
        if ratios is None:
            ratios = self.tp_levels
        
        # Check if using pip-based TP
        if self.config.get('use_pip_based_tp', False) and symbol:
            tp_pips_base = self.config.get('tp_pips', 100)
            tp_prices = []
            
            # Calculate TP for each level using pip multipliers
            for i, ratio in enumerate(ratios):
                # Multiply base pips by the ratio
                tp_pips = tp_pips_base * ratio
                tp = self.calculate_price_from_pips(symbol, entry_price, tp_pips, direction, is_sl=False)
                tp_prices.append(tp)
                
                logging.info(f"  TP Level {i+1}: {tp_pips:.1f} pips (ratio {ratio}) = {tp:.5f}")
            
            return tp_prices
        
        # Default: Risk:reward ratio based TP
        risk = abs(entry_price - stop_loss)
        tp_prices = []
        
        logging.info(f"  Using ratio-based TP calculation:")
        logging.info(f"    Entry: {entry_price}, SL: {stop_loss}, Risk: {risk:.5f}")
        
        for i, ratio in enumerate(ratios):
            reward = risk * ratio
            
            if direction == 1:  # Buy
                tp = entry_price + reward
            else:  # Sell
                tp = entry_price - reward
            
            tp_prices.append(tp)
            logging.info(f"    TP Level {i+1}: ratio {ratio}, reward {reward:.5f} = {tp:.5f}")
        
        return tp_prices'''

# Replace the method
if old_method in content:
    content = content.replace(old_method, new_method)
    print("✓ Updated calculate_multiple_take_profits method")
else:
    print("✗ Could not find calculate_multiple_take_profits method to replace")
    print("  The method may have been modified. Manual update required.")
    exit(1)

# Now update the call to include symbol parameter
old_call = "tp_prices = self.calculate_multiple_take_profits(entry_price, stop_loss, direction)"
new_call = "tp_prices = self.calculate_multiple_take_profits(entry_price, stop_loss, direction, symbol=symbol)"

content = content.replace(old_call, new_call)
print("✓ Updated calculate_multiple_take_profits call to include symbol parameter")

# Create backup
import shutil
from datetime import datetime
backup_file = f'src/mt5_trading_bot.py_backup_tp_fix_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
shutil.copy('src/mt5_trading_bot.py', backup_file)
print(f"✓ Created backup: {backup_file}")

# Write the updated content
with open('src/mt5_trading_bot.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n" + "="*80)
print("TP CALCULATION FIX APPLIED SUCCESSFULLY")
print("="*80)
print("\nChanges made:")
print("  1. Added 'symbol' parameter to calculate_multiple_take_profits()")
print("  2. Added pip-based TP calculation support for split orders")
print("  3. Added detailed logging for TP calculations")
print("  4. Updated method call to pass symbol parameter")
print("\nNext steps:")
print("  1. Restart the bot to apply changes")
print("  2. Monitor logs for TP calculation details")
print("  3. Verify TP values are correct in new trades")
