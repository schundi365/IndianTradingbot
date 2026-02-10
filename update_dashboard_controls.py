"""
Update Dashboard with Missing Controls
Adds hour filter, time-based exit, and breakeven stop controls
"""

from pathlib import Path
import re

print("=" * 80)
print("UPDATING DASHBOARD WITH MISSING CONTROLS")
print("=" * 80)
print()

dashboard_file = Path("templates/dashboard.html")
if not dashboard_file.exists():
    print("❌ Dashboard file not found")
    exit(1)

with open(dashboard_file, 'r', encoding='utf-8') as f:
    content = f.read()

print("✅ Loaded dashboard.html")
print()

# Step 1: Fix MA period defaults
print("Step 1: Fixing MA period defaults...")
print("-" * 80)

# Fix fast MA
content = re.sub(
    r'(<input type="number" id="fast-ma" value=")20(")',
    r'\g<1>10\g<2>',
    content
)
content = re.sub(
    r'(<small style="color: #94a3b8;">)Standard: 20(</small>)',
    r'\g<1>Optimized: 10 (faster signals)\g<2>',
    content
)
print("  ✓ Updated fast_ma_period: 20 → 10")

# Fix slow MA
content = re.sub(
    r'(<input type="number" id="slow-ma" value=")50(")',
    r'\g<1>21\g<2>',
    content
)
content = re.sub(
    r'(<small style="color: #94a3b8;">)Standard: 50(</small>)',
    r'\g<1>Optimized: 21 (balanced)\g<2>',
    content
)
print("  ✓ Updated slow_ma_period: 50 → 21")

print()

# Step 2: Add hour filter section
print("Step 2: Adding hour filter controls...")
print("-" * 80)

hour_filter_html = '''
                    <!-- Hour-Based Trading Filter -->
                    <div class="config-section" style="margin-top: 20px;">
                        <div class="accordion-header" onclick="toggleAccordion('hour-filter')">
                            <span>🕐 Hour-Based Trading Filter</span>
                            <span class="accordion-icon">▼</span>
                        </div>
                        <div id="hour-filter-content" class="accordion-content">
                            <div class="form-group" style="grid-column: 1 / -1;">
                                <label class="checkbox-label">
                                    <input type="checkbox" id="enable-hour-filter" checked>
                                    Enable Hour-Based Filter
                                </label>
                                <small style="color: #94a3b8; display: block; margin-top: 5px;">
                                    Filter trades based on historical performance by hour (UTC)
                                </small>
                            </div>
                            
                            <div class="grid">
                                <div class="form-group">
                                    <label>Golden Hours (Profitable)</label>
                                    <input type="text" id="golden-hours" value="8,11,13,14,15,19,23" placeholder="8,11,13,14,15,19,23">
                                    <small style="color: #94a3b8;">Comma-separated hours (UTC)</small>
                                </div>
                                <div class="form-group">
                                    <label>Dead Hours (Avoid Trading)</label>
                                    <input type="text" id="dead-hours" value="0,1,2,17,20,21,22" placeholder="0,1,2,17,20,21,22">
                                    <small style="color: #94a3b8;">Comma-separated hours (UTC)</small>
                                </div>
                                <div class="form-group">
                                    <label>ROC Threshold (%)</label>
                                    <input type="number" id="roc-threshold" value="0.15" min="0.05" max="1.0" step="0.05">
                                    <small style="color: #94a3b8;">Rate of change threshold</small>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Time-Based Exit Settings -->
                    <div class="config-section" style="margin-top: 20px;">
                        <div class="accordion-header" onclick="toggleAccordion('time-exit')">
                            <span>⏱️ Time-Based Exit</span>
                            <span class="accordion-icon">▼</span>
                        </div>
                        <div id="time-exit-content" class="accordion-content">
                            <div class="form-group" style="grid-column: 1 / -1;">
                                <label class="checkbox-label">
                                    <input type="checkbox" id="enable-time-based-exit">
                                    Enable Time-Based Exit
                                </label>
                                <small style="color: #94a3b8; display: block; margin-top: 5px;">
                                    Automatically close positions after max hold time
                                </small>
                            </div>
                            
                            <div class="grid">
                                <div class="form-group">
                                    <label>Max Hold Time (Minutes)</label>
                                    <input type="number" id="max-hold-minutes" value="45" min="5" max="240" step="5">
                                    <small style="color: #94a3b8;">Maximum time to hold position</small>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Breakeven Stop Settings -->
                    <div class="config-section" style="margin-top: 20px;">
                        <div class="accordion-header" onclick="toggleAccordion('breakeven')">
                            <span>🎯 Breakeven Stop</span>
                            <span class="accordion-icon">▼</span>
                        </div>
                        <div id="breakeven-content" class="accordion-content">
                            <div class="form-group" style="grid-column: 1 / -1;">
                                <label class="checkbox-label">
                                    <input type="checkbox" id="enable-breakeven-stop" checked>
                                    Enable Breakeven Stop
                                </label>
                                <small style="color: #94a3b8; display: block; margin-top: 5px;">
                                    Move SL to entry once profitable
                                </small>
                            </div>
                            
                            <div class="grid">
                                <div class="form-group">
                                    <label>Breakeven ATR Threshold</label>
                                    <input type="number" id="breakeven-atr-threshold" value="0.3" min="0.1" max="2.0" step="0.1">
                                    <small style="color: #94a3b8;">ATR multiplier to trigger (0.3 = 30%)</small>
                                </div>
                            </div>
                        </div>
                    </div>
'''

# Find where to insert (after the last config-section before the save button)
insert_marker = '<button type="submit" class="btn btn-secondary" id="save-config-btn"'
if insert_marker in content:
    content = content.replace(insert_marker, hour_filter_html + '\n                    ' + insert_marker)
    print("  ✓ Added hour filter controls")
    print("  ✓ Added time-based exit controls")
    print("  ✓ Added breakeven stop controls")
else:
    print("  ❌ Could not find insertion point")

print()

# Save updated dashboard
print("Step 3: Saving updated dashboard...")
print("-" * 80)

# Backup original
backup_file = Path("templates/dashboard_backup.html")
with open(backup_file, 'w', encoding='utf-8') as f:
    with open(dashboard_file, 'r', encoding='utf-8') as orig:
        f.write(orig.read())
print(f"  ✓ Backup created: {backup_file}")

# Save updated
with open(dashboard_file, 'w', encoding='utf-8') as f:
    f.write(content)
print(f"  ✓ Updated dashboard saved")

print()
print("=" * 80)
print("DASHBOARD UPDATE COMPLETE")
print("=" * 80)
print()

print("Summary:")
print("  • Fixed MA period defaults (10/21)")
print("  • Added hour filter controls")
print("  • Added time-based exit controls")
print("  • Added breakeven stop controls")
print()

print("⚠️  IMPORTANT: JavaScript handlers still need to be updated!")
print("    See DASHBOARD_MISSING_CONTROLS.md for JavaScript code")
print()
