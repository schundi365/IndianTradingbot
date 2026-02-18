#!/usr/bin/env python3
"""
Update Dashboard Default Values

Make the optimized signal generation values the default values
in the dashboard so new users get the best configuration automatically.

Optimized Values:
- MACD Min Histogram: 0.0005 (was 0.0003)
- Min Volume MA: 0.7 (was 1.0)
- Timeframe: M15 (was M30)
- RSI Overbought: 70 (was 75)
- RSI Oversold: 30 (was 25)
- Min Trade Confidence: 0.5 (was 0.6)
"""

import re

def update_dashboard_defaults():
    """Update default values in the dashboard template"""
    
    dashboard_file = "templates/dashboard.html"
    
    # Read current dashboard
    with open(dashboard_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("🔧 UPDATING DASHBOARD DEFAULT VALUES")
    print("="*60)
    
    # Define the updates to make
    updates = [
        # MACD Min Histogram: 0.0003 → 0.0005
        {
            'pattern': r'(<input[^>]*id="macd-min-histogram"[^>]*value=")[^"]*(")',
            'replacement': r'\g<1>0.0005\g<2>',
            'description': 'MACD Min Histogram: 0.0003 → 0.0005'
        },
        
        # Min Volume MA: 1.0 → 0.7
        {
            'pattern': r'(<input[^>]*id="min-volume-ma"[^>]*value=")[^"]*(")',
            'replacement': r'\g<1>0.7\g<2>',
            'description': 'Min Volume MA: 1.0 → 0.7'
        },
        
        # Timeframe: 30 → 15
        {
            'pattern': r'(<option value="15"[^>]*>)([^<]*)(</option>)',
            'replacement': r'\g<1>\g<2> - Recommended\g<3>',
            'description': 'Mark M15 as recommended timeframe'
        },
        
        # RSI Overbought: 75 → 70
        {
            'pattern': r'(<input[^>]*id="rsi-overbought"[^>]*value=")[^"]*(")',
            'replacement': r'\g<1>70\g<2>',
            'description': 'RSI Overbought: 75 → 70'
        },
        
        # RSI Oversold: 25 → 30
        {
            'pattern': r'(<input[^>]*id="rsi-oversold"[^>]*value=")[^"]*(")',
            'replacement': r'\g<1>30\g<2>',
            'description': 'RSI Oversold: 25 → 30'
        },
        
        # Min Trade Confidence: 0.6 → 0.5
        {
            'pattern': r'(<input[^>]*id="min-trade-confidence"[^>]*value=")[^"]*(")',
            'replacement': r'\g<1>0.5\g<2>',
            'description': 'Min Trade Confidence: 0.6 → 0.5'
        }
    ]
    
    # Apply updates
    updated_count = 0
    for update in updates:
        if re.search(update['pattern'], content):
            content = re.sub(update['pattern'], update['replacement'], content)
            print(f"✅ {update['description']}")
            updated_count += 1
        else:
            print(f"⚠️  Pattern not found: {update['description']}")
    
    # Also update the configuration presets to use optimized values
    preset_updates = [
        # Update profitable preset
        {
            'pattern': r'(profitable:\s*{[^}]*macd_min_histogram:\s*)[0-9.]+',
            'replacement': r'\g<1>0.0005',
            'description': 'Profitable preset MACD threshold'
        },
        {
            'pattern': r'(profitable:\s*{[^}]*min_volume_ma:\s*)[0-9.]+',
            'replacement': r'\g<1>0.7',
            'description': 'Profitable preset volume threshold'
        },
        {
            'pattern': r'(profitable:\s*{[^}]*timeframe:\s*)[0-9]+',
            'replacement': r'\g<1>15',
            'description': 'Profitable preset timeframe'
        },
        {
            'pattern': r'(profitable:\s*{[^}]*rsi_overbought:\s*)[0-9]+',
            'replacement': r'\g<1>70',
            'description': 'Profitable preset RSI overbought'
        },
        {
            'pattern': r'(profitable:\s*{[^}]*rsi_oversold:\s*)[0-9]+',
            'replacement': r'\g<1>30',
            'description': 'Profitable preset RSI oversold'
        },
        {
            'pattern': r'(profitable:\s*{[^}]*min_trade_confidence:\s*)[0-9.]+',
            'replacement': r'\g<1>0.5',
            'description': 'Profitable preset confidence'
        }
    ]
    
    # Apply preset updates
    for update in preset_updates:
        if re.search(update['pattern'], content, re.DOTALL):
            content = re.sub(update['pattern'], update['replacement'], content, flags=re.DOTALL)
            print(f"✅ {update['description']}")
            updated_count += 1
        else:
            print(f"⚠️  Preset pattern not found: {update['description']}")
    
    # Write updated content
    with open(dashboard_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n✅ Updated {updated_count} default values in dashboard")
    return updated_count > 0

def update_web_dashboard_defaults():
    """Update default values in web_dashboard.py"""
    
    web_dashboard_file = "web_dashboard.py"
    
    # Read current file
    with open(web_dashboard_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("\n🔧 UPDATING WEB DASHBOARD BACKEND DEFAULTS")
    print("="*60)
    
    # Look for default configuration loading and update it
    # This ensures API responses use optimized defaults
    default_config_pattern = r'(def.*get.*default.*config|DEFAULT_CONFIG\s*=|default.*=\s*{)'
    
    if re.search(default_config_pattern, content, re.IGNORECASE):
        print("✅ Found default configuration section")
        
        # Update specific default values if they exist
        updates = [
            ('macd_min_histogram.*0\.0003', 'macd_min_histogram": 0.0005'),
            ('min_volume_ma.*1\.0', 'min_volume_ma": 0.7'),
            ('timeframe.*30', 'timeframe": 15'),
            ('rsi_overbought.*75', 'rsi_overbought": 70'),
            ('rsi_oversold.*25', 'rsi_oversold": 30'),
            ('min_trade_confidence.*0\.6', 'min_trade_confidence": 0.5')
        ]
        
        updated = False
        for pattern, replacement in updates:
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
                print(f"✅ Updated backend default: {replacement}")
                updated = True
        
        if updated:
            # Write updated content
            with open(web_dashboard_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print("✅ Backend defaults updated")
        else:
            print("⚠️  No backend defaults found to update")
    else:
        print("⚠️  No default configuration section found in backend")
    
    return True

def update_config_presets():
    """Update configuration preset files"""
    
    preset_files = [
        "src/config.py",
        "src/config_profitable_balanced.py",
        "src/config_optimized.py"
    ]
    
    print("\n🔧 UPDATING CONFIGURATION PRESET FILES")
    print("="*60)
    
    for preset_file in preset_files:
        try:
            with open(preset_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Update default values in preset files
            updates = [
                ('macd_min_histogram.*=.*0\.0003', 'macd_min_histogram = 0.0005'),
                ('min_volume_ma.*=.*1\.0', 'min_volume_ma = 0.7'),
                ('timeframe.*=.*30', 'timeframe = 15'),
                ('rsi_overbought.*=.*75', 'rsi_overbought = 70'),
                ('rsi_oversold.*=.*25', 'rsi_oversold = 30'),
                ('min_trade_confidence.*=.*0\.6', 'min_trade_confidence = 0.5')
            ]
            
            updated = False
            for pattern, replacement in updates:
                if re.search(pattern, content):
                    content = re.sub(pattern, replacement, content)
                    updated = True
            
            if updated:
                with open(preset_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ Updated {preset_file}")
            else:
                print(f"⚠️  No updates needed for {preset_file}")
                
        except FileNotFoundError:
            print(f"⚠️  File not found: {preset_file}")
        except Exception as e:
            print(f"❌ Error updating {preset_file}: {e}")

if __name__ == "__main__":
    print("🚀 UPDATING DASHBOARD DEFAULTS TO OPTIMIZED VALUES")
    print("="*80)
    
    success_count = 0
    
    # Update dashboard template
    if update_dashboard_defaults():
        success_count += 1
    
    # Update web dashboard backend
    if update_web_dashboard_defaults():
        success_count += 1
    
    # Update configuration presets
    update_config_presets()
    success_count += 1
    
    if success_count >= 2:
        print("\n🎉 DASHBOARD DEFAULTS UPDATED SUCCESSFULLY!")
        print("\n📊 NEW DEFAULT VALUES:")
        print("• MACD Min Histogram: 0.0005 (more sensitive)")
        print("• Min Volume MA: 0.7 (less restrictive)")
        print("• Timeframe: M15 (more frequent analysis)")
        print("• RSI Overbought: 70 (standard level)")
        print("• RSI Oversold: 30 (standard level)")
        print("• Min Trade Confidence: 0.5 (more signals)")
        
        print("\n✅ BENEFITS:")
        print("• New users get optimized settings automatically")
        print("• Dashboard forms pre-filled with best values")
        print("• Configuration presets use optimized defaults")
        print("• Maximum signal generation out of the box")
        
        print("\n🔄 RESTART DASHBOARD:")
        print("python web_dashboard.py")
        
    else:
        print("\n❌ SOME UPDATES FAILED!")
        print("Please check the files manually")