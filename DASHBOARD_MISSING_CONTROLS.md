# Dashboard Missing Controls - Implementation Guide

## Issues Found

### 1. MA Period Defaults Are Wrong
**Current**: fast_ma=20, slow_ma=50
**Should be**: fast_ma=10, slow_ma=21

### 2. Missing Hour Filter Controls
- `enable_hour_filter` (checkbox)
- `golden_hours` (multi-select or text input)
- `dead_hours` (multi-select or text input)
- `roc_threshold` (number input)

### 3. Missing Time-Based Exit Controls
- `enable_time_based_exit` (checkbox)
- `max_hold_minutes` (number input)

### 4. Missing Breakeven Stop Controls
- `enable_breakeven_stop` (checkbox)
- `breakeven_atr_threshold` (number input)

## Implementation Plan

### Step 1: Fix MA Period Defaults
Location: Line ~883-893 in templates/dashboard.html

```html
<!-- BEFORE -->
<div class="form-group">
    <label>Fast MA Period</label>
    <input type="number" id="fast-ma" value="20" min="5" max="100">
    <small style="color: #94a3b8;">Standard: 20</small>
</div>
<div class="form-group">
    <label>Slow MA Period</label>
    <input type="number" id="slow-ma" value="50" min="20" max="200">
    <small style="color: #94a3b8;">Standard: 50</small>
</div>

<!-- AFTER -->
<div class="form-group">
    <label>Fast MA Period</label>
    <input type="number" id="fast-ma" value="10" min="5" max="100">
    <small style="color: #94a3b8;">Optimized: 10 (faster signals)</small>
</div>
<div class="form-group">
    <label>Slow MA Period</label>
    <input type="number" id="slow-ma" value="21" min="10" max="200">
    <small style="color: #94a3b8;">Optimized: 21 (balanced)</small>
</div>
```

### Step 2: Add Hour Filter Section
Add after the indicator settings section:

```html
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
                <small style="color: #94a3b8;">Rate of change threshold for momentum</small>
            </div>
        </div>
    </div>
</div>
```

### Step 3: Add Time-Based Exit Section
Add after hour filter section:

```html
<!-- Time-Based Exit Settings -->
<div class="config-section" style="margin-top: 20px;">
    <div class="accordion-header" onclick="toggleAccordion('time-exit')">
        <span>⏱️ Time-Based Exit Settings</span>
        <span class="accordion-icon">▼</span>
    </div>
    <div id="time-exit-content" class="accordion-content">
        <div class="form-group" style="grid-column: 1 / -1;">
            <label class="checkbox-label">
                <input type="checkbox" id="enable-time-based-exit">
                Enable Time-Based Exit
            </label>
            <small style="color: #94a3b8; display: block; margin-top: 5px;">
                Automatically close positions after maximum hold time
            </small>
        </div>
        
        <div class="grid">
            <div class="form-group">
                <label>Max Hold Time (Minutes)</label>
                <input type="number" id="max-hold-minutes" value="45" min="5" max="240" step="5">
                <small style="color: #94a3b8;">Maximum time to hold a position</small>
            </div>
        </div>
    </div>
</div>
```

### Step 4: Add Breakeven Stop Section
Add after time-based exit section:

```html
<!-- Breakeven Stop Settings -->
<div class="config-section" style="margin-top: 20px;">
    <div class="accordion-header" onclick="toggleAccordion('breakeven')">
        <span>🎯 Breakeven Stop Settings</span>
        <span class="accordion-icon">▼</span>
    </div>
    <div id="breakeven-content" class="accordion-content">
        <div class="form-group" style="grid-column: 1 / -1;">
            <label class="checkbox-label">
                <input type="checkbox" id="enable-breakeven-stop" checked>
                Enable Breakeven Stop
            </label>
            <small style="color: #94a3b8; display: block; margin-top: 5px;">
                Move stop loss to entry price once position is profitable
            </small>
        </div>
        
        <div class="grid">
            <div class="form-group">
                <label>Breakeven ATR Threshold</label>
                <input type="number" id="breakeven-atr-threshold" value="0.3" min="0.1" max="2.0" step="0.1">
                <small style="color: #94a3b8;">ATR multiplier to trigger breakeven (0.3 = 30% of ATR)</small>
            </div>
        </div>
    </div>
</div>
```

### Step 5: Update JavaScript to Handle New Fields

Add to the `loadConfig()` function:

```javascript
// Hour filter settings
document.getElementById('enable-hour-filter').checked = config.enable_hour_filter !== false;
document.getElementById('golden-hours').value = (config.golden_hours || [8,11,13,14,15,19,23]).join(',');
document.getElementById('dead-hours').value = (config.dead_hours || [0,1,2,17,20,21,22]).join(',');
document.getElementById('roc-threshold').value = config.roc_threshold || 0.15;

// Time-based exit settings
document.getElementById('enable-time-based-exit').checked = config.enable_time_based_exit === true;
document.getElementById('max-hold-minutes').value = config.max_hold_minutes || 45;

// Breakeven stop settings
document.getElementById('enable-breakeven-stop').checked = config.enable_breakeven_stop !== false;
document.getElementById('breakeven-atr-threshold').value = config.breakeven_atr_threshold || 0.3;
```

Add to the form submission handler:

```javascript
// Hour filter settings
enable_hour_filter: document.getElementById('enable-hour-filter').checked,
golden_hours: document.getElementById('golden-hours').value.split(',').map(h => parseInt(h.trim())),
dead_hours: document.getElementById('dead-hours').value.split(',').map(h => parseInt(h.trim())),
roc_threshold: parseFloat(document.getElementById('roc-threshold').value),

// Time-based exit settings
enable_time_based_exit: document.getElementById('enable-time-based-exit').checked,
max_hold_minutes: parseInt(document.getElementById('max-hold-minutes').value),

// Breakeven stop settings
enable_breakeven_stop: document.getElementById('enable-breakeven-stop').checked,
breakeven_atr_threshold: parseFloat(document.getElementById('breakeven-atr-threshold').value),
```

## Summary

This will add:
- ✅ Fixed MA period defaults (10/21)
- ✅ Hour filter controls (golden/dead hours, ROC threshold)
- ✅ Time-based exit controls
- ✅ Breakeven stop controls

All controls will be properly synchronized with bot_config.json and the bot logic.
