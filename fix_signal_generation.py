#!/usr/bin/env python3
"""
Fix Signal Generation Issue

The bot is only looking for MA crossovers and trend confirmations,
but these are rare events. We need to add more signal generation
conditions to make the bot more responsive to market opportunities.

Current Issues:
1. Only generates signals on MA crossovers (rare)
2. Only generates signals on trend changes (rare)
3. Missing momentum-based signals
4. Missing pullback/retracement signals
5. Missing breakout signals

Solution: Add multiple signal generation methods
"""

import os
import shutil
from datetime import datetime

def backup_file(filepath):
    """Create backup of file before modification"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{filepath}_backup_signal_fix_{timestamp}"
    shutil.copy2(filepath, backup_path)
    print(f"✅ Backup created: {backup_path}")
    return backup_path

def fix_signal_generation():
    """
    Fix the signal generation logic to be more responsive
    """
    filepath = "src/mt5_trading_bot.py"
    
    # Create backup
    backup_path = backup_file(filepath)
    
    # Read current file
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the signal generation section that needs to be enhanced
    old_signal_logic = '''        # Check for MA crossover
        signal = 0
        logging.info("🔍 CHECKING MA CROSSOVER:")
        logging.info(f"  Previous: Fast MA={previous['fast_ma']:.5f}, Slow MA={previous['slow_ma']:.5f}")
        logging.info(f"  Current:  Fast MA={latest['fast_ma']:.5f}, Slow MA={latest['slow_ma']:.5f}")
        
        if latest['ma_cross'] == 1:
            logging.info(f"  ✅ BULLISH CROSSOVER DETECTED!")
            logging.info(f"     Fast MA crossed ABOVE Slow MA")
            logging.info(f"     Previous: Fast {previous['fast_ma']:.5f} <= Slow {previous['slow_ma']:.5f}")
            logging.info(f"     Current:  Fast {latest['fast_ma']:.5f} > Slow {latest['slow_ma']:.5f}")
            signal = 1
        elif latest['ma_cross'] == -1:
            logging.info(f"  ✅ BEARISH CROSSOVER DETECTED!")
            logging.info(f"     Fast MA crossed BELOW Slow MA")
            logging.info(f"     Previous: Fast {previous['fast_ma']:.5f} >= Slow {previous['slow_ma']:.5f}")
            logging.info(f"     Current:  Fast {latest['fast_ma']:.5f} < Slow {latest['slow_ma']:.5f}")
            signal = -1
        else:
            logging.info(f"  ❌ No crossover detected")
            logging.info(f"     MA Cross value: {latest['ma_cross']}")
        
        # Additional confirmation: price above/below both MAs
        if signal == 0:
            logging.info("-"*80)
            logging.info("🔍 CHECKING TREND CONFIRMATION:")
            logging.info(f"  Current MA Trend:  {latest['ma_trend']} (1=bullish, -1=bearish)")
            logging.info(f"  Previous MA Trend: {previous['ma_trend']}")
            logging.info(f"  Price > Fast MA:   {latest['close'] > latest['fast_ma']}")
            logging.info(f"  Price > Slow MA:   {latest['close'] > latest['slow_ma']}")
            logging.info(f"  Price < Fast MA:   {latest['close'] < latest['fast_ma']}")
            logging.info(f"  Price < Slow MA:   {latest['close'] < latest['slow_ma']}")
            
            if (latest['close'] > latest['fast_ma'] and 
                latest['close'] > latest['slow_ma'] and 
                latest['ma_trend'] == 1 and previous['ma_trend'] == -1):
                logging.info(f"  ✅ BULLISH TREND CONFIRMATION!")
                logging.info(f"     Price above both MAs AND trend changed to bullish")
                signal = 1
            elif (latest['close'] < latest['fast_ma'] and 
                  latest['close'] < latest['slow_ma'] and 
                  latest['ma_trend'] == -1 and previous['ma_trend'] == 1):
                logging.info(f"  ✅ BEARISH TREND CONFIRMATION!")
                logging.info(f"     Price below both MAs AND trend changed to bearish")
                signal = -1
            else:
                logging.info(f"  ❌ No trend confirmation")
                logging.info(f"     Conditions not met for trend-based signal")
        
        if signal == 0:
            logging.info("-"*80)
            logging.info("❌ NO SIGNAL GENERATED")
            logging.info("   Waiting for MA crossover or trend confirmation...")
            logging.info("="*80)
            return 0'''
    
    # New enhanced signal logic with multiple signal types
    new_signal_logic = '''        # ENHANCED SIGNAL GENERATION - Multiple Signal Types
        signal = 0
        signal_reason = ""
        
        # METHOD 1: MA CROSSOVER (Original - High Confidence)
        logging.info("🔍 METHOD 1: CHECKING MA CROSSOVER:")
        logging.info(f"  Previous: Fast MA={previous['fast_ma']:.5f}, Slow MA={previous['slow_ma']:.5f}")
        logging.info(f"  Current:  Fast MA={latest['fast_ma']:.5f}, Slow MA={latest['slow_ma']:.5f}")
        
        if latest['ma_cross'] == 1:
            logging.info(f"  ✅ BULLISH CROSSOVER DETECTED!")
            logging.info(f"     Fast MA crossed ABOVE Slow MA")
            logging.info(f"     Previous: Fast {previous['fast_ma']:.5f} <= Slow {previous['slow_ma']:.5f}")
            logging.info(f"     Current:  Fast {latest['fast_ma']:.5f} > Slow {latest['slow_ma']:.5f}")
            signal = 1
            signal_reason = "MA Bullish Crossover"
        elif latest['ma_cross'] == -1:
            logging.info(f"  ✅ BEARISH CROSSOVER DETECTED!")
            logging.info(f"     Fast MA crossed BELOW Slow MA")
            logging.info(f"     Previous: Fast {previous['fast_ma']:.5f} >= Slow {previous['slow_ma']:.5f}")
            logging.info(f"     Current:  Fast {latest['fast_ma']:.5f} < Slow {latest['slow_ma']:.5f}")
            signal = -1
            signal_reason = "MA Bearish Crossover"
        else:
            logging.info(f"  ❌ No crossover detected")
            logging.info(f"     MA Cross value: {latest['ma_cross']}")
        
        # METHOD 2: TREND CONFIRMATION (Original - High Confidence)
        if signal == 0:
            logging.info("-"*80)
            logging.info("🔍 METHOD 2: CHECKING TREND CONFIRMATION:")
            logging.info(f"  Current MA Trend:  {latest['ma_trend']} (1=bullish, -1=bearish)")
            logging.info(f"  Previous MA Trend: {previous['ma_trend']}")
            logging.info(f"  Price > Fast MA:   {latest['close'] > latest['fast_ma']}")
            logging.info(f"  Price > Slow MA:   {latest['close'] > latest['slow_ma']}")
            logging.info(f"  Price < Fast MA:   {latest['close'] < latest['fast_ma']}")
            logging.info(f"  Price < Slow MA:   {latest['close'] < latest['slow_ma']}")
            
            if (latest['close'] > latest['fast_ma'] and 
                latest['close'] > latest['slow_ma'] and 
                latest['ma_trend'] == 1 and previous['ma_trend'] == -1):
                logging.info(f"  ✅ BULLISH TREND CONFIRMATION!")
                logging.info(f"     Price above both MAs AND trend changed to bullish")
                signal = 1
                signal_reason = "Bullish Trend Confirmation"
            elif (latest['close'] < latest['fast_ma'] and 
                  latest['close'] < latest['slow_ma'] and 
                  latest['ma_trend'] == -1 and previous['ma_trend'] == 1):
                logging.info(f"  ✅ BEARISH TREND CONFIRMATION!")
                logging.info(f"     Price below both MAs AND trend changed to bearish")
                signal = -1
                signal_reason = "Bearish Trend Confirmation"
            else:
                logging.info(f"  ❌ No trend confirmation")
                logging.info(f"     Conditions not met for trend-based signal")
        
        # METHOD 3: MOMENTUM SIGNALS (New - Medium Confidence)
        if signal == 0:
            logging.info("-"*80)
            logging.info("🔍 METHOD 3: CHECKING MOMENTUM SIGNALS:")
            
            # Check if we have RSI and MACD data for momentum analysis
            if not pd.isna(latest['rsi']) and not pd.isna(latest['macd_histogram']):
                rsi = latest['rsi']
                macd_hist = latest['macd_histogram']
                macd_hist_prev = previous['macd_histogram'] if not pd.isna(previous['macd_histogram']) else 0
                
                logging.info(f"  RSI: {rsi:.2f}")
                logging.info(f"  MACD Histogram: {macd_hist:.6f}")
                logging.info(f"  MACD Hist Previous: {macd_hist_prev:.6f}")
                
                # BULLISH MOMENTUM: RSI oversold recovery + MACD turning positive
                if (rsi > 30 and rsi < 60 and  # RSI recovering from oversold
                    macd_hist > 0 and macd_hist > macd_hist_prev and  # MACD histogram improving
                    latest['close'] > latest['fast_ma'] and  # Price above fast MA
                    latest['fast_ma'] > latest['slow_ma']):  # Bullish MA alignment
                    
                    logging.info(f"  ✅ BULLISH MOMENTUM SIGNAL!")
                    logging.info(f"     RSI {rsi:.2f} recovering from oversold")
                    logging.info(f"     MACD histogram improving: {macd_hist:.6f} > {macd_hist_prev:.6f}")
                    logging.info(f"     Price above fast MA in bullish trend")
                    signal = 1
                    signal_reason = "Bullish Momentum Recovery"
                
                # BEARISH MOMENTUM: RSI overbought decline + MACD turning negative
                elif (rsi < 70 and rsi > 40 and  # RSI declining from overbought
                      macd_hist < 0 and macd_hist < macd_hist_prev and  # MACD histogram declining
                      latest['close'] < latest['fast_ma'] and  # Price below fast MA
                      latest['fast_ma'] < latest['slow_ma']):  # Bearish MA alignment
                    
                    logging.info(f"  ✅ BEARISH MOMENTUM SIGNAL!")
                    logging.info(f"     RSI {rsi:.2f} declining from overbought")
                    logging.info(f"     MACD histogram declining: {macd_hist:.6f} < {macd_hist_prev:.6f}")
                    logging.info(f"     Price below fast MA in bearish trend")
                    signal = -1
                    signal_reason = "Bearish Momentum Decline"
                else:
                    logging.info(f"  ❌ No momentum signal")
                    logging.info(f"     Momentum conditions not aligned")
            else:
                logging.info(f"  ⚠️  Insufficient data for momentum analysis")
        
        # METHOD 4: PULLBACK SIGNALS (New - Medium Confidence)
        if signal == 0:
            logging.info("-"*80)
            logging.info("🔍 METHOD 4: CHECKING PULLBACK SIGNALS:")
            
            # Calculate price distance from MAs
            fast_ma_distance = (latest['close'] - latest['fast_ma']) / latest['fast_ma'] * 100
            slow_ma_distance = (latest['close'] - latest['slow_ma']) / latest['slow_ma'] * 100
            
            logging.info(f"  Price distance from Fast MA: {fast_ma_distance:+.3f}%")
            logging.info(f"  Price distance from Slow MA: {slow_ma_distance:+.3f}%")
            
            # BULLISH PULLBACK: Price near fast MA in uptrend
            if (latest['fast_ma'] > latest['slow_ma'] and  # Uptrend
                abs(fast_ma_distance) < 0.1 and  # Price very close to fast MA
                fast_ma_distance > -0.05 and  # Price not too far below
                slow_ma_distance > 0.05):  # Price still above slow MA
                
                logging.info(f"  ✅ BULLISH PULLBACK SIGNAL!")
                logging.info(f"     Price pulled back to fast MA in uptrend")
                logging.info(f"     Good entry point for trend continuation")
                signal = 1
                signal_reason = "Bullish Pullback to MA"
            
            # BEARISH PULLBACK: Price near fast MA in downtrend
            elif (latest['fast_ma'] < latest['slow_ma'] and  # Downtrend
                  abs(fast_ma_distance) < 0.1 and  # Price very close to fast MA
                  fast_ma_distance < 0.05 and  # Price not too far above
                  slow_ma_distance < -0.05):  # Price still below slow MA
                
                logging.info(f"  ✅ BEARISH PULLBACK SIGNAL!")
                logging.info(f"     Price pulled back to fast MA in downtrend")
                logging.info(f"     Good entry point for trend continuation")
                signal = -1
                signal_reason = "Bearish Pullback to MA"
            else:
                logging.info(f"  ❌ No pullback signal")
                logging.info(f"     Pullback conditions not met")
        
        # METHOD 5: BREAKOUT SIGNALS (New - High Confidence)
        if signal == 0 and len(df) >= 20:
            logging.info("-"*80)
            logging.info("🔍 METHOD 5: CHECKING BREAKOUT SIGNALS:")
            
            # Calculate recent high/low (last 10 bars)
            recent_bars = df.tail(10)
            recent_high = recent_bars['high'].max()
            recent_low = recent_bars['low'].min()
            current_price = latest['close']
            
            logging.info(f"  Recent High (10 bars): {recent_high:.5f}")
            logging.info(f"  Recent Low (10 bars):  {recent_low:.5f}")
            logging.info(f"  Current Price:         {current_price:.5f}")
            
            # BULLISH BREAKOUT: Price breaks above recent high
            if (current_price > recent_high and
                latest['fast_ma'] > latest['slow_ma'] and  # Bullish MA alignment
                current_price > latest['fast_ma']):  # Price above fast MA
                
                breakout_strength = (current_price - recent_high) / recent_high * 100
                logging.info(f"  ✅ BULLISH BREAKOUT SIGNAL!")
                logging.info(f"     Price broke above recent high")
                logging.info(f"     Breakout strength: {breakout_strength:+.3f}%")
                signal = 1
                signal_reason = "Bullish Breakout"
            
            # BEARISH BREAKOUT: Price breaks below recent low
            elif (current_price < recent_low and
                  latest['fast_ma'] < latest['slow_ma'] and  # Bearish MA alignment
                  current_price < latest['fast_ma']):  # Price below fast MA
                
                breakout_strength = (recent_low - current_price) / recent_low * 100
                logging.info(f"  ✅ BEARISH BREAKOUT SIGNAL!")
                logging.info(f"     Price broke below recent low")
                logging.info(f"     Breakout strength: {breakout_strength:+.3f}%")
                signal = -1
                signal_reason = "Bearish Breakout"
            else:
                logging.info(f"  ❌ No breakout signal")
                logging.info(f"     No significant breakout detected")
        
        # Final check - if still no signal
        if signal == 0:
            logging.info("-"*80)
            logging.info("❌ NO SIGNAL GENERATED")
            logging.info("   Checked 5 signal methods:")
            logging.info("   1. MA Crossover - No crossover")
            logging.info("   2. Trend Confirmation - No trend change")
            logging.info("   3. Momentum Signals - No momentum alignment")
            logging.info("   4. Pullback Signals - No pullback opportunity")
            logging.info("   5. Breakout Signals - No breakout detected")
            logging.info("   Market conditions not favorable for entry")
            logging.info("="*80)
            return 0
        
        # Log the successful signal
        logging.info("-"*80)
        logging.info(f"✅ SIGNAL GENERATED: {signal_reason}")
        logging.info("="*80)'''
    
    # Replace the old logic with new logic
    if old_signal_logic in content:
        content = content.replace(old_signal_logic, new_signal_logic)
        print("✅ Enhanced signal generation logic")
    else:
        print("❌ Could not find signal generation section to replace")
        return False
    
    # Write the updated content
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Signal generation fix applied to {filepath}")
    return True

if __name__ == "__main__":
    print("🔧 Fixing Signal Generation Issue...")
    print("="*60)
    
    if fix_signal_generation():
        print("\n✅ SIGNAL GENERATION FIX COMPLETE!")
        print("\nEnhancements added:")
        print("1. ✅ MA Crossover (Original - High Confidence)")
        print("2. ✅ Trend Confirmation (Original - High Confidence)")
        print("3. 🆕 Momentum Signals (RSI + MACD - Medium Confidence)")
        print("4. 🆕 Pullback Signals (MA Retracement - Medium Confidence)")
        print("5. 🆕 Breakout Signals (Support/Resistance - High Confidence)")
        print("\n📊 The bot will now generate more trading signals!")
        print("🔄 Restart the bot to apply changes")
    else:
        print("\n❌ SIGNAL GENERATION FIX FAILED!")
        print("Please check the file manually")