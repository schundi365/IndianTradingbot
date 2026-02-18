# Screenshot Guide for User Documentation

This document describes the screenshots that should be captured for the user guide. Screenshots help users understand the interface and follow instructions more easily.

## Screenshot Directory Structure

```
indian_dashboard/
└── docs/
    └── screenshots/
        ├── 01-broker/
        ├── 02-instruments/
        ├── 03-configuration/
        ├── 04-monitor/
        ├── 05-trades/
        └── 06-misc/
```

---

## Required Screenshots

### 1. Broker Tab Screenshots

#### 1.1 Broker Selection Screen
**Filename**: `01-broker/broker-selection.png`

**What to capture**:
- Broker tab active
- List of broker cards/dropdown showing all brokers
- Broker logos visible
- Clean, uncluttered view

**Setup**:
- Fresh dashboard load
- No broker connected
- Default state

**Annotations needed**:
- Arrow pointing to broker selector
- Label: "Select your broker here"

---

#### 1.2 Kite Connect Login Form
**Filename**: `01-broker/kite-login-form.png`

**What to capture**:
- Kite Connect selected
- API Key field
- API Secret field
- "Login with Kite" button
- "Test Connection" button

**Setup**:
- Select Kite Connect broker
- Empty form fields
- All buttons visible

**Annotations needed**:
- Arrow to "Login with Kite" button
- Label: "Recommended: Use OAuth"

---

#### 1.3 Alice Blue Login Form
**Filename**: `01-broker/alice-login-form.png`

**What to capture**:
- Alice Blue selected
- User ID field
- API Key field
- Test Connection button

---

#### 1.4 Angel One Login Form
**Filename**: `01-broker/angel-login-form.png`

**What to capture**:
- Angel One selected
- Client ID field
- Password field
- TOTP field
- Test Connection button

---

#### 1.5 Upstox Login Form
**Filename**: `01-broker/upstox-login-form.png`

**What to capture**:
- Upstox selected
- API Key field
- API Secret field
- Redirect URI field
- Test Connection button

---

#### 1.6 Paper Trading Option
**Filename**: `01-broker/paper-trading.png`

**What to capture**:
- Paper Trading selected
- "No credentials required" message
- Connect button
- Information about paper trading

---

#### 1.7 Successful Connection
**Filename**: `01-broker/connection-success.png`

**What to capture**:
- Green checkmark/success indicator
- Broker name displayed
- User information (name/ID)
- Connection timestamp
- Disconnect button

**Setup**:
- Successfully connected to any broker
- User info populated

**Annotations needed**:
- Highlight connection status
- Label: "Connection successful"

---

#### 1.8 Connection Error
**Filename**: `01-broker/connection-error.png`

**What to capture**:
- Error message displayed
- Red error indicator
- Helpful error text
- Retry option

**Setup**:
- Attempt connection with invalid credentials
- Capture error state

---

### 2. Instruments Tab Screenshots

#### 2.1 Instrument Table
**Filename**: `02-instruments/instrument-table.png`

**What to capture**:
- Full instrument table
- Columns: Symbol, Name, Exchange, Type, Price, Select
- Multiple rows of data
- Pagination controls
- Search bar
- Filter dropdowns

**Setup**:
- Instruments loaded
- No filters applied
- First page showing

**Annotations needed**:
- Arrow to search bar
- Arrow to filter dropdowns
- Arrow to checkboxes

---

#### 2.2 Search Functionality
**Filename**: `02-instruments/search-example.png`

**What to capture**:
- Search bar with "RELIANCE" typed
- Filtered results showing only matching instruments
- Highlighted search matches

**Setup**:
- Type "RELIANCE" in search
- Wait for results to filter

---

#### 2.3 Filter Applied
**Filename**: `02-instruments/filter-applied.png`

**What to capture**:
- Exchange filter set to "NSE"
- Type filter set to "EQ"
- Filtered results
- Active filter indicators

**Setup**:
- Select NSE from exchange dropdown
- Select EQ from type dropdown

---

#### 2.4 Instrument Selection
**Filename**: `02-instruments/instruments-selected.png`

**What to capture**:
- Multiple instruments with checkboxes checked
- Selected instruments panel on right
- Count of selected instruments
- Remove buttons (×) for each

**Setup**:
- Select 3-4 instruments
- Show selected panel

**Annotations needed**:
- Highlight selected checkboxes
- Highlight selected panel

---

#### 2.5 Selected Instruments Panel
**Filename**: `02-instruments/selected-panel.png`

**What to capture**:
- Close-up of selected instruments panel
- List of selected instruments
- Remove buttons
- Total count
- "Continue to Configuration" button

**Setup**:
- Select 3-4 instruments
- Focus on right panel

---

#### 2.6 Refresh Instruments
**Filename**: `02-instruments/refresh-button.png`

**What to capture**:
- Refresh button
- Last updated timestamp
- Loading indicator (if possible)

---

### 3. Configuration Tab Screenshots

#### 3.1 Configuration Form Overview
**Filename**: `03-configuration/config-form-overview.png`

