"""
Add JavaScript handlers for new dashboard controls
"""

from pathlib import Path

print("=" * 80)
print("ADDING JAVASCRIPT HANDLERS")
print("=" * 80)
print()

dashboard_file = Path("templates/dashboard.html")
with open(dashboard_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Add to loadConfig section (after the indicators section)
load_config_addition = '''
            // Hour Filter Settings
            document.getElementById('enable-hour-filter').checked = config.enable_hour_filter !== false;
            document.getElementById('golden-hours').value = (config.golden_hours || [8,11,13,14,15,19,23]).join(',');
            document.getElementById('dead-hours').value = (config.dead_hours || [0,1,2,17,20,21,22]).join(',');
            document.getElementById('roc-threshold').value = config.roc_threshold || 0.15;
            
            // Time-Based Exit Settings
            document.getElementById('enable-time-based-exit').checked = config.enable_time_based_exit === true;
            document.getElementById('max-hold-minutes').value = config.max_hold_minutes || 45;
            
            // Breakeven Stop Settings
            document.getElementById('enable-breakeven-stop').checked = config.enable_breakeven_stop !== false;
            document.getElementById('breakeven-atr-threshold').value = config.breakeven_atr_threshold || 0.3;
            '''

# Find insertion point (after adx-min line)
marker1 = "document.getElementById('adx-min').value = config.adx_min;"
if marker1 in content:
    content = content.replace(marker1, marker1 + '\n' + load_config_addition)
    print("✓ Added loadConfig handlers")
else:
    print("❌ Could not find loadConfig insertion point")

# Add to form submission section
form_submit_addition = '''
                // Hour Filter Settings
                enable_hour_filter: document.getElementById('enable-hour-filter').checked,
                golden_hours: document.getElementById('golden-hours').value.split(',').map(h => parseInt(h.trim())).filter(h => !isNaN(h)),
                dead_hours: document.getElementById('dead-hours').value.split(',').map(h => parseInt(h.trim())).filter(h => !isNaN(h)),
                roc_threshold: parseFloat(document.getElementById('roc-threshold').value),
                
                // Time-Based Exit Settings
                enable_time_based_exit: document.getElementById('enable-time-based-exit').checked,
                max_hold_minutes: parseInt(document.getElementById('max-hold-minutes').value),
                
                // Breakeven Stop Settings
                enable_breakeven_stop: document.getElementById('enable-breakeven-stop').checked,
                breakeven_atr_threshold: parseFloat(document.getElementById('breakeven-atr-threshold').value),
                '''

# Find insertion point (after adx_min_strength line in form submission)
marker2 = "adx_min_strength: parseInt(document.getElementById('adx-min').value),"
if marker2 in content:
    content = content.replace(marker2, marker2 + '\n' + form_submit_addition)
    print("✓ Added form submission handlers")
else:
    print("❌ Could not find form submission insertion point")

# Save
with open(dashboard_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Dashboard JavaScript updated")
print()
print("=" * 80)
print("JAVASCRIPT HANDLERS ADDED")
print("=" * 80)
