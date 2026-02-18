/**
 * Helpful Features Module
 * Provides tooltips, contextual help, quick start guide, and example values
 */

const HelpfulFeatures = {
    // Parameter help data with tooltips and examples
    parameterHelp: {
        // Basic Settings
        'timeframe': {
            tooltip: 'The time interval for each candlestick in your trading strategy',
            help: 'Shorter timeframes (1-5 min) are for scalping, longer timeframes (1 hour+) for swing trading',
            examples: ['1 minute for high-frequency trading', '5 minutes for intraday', '1 day for positional']
        },
        'strategy': {
            tooltip: 'The trading strategy algorithm to use for generating signals',
            help: 'Trend Following works best in trending markets, Mean Reversion in ranging markets',
            examples: ['Trend Following for NIFTY futures', 'Mean Reversion for range-bound stocks']
        },
        'trading_start': {
            tooltip: 'Time when the bot starts trading each day (IST)',
            help: 'Indian markets open at 09:15 AM. Consider starting after initial volatility settles',
            examples: ['09:15 for full day', '09:30 to avoid opening volatility', '10:00 for calmer entry']
        },
        'trading_end': {
            tooltip: 'Time when the bot stops taking new positions (IST)',
            help: 'Markets close at 15:30. Stop earlier to avoid end-of-day volatility',
            examples: ['15:00 to close positions safely', '15:30 for full day trading']
        },
        
        // Strategy Parameters
        'indicator_period': {
            tooltip: 'Number of candles used to calculate technical indicators',
            help: 'Smaller periods (10-20) are more responsive, larger periods (50-200) are smoother',
            examples: ['20 for short-term signals', '50 for medium-term', '200 for long-term trends']
        },
        'position_sizing': {
            tooltip: 'Method used to determine how much capital to allocate per trade',
            help: 'Fixed Amount uses same size for all trades, Risk-Based adjusts based on stop loss',
            examples: ['Fixed: ₹10,000 per trade', 'Risk-Based: 1% of capital at risk']
        },
        'base_position_size': {
            tooltip: 'Base amount in rupees to invest per position',
            help: 'Should be appropriate for your capital and risk tolerance',
            examples: ['₹10,000 for small accounts', '₹50,000 for medium', '₹1,00,000+ for large']
        },
        'take_profit': {
            tooltip: 'Percentage gain at which to automatically close profitable positions',
            help: 'Set based on average market moves. Too tight = frequent exits, too wide = missed profits',
            examples: ['1-2% for intraday', '3-5% for swing trading', '2% for NIFTY futures']
        },
        'stop_loss': {
            tooltip: 'Percentage loss at which to automatically close losing positions',
            help: 'Critical for risk management. Should be wider than normal market noise',
            examples: ['0.5-1% for tight stops', '1-2% for normal', '0.75% for NIFTY futures']
        },
        
        // Risk Management
        'risk_per_trade': {
            tooltip: 'Maximum percentage of total capital to risk on a single trade',
            help: 'Professional traders typically risk 0.5-2% per trade. Never risk more than 5%',
            examples: ['0.5% for conservative', '1% for balanced', '2% for aggressive']
        },
        'max_positions': {
            tooltip: 'Maximum number of positions that can be open simultaneously',
            help: 'More positions = more diversification but harder to manage. Consider your capital',
            examples: ['1-2 for focused trading', '3-5 for diversification', '5-10 for large accounts']
        },
        'max_daily_loss': {
            tooltip: 'Maximum percentage loss allowed in a single day before bot stops trading',
            help: 'Protects against catastrophic losses on bad days. Bot will stop when limit is hit',
            examples: ['2% for conservative', '3-5% for balanced', '5-10% for aggressive']
        },
        
        // Advanced Settings
        'paper_trading': {
            tooltip: 'Simulate trading without using real money',
            help: 'Always test your strategy in paper trading mode first before going live',
            examples: ['Enable for testing new strategies', 'Disable only when confident']
        },
        'log_level': {
            tooltip: 'Amount of detail in log files',
            help: 'DEBUG shows everything (useful for troubleshooting), INFO shows important events',
            examples: ['DEBUG for development', 'INFO for production', 'ERROR for minimal logging']
        },
        'data_refresh_interval': {
            tooltip: 'How often (in seconds) to fetch new market data',
            help: 'Shorter intervals = more responsive but more API calls. Consider broker rate limits',
            examples: ['60 seconds for 5-min timeframe', '300 seconds for hourly', '30 seconds for 1-min']
        },
        'enable_notifications': {
            tooltip: 'Show browser notifications for important events',
            help: 'Get alerts for trades, errors, and important status changes',
            examples: ['Enable to stay informed', 'Disable if notifications are distracting']
        }
    },
    
    // Quick start guide steps
    quickStartSteps: [
        {
            title: 'Connect to Broker',
            description: 'Select your broker and enter credentials to connect your trading account',
            tab: 'broker',
            icon: '🔗'
        },
        {
            title: 'Select Instruments',
            description: 'Choose which stocks or instruments you want to trade',
            tab: 'instruments',
            icon: '📊'
        },
        {
            title: 'Configure Strategy',
            description: 'Set up your trading parameters, risk management, and strategy settings',
            tab: 'configuration',
            icon: '⚙️'
        },
        {
            title: 'Start Trading',
            description: 'Review your settings and start the bot to begin automated trading',
            tab: 'monitor',
            icon: '▶️'
        }
    ],
    
    // Initialize helpful features
    init() {
        this.addTooltipsToParameters();
        this.addExampleValues();
        this.createQuickStartGuide();
        this.addContextualHelp();
        this.addHelpButtons();
    },
    
    // Add tooltips to all form parameters
    addTooltipsToParameters() {
        const formGroups = document.querySelectorAll('.form-group');
        
        formGroups.forEach(group => {
            const input = group.querySelector('input, select, textarea');
            if (!input) return;
            
            const paramName = input.name || input.id.replace('config-', '').replace(/-/g, '_');
            const helpData = this.parameterHelp[paramName];
            
            if (helpData && helpData.tooltip) {
                const label = group.querySelector('label');
                if (label && !label.querySelector('.tooltip-wrapper')) {
                    const tooltipWrapper = this.createTooltip(helpData.tooltip);
                    label.appendChild(tooltipWrapper);
                }
            }
        });
    },
    
    // Create tooltip element
    createTooltip(text) {
        const wrapper = document.createElement('span');
        wrapper.className = 'tooltip-wrapper';
        wrapper.innerHTML = `
            <span class="tooltip-icon">?</span>
            <span class="tooltip-content">${text}</span>
        `;
        return wrapper;
    },
    
    // Add example values as placeholders or help text
    addExampleValues() {
        Object.keys(this.parameterHelp).forEach(paramName => {
            const helpData = this.parameterHelp[paramName];
            if (!helpData.examples || helpData.examples.length === 0) return;
            
            // Find the input element
            const input = document.querySelector(`[name="${paramName}"], #config-${paramName.replace(/_/g, '-')}`);
            if (!input) return;
            
            // Add example as help text below the input
            const formGroup = input.closest('.form-group');
            if (!formGroup) return;
            
            // Check if help text already exists
            let helpText = formGroup.querySelector('.form-help');
            if (!helpText) {
                helpText = document.createElement('small');
                helpText.className = 'form-help';
                input.parentNode.insertBefore(helpText, input.nextSibling);
            }
            
            // Add examples to help text
            const exampleText = `Examples: ${helpData.examples[0]}`;
            if (!helpText.textContent.includes('Examples:')) {
                helpText.textContent = helpText.textContent 
                    ? `${helpText.textContent}. ${exampleText}` 
                    : exampleText;
            }
        });
    },
    
    // Create quick start guide overlay
    createQuickStartGuide() {
        // Check if user has seen the guide before
        const hasSeenGuide = localStorage.getItem('hasSeenQuickStartGuide');
        
        // Create guide button in header
        const header = document.querySelector('.dashboard-header .container');
        if (header && !document.getElementById('quick-start-btn')) {
            const guideButton = document.createElement('button');
            guideButton.id = 'quick-start-btn';
            guideButton.className = 'btn btn-sm btn-secondary';
            guideButton.innerHTML = '<span class="btn-icon">📖</span> Quick Start';
            guideButton.onclick = () => this.showQuickStartGuide();
            
            // Add to header status area
            const headerStatus = header.querySelector('.header-status');
            if (headerStatus) {
                headerStatus.appendChild(guideButton);
            }
        }
        
        // Show guide automatically for first-time users
        if (!hasSeenGuide) {
            setTimeout(() => this.showQuickStartGuide(), 1000);
        }
    },
    
    // Show quick start guide modal
    showQuickStartGuide() {
        // Create modal overlay
        const overlay = document.createElement('div');
        overlay.className = 'quick-start-overlay';
        overlay.innerHTML = `
            <div class="quick-start-modal">
                <div class="quick-start-header">
                    <h2>✈️ Start Here</h2>
                    <button class="close-btn" onclick="HelpfulFeatures.closeQuickStartGuide()">&times;</button>
                </div>
                <div class="quick-start-content">
                    <p class="quick-start-intro">
                        Welcome to the Indian Market Trading Dashboard! Follow these steps to get started:
                    </p>
                    <div class="quick-start-steps">
                        ${this.quickStartSteps.map((step, index) => `
                            <div class="quick-start-step" data-tab="${step.tab}">
                                <div class="step-number">${index + 1}</div>
                                <div class="step-icon">${step.icon}</div>
                                <div class="step-content">
                                    <h3>${step.title}</h3>
                                    <p>${step.description}</p>
                                    <button class="btn btn-sm btn-primary" onclick="HelpfulFeatures.goToStep('${step.tab}')">
                                        Go to ${step.title}
                                    </button>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                    <div class="quick-start-footer">
                        <label>
                            <input type="checkbox" id="dont-show-again"> Don't show this again
                        </label>
                        <button class="btn btn-primary" onclick="HelpfulFeatures.closeQuickStartGuide()">
                            Get Started
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(overlay);
        
        // Add click outside to close
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                this.closeQuickStartGuide();
            }
        });
    },
    
    // Close quick start guide
    closeQuickStartGuide() {
        const overlay = document.querySelector('.quick-start-overlay');
        if (overlay) {
            // Check if user selected "don't show again"
            const dontShowAgain = document.getElementById('dont-show-again');
            if (dontShowAgain && dontShowAgain.checked) {
                localStorage.setItem('hasSeenQuickStartGuide', 'true');
            }
            
            overlay.remove();
        }
    },
    
    // Navigate to a specific step
    goToStep(tabName) {
        this.closeQuickStartGuide();
        
        // Click the appropriate tab
        const tabButton = document.querySelector(`[data-tab="${tabName}"]`);
        if (tabButton) {
            tabButton.click();
        }
    },
    
    // Add contextual help panels
    addContextualHelp() {
        // Add help panel to each configuration section
        const configSections = document.querySelectorAll('.config-section');
        
        configSections.forEach(section => {
            const sectionName = section.dataset.configSection;
            const helpContent = this.getContextualHelpForSection(sectionName);
            
            if (helpContent && !section.querySelector('.contextual-help-panel')) {
                const helpPanel = document.createElement('div');
                helpPanel.className = 'contextual-help-panel';
                helpPanel.innerHTML = `
                    <div class="help-panel-header">
                        <span class="help-icon">💡</span>
                        <h4>Tips for ${this.getSectionTitle(sectionName)}</h4>
                        <button class="help-toggle-btn" onclick="this.parentElement.parentElement.classList.toggle('collapsed')">
                            <span class="toggle-icon">−</span>
                        </button>
                    </div>
                    <div class="help-panel-content">
                        ${helpContent}
                    </div>
                `;
                
                // Insert at the beginning of the section
                section.insertBefore(helpPanel, section.firstChild.nextSibling);
            }
        });
    },
    
    // Get contextual help content for each section
    getContextualHelpForSection(sectionName) {
        const helpContent = {
            'basic': `
                <ul class="help-list">
                    <li><strong>Timeframe:</strong> Start with 5-minute for intraday trading</li>
                    <li><strong>Trading Hours:</strong> Indian markets: 09:15 AM - 03:30 PM IST</li>
                    <li><strong>Strategy:</strong> Trend Following works well for NIFTY/BANKNIFTY</li>
                    <li><strong>Tip:</strong> Test with paper trading before going live!</li>
                </ul>
            `,
            'strategy': `
                <ul class="help-list">
                    <li><strong>Indicator Period:</strong> 20 is a good starting point for most strategies</li>
                    <li><strong>Take Profit:</strong> Set 2x your stop loss for 1:2 risk-reward ratio</li>
                    <li><strong>Stop Loss:</strong> Keep it tight (0.5-1%) for intraday, wider (1-2%) for swing</li>
                    <li><strong>Position Sizing:</strong> Risk-based is recommended for better risk management</li>
                </ul>
            `,
            'risk': `
                <ul class="help-list">
                    <li><strong>Risk Per Trade:</strong> Never risk more than 1-2% of your capital per trade</li>
                    <li><strong>Max Positions:</strong> Start with 2-3 positions to manage risk</li>
                    <li><strong>Daily Loss Limit:</strong> Set to 3-5% to protect your capital on bad days</li>
                    <li><strong>Important:</strong> These limits will automatically stop the bot to protect you</li>
                </ul>
            `,
            'advanced': `
                <ul class="help-list">
                    <li><strong>Paper Trading:</strong> Always test new strategies here first</li>
                    <li><strong>Log Level:</strong> Use DEBUG when testing, INFO for live trading</li>
                    <li><strong>Refresh Interval:</strong> 60 seconds is good for most timeframes</li>
                    <li><strong>Notifications:</strong> Enable to get alerts for trades and errors</li>
                </ul>
            `
        };
        
        return helpContent[sectionName] || '';
    },
    
    // Get section title
    getSectionTitle(sectionName) {
        const titles = {
            'basic': 'Basic Settings',
            'strategy': 'Strategy Parameters',
            'risk': 'Risk Management',
            'advanced': 'Advanced Settings'
        };
        return titles[sectionName] || sectionName;
    },
    
    // Add help buttons throughout the interface
    addHelpButtons() {
        // Add help button to instruments tab
        this.addInstrumentsHelp();
        
        // Add help button to monitor tab
        this.addMonitorHelp();
        
        // Add help button to trades tab
        this.addTradesHelp();
    },
    
    // Add help for instruments tab
    addInstrumentsHelp() {
        const instrumentsTab = document.getElementById('instruments-tab');
        if (!instrumentsTab || instrumentsTab.querySelector('.tab-help-panel')) return;
        
        const helpPanel = document.createElement('div');
        helpPanel.className = 'tab-help-panel';
        helpPanel.innerHTML = `
            <div class="help-banner">
                <span class="help-icon">💡</span>
                <div class="help-text">
                    <strong>Tip:</strong> Use filters to narrow down instruments. 
                    For NIFTY futures, select NFO exchange and FUT type. 
                    You can select multiple instruments for diversification.
                </div>
                <button class="help-close-btn" onclick="this.parentElement.parentElement.remove()">&times;</button>
            </div>
        `;
        
        instrumentsTab.insertBefore(helpPanel, instrumentsTab.firstChild.nextSibling);
    },
    
    // Add help for monitor tab
    addMonitorHelp() {
        const monitorTab = document.getElementById('monitor-tab');
        if (!monitorTab || monitorTab.querySelector('.tab-help-panel')) return;
        
        const helpPanel = document.createElement('div');
        helpPanel.className = 'tab-help-panel';
        helpPanel.innerHTML = `
            <div class="help-banner">
                <span class="help-icon">💡</span>
                <div class="help-text">
                    <strong>Tip:</strong> This page auto-refreshes every 5 seconds. 
                    Monitor your positions and P&L in real-time. 
                    You can manually stop the bot anytime if needed.
                </div>
                <button class="help-close-btn" onclick="this.parentElement.parentElement.remove()">&times;</button>
            </div>
        `;
        
        monitorTab.insertBefore(helpPanel, monitorTab.firstChild.nextSibling);
    },
    
    // Add help for trades tab
    addTradesHelp() {
        const tradesTab = document.getElementById('trades-tab');
        if (!tradesTab || tradesTab.querySelector('.tab-help-panel')) return;
        
        const helpPanel = document.createElement('div');
        helpPanel.className = 'tab-help-panel';
        helpPanel.innerHTML = `
            <div class="help-banner">
                <span class="help-icon">💡</span>
                <div class="help-text">
                    <strong>Tip:</strong> Review your trade history to analyze performance. 
                    Use date filters to view specific periods. 
                    Export trades to Excel for detailed analysis.
                </div>
                <button class="help-close-btn" onclick="this.parentElement.parentElement.remove()">&times;</button>
            </div>
        `;
        
        tradesTab.insertBefore(helpPanel, tradesTab.firstChild.nextSibling);
    },
    
    // Show parameter help in a modal
    showParameterHelp(paramName) {
        const helpData = this.parameterHelp[paramName];
        if (!helpData) return;
        
        const modal = document.createElement('div');
        modal.className = 'parameter-help-modal-overlay';
        modal.innerHTML = `
            <div class="parameter-help-modal">
                <div class="modal-header">
                    <h3>${this.formatParameterName(paramName)}</h3>
                    <button class="close-btn" onclick="this.parentElement.parentElement.parentElement.remove()">&times;</button>
                </div>
                <div class="modal-content">
                    <div class="help-section">
                        <h4>What is this?</h4>
                        <p>${helpData.tooltip}</p>
                    </div>
                    ${helpData.help ? `
                        <div class="help-section">
                            <h4>How to use it</h4>
                            <p>${helpData.help}</p>
                        </div>
                    ` : ''}
                    ${helpData.examples && helpData.examples.length > 0 ? `
                        <div class="help-section">
                            <h4>Examples</h4>
                            <ul>
                                ${helpData.examples.map(ex => `<li>${ex}</li>`).join('')}
                            </ul>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Close on click outside
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
    },
    
    // Format parameter name for display
    formatParameterName(paramName) {
        return paramName
            .split('_')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
    }
};

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => HelpfulFeatures.init());
} else {
    HelpfulFeatures.init();
}