**What to capture**:
- Full configuration form
- All sections visible (Basic, Risk, Strategy)
- Tabbed interface if applicable
- Save/Load buttons

**Setup**:
- Configuration tab active
- Form with some data filled

---

#### 3.2 Basic Settings Section
**Filename**: `03-configuration/basic-settings.png`

**What to capture**:
- Selected instruments display
- Timeframe dropdown
- Strategy selector
- Trading hours inputs

**Setup**:
- Basic settings section expanded
- Some values selected

**Annotations needed**:
- Label each field

---

#### 3.3 Risk Management Section
**Filename**: `03-configuration/risk-management.png`

**What to capture**:
- Risk per trade slider
- Max positions input
- Max daily loss input
- All controls visible

**Setup**:
- Risk section expanded
- Sliders at reasonable values (2%, 3 positions, 5% loss)

**Annotations needed**:
- Highlight recommended values

---

#### 3.4 Strategy Parameters Section
**Filename**: `03-configuration/strategy-parameters.png`

**What to capture**:
- Indicator parameter inputs
- MA periods
- RSI settings
- TP/SL settings

**Setup**:
- Strategy section expanded
- Typical values filled in

---

#### 3.5 Validation Errors
**Filename**: `03-configuration/validation-errors.png`

**What to capture**:
- Red error messages
- Invalid input highlighted
- Save button disabled
- Error text explaining issue

**Setup**:
- Enter invalid values (e.g., risk > 5%)
- Trigger validation errors

**Annotations needed**:
- Highlight error messages

---

#### 3.6 Risk Metrics Panel
**Filename**: `03-configuration/risk-metrics.png`

**What to capture**:
- Risk metrics card/panel
- Max position size
- Risk per trade (₹ and %)
- Margin requirements
- All calculated values

**Setup**:
- Fill configuration with valid values
- Show calculated metrics

---

#### 3.7 Preset Dropdown
**Filename**: `03-configuration/presets-dropdown.png`

**What to capture**:
- Preset selector dropdown open
- List of presets:
  - NIFTY Futures
  - BANKNIFTY Futures
  - Equity Intraday
  - Options Trading

**Setup**:
- Click preset dropdown
- Show all options

---

#### 3.8 Save Configuration Dialog
**Filename**: `03-configuration/save-dialog.png`

**What to capture**:
- Save dialog/modal
- Input field for configuration name
- Save and Cancel buttons

**Setup**:
- Click "Save Configuration"
- Show dialog

---

#### 3.9 Load Configuration Dialog
**Filename**: `03-configuration/load-dialog.png`

**What to capture**:
- Load dialog/modal
- List of saved configurations
- Each config with name and date
- Delete buttons
- Load button

**Setup**:
- Click "Load Configuration"
- Show list with 2-3 saved configs

---

#### 3.10 Export/Import Buttons
**Filename**: `03-configuration/export-import.png`

**What to capture**:
- Export to JSON button
- Import from JSON button
- Copy to Clipboard button

---

### 4. Monitor Tab Screenshots

#### 4.1 Bot Status Card
**Filename**: `04-monitor/bot-status-card.png`

**What to capture**:
- Bot status indicator (Running/Stopped)
- Uptime counter
- Broker connection status
- Open positions count
- Start/Stop/Restart buttons

**Setup**:
- Bot running
- Show green "Running" status

**Annotations needed**:
- Highlight status indicator

---

#### 4.2 Bot Stopped State
**Filename**: `04-monitor/bot-stopped.png`

**What to capture**:
- Red "Stopped" status
- Start button enabled
- Stop/Restart buttons disabled

**Setup**:
- Bot stopped
- Show stopped state

---

#### 4.3 Account Information Card
**Filename**: `04-monitor/account-info.png`

**What to capture**:
- Balance
- Equity
- Available margin
- Used margin
- Today's P&L (with color coding)

**Setup**:
- Bot connected to broker
- Real or mock account data

**Annotations needed**:
- Label each metric

---

#### 4.4 Positions Table
**Filename**: `04-monitor/positions-table.png`

**What to capture**:
- Open positions table
- Columns: Symbol, Qty, Entry, Current, P&L
- Multiple positions (2-3)
- Close buttons
- Total P&L at bottom

**Setup**:
- Bot with 2-3 open positions
- Mix of profit and loss positions

**Annotations needed**:
- Highlight P&L colors (green/red)

---

#### 4.5 Auto-Refresh Controls
**Filename**: `04-monitor/auto-refresh.png`

**What to capture**:
- Auto-refresh toggle
- Manual refresh button
- Last updated timestamp

---

#### 4.6 Start Bot Confirmation
**Filename**: `04-monitor/start-confirmation.png`

**What to capture**:
- Confirmation dialog
- Warning/info message
- Confirm and Cancel buttons

**Setup**:
- Click "Start Bot"
- Show confirmation dialog

---

### 5. Trades Tab Screenshots

#### 5.1 Trade History Table
**Filename**: `05-trades/trade-history.png`

