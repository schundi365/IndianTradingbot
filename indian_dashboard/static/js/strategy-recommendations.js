/**
 * Strategy Recommendations Module
 * Shows recommended configuration and indicator values based on selected strategy
 */

const StrategyRecommendations = {
    // Strategy-specific recommendations
    recommendations: {
        'breakout': {
            name: 'Breakout Strategy',
            description: 'Trades price breakouts above resistance or below support levels',
            indicators: {
                'RSI Period': { value: 14, range: '10-20', description: 'Standard period for momentum confirmation' },
                'RSI Overbought': { value: 70, range: '65-75', description: 'Higher threshold for strong breakouts' },
                'RSI Oversold': { value: 30, range: '25-35', description: 'Lower threshold for strong breakdowns' },
                'MACD Fast': { value: 12, range: '8-15', description: 'Faster response to price changes' },
                'MACD Slow': { value: 26, range: '20-30', description: 'Trend confirmation' },
                'MACD Signal': { value: 9, range: '7-12', description: 'Signal line for entry timing' },
                'ADX Period': { value: 14, range: '10-20', description: 'Trend strength measurement' },
                'ADX Threshold': { value: 25, range: '20-30', description: 'Strong trend confirmation' },
                'Bollinger Period': { value: 20, range: '15-25', description: 'Volatility bands' },
                'Bollinger Std Dev': { value: 2.0, range: '1.5-2.5', description: 'Band width multiplier' }
            },
            riskManagement: {
                'Take Profit': { value: 2.0, range: '1.5-3.0', description: 'Risk-reward ratio for breakouts' },
                'Stop Loss': { value: 1.0, range: '0.8-1.5', description: 'Tight stops below breakout level' },
                'Position Sizing': { value: 'risk_based', description: 'Size based on stop loss distance' },
                'Max Positions': { value: 3, range: '2-5', description: 'Limit concurrent breakout trades' }
            },
            tips: [
                'Wait for volume confirmation on breakouts',
                'Use ADX > 25 to confirm strong trends',
                'Place stops just below breakout level',
                'Take partial profits at 1.5R, let rest run to 2R'
            ]
        },
        'mean_reversion': {
            name: 'Mean Reversion Strategy',
            description: 'Trades price returns to average after extreme moves',
            indicators: {
                'RSI Period': { value: 14, range: '10-20', description: 'Overbought/oversold detection' },
                'RSI Overbought': { value: 75, range: '70-80', description: 'Extreme overbought for reversal' },
                'RSI Oversold': { value: 25, range: '20-30', description: 'Extreme oversold for reversal' },
                'MACD Fast': { value: 12, range: '10-15', description: 'Divergence detection' },
                'MACD Slow': { value: 26, range: '20-30', description: 'Trend baseline' },
                'MACD Signal': { value: 9, range: '7-12', description: 'Reversal signal' },
                'ADX Period': { value: 14, range: '10-20', description: 'Avoid strong trends' },
                'ADX Threshold': { value: 20, range: '15-25', description: 'Trade in ranging markets (ADX < 20)' },
                'Bollinger Period': { value: 20, range: '15-25', description: 'Mean reversion bands' },
                'Bollinger Std Dev': { value: 2.0, range: '2.0-2.5', description: 'Wider bands for extremes' }
            },
            riskManagement: {
                'Take Profit': { value: 1.5, range: '1.0-2.0', description: 'Quick profits on reversals' },
                'Stop Loss': { value: 1.0, range: '0.8-1.2', description: 'Tight stops for failed reversals' },
                'Position Sizing': { value: 'percentage', description: 'Fixed percentage per trade' },
                'Max Positions': { value: 5, range: '3-7', description: 'More trades in ranging markets' }
            },
            tips: [
                'Trade when ADX < 20 (ranging market)',
                'Enter when price touches Bollinger Bands',
                'Exit when price returns to middle band',
                'Avoid trading during strong trends'
            ]
        },
        'trend_following': {
            name: 'Trend Following Strategy',
            description: 'Follows established trends using moving averages and momentum',
            indicators: {
                'RSI Period': { value: 14, range: '10-20', description: 'Momentum confirmation' },
                'RSI Overbought': { value: 60, range: '55-65', description: 'Lower threshold in uptrends' },
                'RSI Oversold': { value: 40, range: '35-45', description: 'Higher threshold in downtrends' },
                'MACD Fast': { value: 12, range: '10-15', description: 'Trend direction' },
                'MACD Slow': { value: 26, range: '20-30', description: 'Trend strength' },
                'MACD Signal': { value: 9, range: '7-12', description: 'Entry timing' },
                'ADX Period': { value: 14, range: '10-20', description: 'Trend strength' },
                'ADX Threshold': { value: 25, range: '20-30', description: 'Strong trend required' },
                'Bollinger Period': { value: 20, range: '15-25', description: 'Trend channel' },
                'Bollinger Std Dev': { value: 2.0, range: '1.5-2.5', description: 'Volatility adjustment' }
            },
            riskManagement: {
                'Take Profit': { value: 3.0, range: '2.0-4.0', description: 'Let winners run in trends' },
                'Stop Loss': { value: 1.5, range: '1.0-2.0', description: 'Wider stops for trend continuation' },
                'Position Sizing': { value: 'risk_based', description: 'Scale into trends' },
                'Max Positions': { value: 3, range: '2-4', description: 'Focus on strong trends' }
            },
            tips: [
                'Only trade when ADX > 25',
                'Enter on pullbacks to moving average',
                'Trail stops using ATR or moving average',
                'Add to winning positions in strong trends'
            ]
        },
        'scalping': {
            name: 'Scalping Strategy',
            description: 'Quick trades capturing small price movements',
            indicators: {
                'RSI Period': { value: 7, range: '5-10', description: 'Fast momentum for quick trades' },
                'RSI Overbought': { value: 70, range: '65-75', description: 'Quick reversal signals' },
                'RSI Oversold': { value: 30, range: '25-35', description: 'Quick reversal signals' },
                'MACD Fast': { value: 5, range: '3-8', description: 'Very fast response' },
                'MACD Slow': { value: 13, range: '10-15', description: 'Quick trend detection' },
                'MACD Signal': { value: 5, range: '3-7', description: 'Fast signal line' },
                'ADX Period': { value: 7, range: '5-10', description: 'Quick trend strength' },
                'ADX Threshold': { value: 20, range: '15-25', description: 'Moderate trend needed' },
                'Bollinger Period': { value: 10, range: '8-15', description: 'Tight volatility bands' },
                'Bollinger Std Dev': { value: 1.5, range: '1.0-2.0', description: 'Narrow bands for quick moves' }
            },
            riskManagement: {
                'Take Profit': { value: 1.0, range: '0.5-1.5', description: 'Quick small profits' },
                'Stop Loss': { value: 0.5, range: '0.3-0.8', description: 'Very tight stops' },
                'Position Sizing': { value: 'fixed', description: 'Consistent size per trade' },
                'Max Positions': { value: 1, range: '1-2', description: 'Focus on one trade at a time' }
            },
            tips: [
                'Use 1-minute or 5-minute timeframes',
                'Trade during high liquidity hours',
                'Exit quickly if trade goes against you',
                'Take profits at first target, don\'t be greedy'
            ]
        }
    },

    /**
     * Initialize the recommendations system
     */
    init() {
        console.log('Strategy Recommendations: Initializing...');
        
        // Check if strategy selector exists
        const strategySelect = document.getElementById('config-strategy');
        if (!strategySelect) {
            console.error('Strategy Recommendations: Strategy selector not found, will retry...');
            // Retry after a delay
            setTimeout(() => this.init(), 1000);
            return;
        }
        
        this.createRecommendationsPanel();
        this.setupStrategyListener();
        console.log('Strategy Recommendations: Initialized successfully');
    },

    /**
     * Setup listener for strategy selection changes
     */
    setupStrategyListener() {
        const strategySelect = document.getElementById('config-strategy');
        if (strategySelect) {
            console.log('Strategy Recommendations: Setting up listener on strategy selector');
            strategySelect.addEventListener('change', (e) => {
                console.log('Strategy Recommendations: Strategy changed to', e.target.value);
                this.showRecommendations(e.target.value);
            });
            
            // Show recommendations for initially selected strategy
            if (strategySelect.value && strategySelect.value !== '') {
                console.log('Strategy Recommendations: Showing initial recommendations for', strategySelect.value);
                this.showRecommendations(strategySelect.value);
            }
        } else {
            console.error('Strategy Recommendations: Strategy selector not found in setupStrategyListener');
        }
    },

    /**
     * Create the recommendations panel in the UI
     */
    createRecommendationsPanel() {
        console.log('Strategy Recommendations: Creating panel...');
        
        // Create recommendations container
        const recommendationsDiv = document.createElement('div');
        recommendationsDiv.id = 'strategy-recommendations';
        recommendationsDiv.className = 'strategy-recommendations';
        recommendationsDiv.style.display = 'none';

        // Insert after strategy selector in Basic Settings section
        const strategyGroup = document.getElementById('config-strategy')?.closest('.form-group');
        if (strategyGroup) {
            strategyGroup.parentNode.insertBefore(recommendationsDiv, strategyGroup.nextSibling);
            console.log('Strategy Recommendations: Panel created successfully');
        } else {
            console.error('Strategy Recommendations: Could not find strategy selector');
        }
    },

    /**
     * Show recommendations for selected strategy
     */
    showRecommendations(strategy) {
        console.log('Strategy Recommendations: showRecommendations called with strategy:', strategy);
        
        const container = document.getElementById('strategy-recommendations');
        if (!container) {
            console.error('Strategy Recommendations: Container not found!');
            return;
        }

        const rec = this.recommendations[strategy];
        if (!rec) {
            console.log('Strategy Recommendations: No recommendations for strategy:', strategy);
            container.style.display = 'none';
            return;
        }

        console.log('Strategy Recommendations: Building recommendations panel for', rec.name);

        container.innerHTML = `
            <div class="recommendations-card">
                <div class="recommendations-header">
                    <span class="recommendations-icon">💡</span>
                    <div>
                        <h4>${rec.name} - Recommended Settings</h4>
                        <p>${rec.description}</p>
                    </div>
                </div>

                <div class="recommendations-content">
                    <!-- Technical Indicators -->
                    <div class="recommendations-section">
                        <h5>📊 Technical Indicators</h5>
                        <div class="recommendations-grid">
                            ${Object.entries(rec.indicators).map(([name, config]) => `
                                <div class="recommendation-item">
                                    <div class="recommendation-label">${name}</div>
                                    <div class="recommendation-value">${config.value}</div>
                                    <div class="recommendation-range">Range: ${config.range}</div>
                                    <div class="recommendation-desc">${config.description}</div>
                                </div>
                            `).join('')}
                        </div>
                    </div>

                    <!-- Risk Management -->
                    <div class="recommendations-section">
                        <h5>🛡️ Risk Management</h5>
                        <div class="recommendations-grid">
                            ${Object.entries(rec.riskManagement).map(([name, config]) => `
                                <div class="recommendation-item">
                                    <div class="recommendation-label">${name}</div>
                                    <div class="recommendation-value">${config.value}</div>
                                    ${config.range ? `<div class="recommendation-range">Range: ${config.range}</div>` : ''}
                                    <div class="recommendation-desc">${config.description}</div>
                                </div>
                            `).join('')}
                        </div>
                    </div>

                    <!-- Trading Tips -->
                    <div class="recommendations-section">
                        <h5>💭 Trading Tips</h5>
                        <ul class="recommendations-tips">
                            ${rec.tips.map(tip => `<li>${tip}</li>`).join('')}
                        </ul>
                    </div>

                    <!-- Apply Button -->
                    <div class="recommendations-actions">
                        <button type="button" class="btn btn-primary" onclick="StrategyRecommendations.applyRecommendations('${strategy}')">
                            <span class="btn-icon">✨</span> Apply Recommended Settings
                        </button>
                        <button type="button" class="btn btn-secondary" onclick="StrategyRecommendations.hideRecommendations()">
                            <span class="btn-icon">✕</span> Close
                        </button>
                    </div>
                </div>
            </div>
        `;

        container.style.display = 'block';
        console.log('Strategy Recommendations: Panel displayed');
    },

    /**
     * Apply recommended settings to the form
     */
    applyRecommendations(strategy) {
        const rec = this.recommendations[strategy];
        if (!rec) return;

        // Apply indicator settings (this would need to map to actual form fields)
        // For now, just show a confirmation
        if (confirm(`Apply recommended settings for ${rec.name}?\n\nThis will update your indicator and risk management parameters.`)) {
            // Apply risk management settings
            const positionSizing = document.getElementById('config-position-sizing');
            if (positionSizing && rec.riskManagement['Position Sizing']) {
                positionSizing.value = rec.riskManagement['Position Sizing'].value;
                positionSizing.dispatchEvent(new Event('change'));
            }

            const takeProfit = document.getElementById('config-take-profit');
            if (takeProfit && rec.riskManagement['Take Profit']) {
                takeProfit.value = rec.riskManagement['Take Profit'].value;
                takeProfit.dispatchEvent(new Event('change'));
            }

            const stopLoss = document.getElementById('config-stop-loss');
            if (stopLoss && rec.riskManagement['Stop Loss']) {
                stopLoss.value = rec.riskManagement['Stop Loss'].value;
                stopLoss.dispatchEvent(new Event('change'));
            }

            showNotification('Recommended settings applied! Review and adjust as needed.', 'success');
        }
    },

    /**
     * Hide recommendations panel
     */
    hideRecommendations() {
        const container = document.getElementById('strategy-recommendations');
        if (container) {
            container.style.display = 'none';
        }
    }
};

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        // Wait a bit for other scripts to initialize
        setTimeout(() => StrategyRecommendations.init(), 500);
    });
} else {
    // DOM already loaded
    setTimeout(() => StrategyRecommendations.init(), 500);
}