**What to capture**:
- Full trade history table
- Columns: Date, Symbol, Type, Qty, Entry, Exit, P&L
- Multiple completed trades
- Pagination controls

**Setup**:
- Load historical trades
- Show 5-10 trades

---

#### 5.2 Date Range Filter
**Filename**: `05-trades/date-range-filter.png`

**What to capture**:
- From date picker
- To date picker
- Quick filter buttons (Today, Week, Month)
- Apply button

**Setup**:
- Show date filter controls
- Highlight quick filters

---

#### 5.3 Trade Statistics
**Filename**: `05-trades/trade-statistics.png`

**What to capture**:
- Statistics cards
- Total trades
- Win rate
- Total P&L
- Average P&L
- Best/Worst trade

**Setup**:
- Show statistics with real data
- Mix of wins and losses

**Annotations needed**:
- Highlight key metrics

---

#### 5.4 Export Trades Buttons
**Filename**: `05-trades/export-buttons.png`

**What to capture**:
- Export to CSV button
- Export to Excel button
- Download icon

---

### 6. Miscellaneous Screenshots

#### 6.1 Dashboard Header
**Filename**: `06-misc/dashboard-header.png`

**What to capture**:
- Dashboard title/logo
- Navigation tabs
- Broker status indicator in header
- Any global controls

---

#### 6.2 Tab Navigation
**Filename**: `06-misc/tab-navigation.png`

**What to capture**:
- All tabs visible
- Active tab highlighted
- Tab labels clear

---

#### 6.3 Loading State
**Filename**: `06-misc/loading-state.png`

**What to capture**:
- Loading spinner
- "Loading..." message
- Disabled controls during load

---

#### 6.4 Error Notification
**Filename**: `06-misc/error-notification.png`

**What to capture**:
- Error toast/notification
- Error icon
- Error message
- Close button

---

#### 6.5 Success Notification
**Filename**: `06-misc/success-notification.png`

**What to capture**:
- Success toast/notification
- Success icon (checkmark)
- Success message

---

#### 6.6 Mobile View (Optional)
**Filename**: `06-misc/mobile-view.png`

**What to capture**:
- Dashboard on mobile device
- Responsive layout
- Touch-friendly controls

---

## Screenshot Guidelines

### Technical Requirements
- **Resolution**: 1920x1080 or higher
- **Format**: PNG (for clarity)
- **File Size**: Compress to < 500KB per image
- **Browser**: Use Chrome or Firefox (latest version)
- **Zoom**: 100% browser zoom
- **Theme**: Use light theme (unless showing dark theme feature)

### Capture Guidelines
1. **Clean State**: Clear any personal data, use mock data
2. **Consistent Data**: Use same mock data across related screenshots
3. **Full Context**: Include enough surrounding UI for context
4. **No Clutter**: Close unnecessary browser tabs/windows
5. **Annotations**: Add arrows, labels, highlights using image editor

### Mock Data to Use
- **Broker**: Use Paper Trading or mock credentials
- **Instruments**: RELIANCE, TCS, INFY, NIFTY, BANKNIFTY
- **Prices**: Use realistic but rounded numbers (₹2,400, ₹3,200)
- **User Name**: "John Doe" or "Demo User"
- **Account Balance**: ₹1,00,000
- **Dates**: Use recent dates

### Annotation Tools
- **Windows**: Snipping Tool, Paint, Greenshot
- **Mac**: Preview, Skitch
- **Cross-platform**: GIMP, Inkscape
- **Online**: Photopea, Canva

### Annotation Style
- **Arrows**: Red, 3px width
- **Text**: Arial, 14pt, bold
- **Highlights**: Yellow transparent overlay
- **Boxes**: Red border, 2px width

---

## Screenshot Checklist

Use this checklist when capturing screenshots:

### Before Capturing
- [ ] Dashboard is running
- [ ] Browser at 100% zoom
- [ ] Window size is consistent (1920x1080)
- [ ] Mock data is loaded
- [ ] No personal information visible
- [ ] UI is in clean state (no errors unless showing error)

### During Capture
- [ ] Capture full context
- [ ] Include relevant UI elements
- [ ] Ensure text is readable
- [ ] Check for any cut-off elements

### After Capture
- [ ] Image is clear and sharp
- [ ] File size is reasonable
- [ ] Filename follows convention
- [ ] Saved in correct directory
- [ ] Add annotations if needed
- [ ] Compress if > 500KB

---

## Integration with User Guide

Once screenshots are captured, update the USER_GUIDE.md file:

1. Replace placeholder text with actual image references:
   ```markdown
   **Screenshot Placeholder: Broker Selection Screen**
   ```
   
   Becomes:
   ```markdown
   ![Broker Selection Screen](docs/screenshots/01-broker/broker-selection.png)
   *Select your broker from the available options*
   ```

2. Ensure alt text is descriptive for accessibility

3. Add captions below each image explaining what's shown

---

## Maintenance

Screenshots should be updated when:
- UI design changes significantly
- New features are added
- Broker options change
- User feedback indicates confusion

**Last Updated**: 2024-02-18  
**Next Review**: When UI changes are made
