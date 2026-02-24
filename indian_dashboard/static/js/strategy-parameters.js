/**
 * Strategy Parameters Module
 * Handles strategy parameter inputs, validation, and real-time updates
 */

const StrategyParameters = {
    /**
     * Initialize strategy parameters
     */
    init() {
        this.setupInputListeners();
        this.setupPositionSizingToggle();
        this.setupValidation();
        this.updateParameterHelp();
    },

    /**
     * Setup input listeners for all strategy-related fields
     */
    setupInputListeners() {
        const inputs = [
            'config-indicator-period',
            'config-position-sizing',
            'config-base-position-size',
            'config-take-profit',
            'config-stop-loss',
            'config-loop-interval',
            'config-rsi-period',
            'config-rsi-overbought',
            'config-rsi-oversold',
            'config-macd-min-histogram',
            'config-roc-threshold',
            'config-min-trend-confidence',
            'config-trend-sensitivity',
            'config-adx-period',
            'config-adx-min-strength',
            'config-paper-trading-initial-balance'
        ];

        inputs.forEach(id => {
            const input = document.getElementById(id);
            if (input) {
                input.addEventListener('change', () => {
                    this.validateField(input);
                    this.updateDependentFields();
                    // Trigger risk metrics recalculation if RiskManagement is available
                    if (typeof RiskManagement !== 'undefined') {
                        RiskManagement.calculateMetrics();
                    }
                });

                input.addEventListener('input', () => {
                    this.validateField(input);
                });
            }
        });

        // Strategy selector
        const strategySelect = document.getElementById('config-strategy');
        if (strategySelect) {
            strategySelect.addEventListener('change', () => {
                this.updateStrategyParameters();
            });
        }
    },

    /**
     * Setup position sizing method toggle
     */
    setupPositionSizingToggle() {
        const positionSizingSelect = document.getElementById('config-position-sizing');
        const basePositionSizeGroup = document.getElementById('config-base-position-size')?.closest('.form-group');

        if (positionSizingSelect && basePositionSizeGroup) {
            positionSizingSelect.addEventListener('change', (e) => {
                const method = e.target.value;

                // Update label based on method
                const label = basePositionSizeGroup.querySelector('label');
                if (label) {
                    switch (method) {
                        case 'fixed':
                            label.textContent = 'Base Position Size (₹)';
                            break;
                        case 'percentage':
                            label.textContent = 'Position Size (% of Capital)';
                            break;
                        case 'risk_based':
                            label.textContent = 'Risk Amount (₹)';
                            break;
                    }
                }

                // Update help text
                const helpText = basePositionSizeGroup.querySelector('.form-help');
                if (helpText) {
                    switch (method) {
                        case 'fixed':
                            helpText.textContent = 'Fixed amount to invest per trade';
                            break;
                        case 'percentage':
                            helpText.textContent = 'Percentage of total capital to invest per trade';
                            break;
                        case 'risk_based':
                            helpText.textContent = 'Position size calculated based on risk per trade';
                            break;
                    }
                }
            });
        }
    },

    /**
     * Setup real-time validation
     */
    setupValidation() {
        // Indicator period validation
        const indicatorPeriod = document.getElementById('config-indicator-period');
        if (indicatorPeriod) {
            indicatorPeriod.addEventListener('blur', () => {
                const value = parseInt(indicatorPeriod.value);
                if (value < 5) {
                    this.showFieldError(indicatorPeriod, 'Period should be at least 5');
                } else if (value > 200) {
                    this.showFieldError(indicatorPeriod, 'Period should not exceed 200');
                } else {
                    this.clearFieldError(indicatorPeriod);
                }
            });
        }

        // Take profit validation
        const takeProfit = document.getElementById('config-take-profit');
        if (takeProfit) {
            takeProfit.addEventListener('blur', () => {
                const value = parseFloat(takeProfit.value);
                if (value < 0.5) {
                    this.showFieldError(takeProfit, 'Take profit should be at least 0.5%');
                } else if (value > 20) {
                    this.showFieldError(takeProfit, 'Take profit seems too high (>20%)');
                } else {
                    this.clearFieldError(takeProfit);
                }
            });
        }

        // Stop loss validation
        const stopLoss = document.getElementById('config-stop-loss');
        if (stopLoss) {
            stopLoss.addEventListener('blur', () => {
                const value = parseFloat(stopLoss.value);
                const tpValue = parseFloat(takeProfit?.value || 2.0);

                if (value < 0.5) {
                    this.showFieldError(stopLoss, 'Stop loss should be at least 0.5%');
                } else if (value > 10) {
                    this.showFieldError(stopLoss, 'Stop loss seems too high (>10%)');
                } else if (value > tpValue) {
                    this.showFieldError(stopLoss, 'Stop loss should be less than take profit');
                } else {
                    this.clearFieldError(stopLoss);
                }
            });
        }

        // Base position size validation
        const basePositionSize = document.getElementById('config-base-position-size');
        if (basePositionSize) {
            basePositionSize.addEventListener('blur', () => {
                const value = parseFloat(basePositionSize.value);
                if (value < 1000) {
                    this.showFieldError(basePositionSize, 'Position size should be at least ₹1,000');
                } else {
                    this.clearFieldError(basePositionSize);
                }
            });
        }
    },

    /**
     * Validate a single field
     */
    validateField(field) {
        const value = field.value;
        const min = field.min;
        const max = field.max;
        let isValid = true;

        // Check if field has value
        if (field.hasAttribute('required') && !value) {
            isValid = false;
        }

        // Check min/max for number inputs
        if (field.type === 'number' && value) {
            const numValue = parseFloat(value);
            if (min && numValue < parseFloat(min)) {
                isValid = false;
            }
            if (max && numValue > parseFloat(max)) {
                isValid = false;
            }
        }

        // Update field styling
        if (isValid) {
            field.classList.remove('invalid');
            field.classList.add('valid');
        } else {
            field.classList.remove('valid');
            field.classList.add('invalid');
        }

        return isValid;
    },

    /**
     * Show field error
     */
    showFieldError(field, message) {
        field.classList.add('invalid');
        field.classList.remove('valid');

        // Remove existing error message
        const existingError = field.parentElement.querySelector('.form-error');
        if (existingError) {
            existingError.remove();
        }

        // Add new error message
        const errorElement = document.createElement('small');
        errorElement.className = 'form-error';
        errorElement.textContent = message;
        field.parentElement.appendChild(errorElement);
    },

    /**
     * Clear field error
     */
    clearFieldError(field) {
        field.classList.remove('invalid');
        field.classList.add('valid');

        const existingError = field.parentElement.querySelector('.form-error');
        if (existingError) {
            existingError.remove();
        }
    },

    /**
     * Update dependent fields when values change
     */
    updateDependentFields() {
        const takeProfit = parseFloat(document.getElementById('config-take-profit')?.value || 2.0);
        const stopLoss = parseFloat(document.getElementById('config-stop-loss')?.value || 1.0);

        // Calculate and display risk/reward ratio
        const riskRewardRatio = takeProfit / stopLoss;

        // You can add visual feedback here if needed
        if (riskRewardRatio < 1.5) {
            // Show warning for poor risk/reward
            console.log('Warning: Risk/Reward ratio is below 1.5:1');
        }
    },

    /**
     * Update strategy-specific parameters
     */
    updateStrategyParameters() {
        const strategy = document.getElementById('config-strategy')?.value;
        const indicatorPeriod = document.getElementById('config-indicator-period');

        if (!strategy || !indicatorPeriod) return;

        // Set recommended indicator periods based on strategy
        const recommendedPeriods = {
            'trend_following': 20,
            'momentum': 14,
            'mean_reversion': 20,
            'breakout': 20
        };

        const recommended = recommendedPeriods[strategy];
        if (recommended && indicatorPeriod.value == indicatorPeriod.defaultValue) {
            indicatorPeriod.value = recommended;
        }

        // Update help text based on strategy
        this.updateParameterHelp();
    },

    /**
     * Update parameter help text based on selected strategy
     */
    updateParameterHelp() {
        const strategy = document.getElementById('config-strategy')?.value;
        const indicatorPeriodHelp = document.querySelector('#config-indicator-period + .form-help');

        if (!strategy || !indicatorPeriodHelp) return;

        const helpTexts = {
            'trend_following': 'Typical: 20 for moving averages, 14 for ADX',
            'momentum': 'Typical: 14 for RSI, 12-26 for MACD',
            'mean_reversion': 'Typical: 20 for Bollinger Bands',
            'breakout': 'Typical: 20 for volatility calculation'
        };

        indicatorPeriodHelp.textContent = helpTexts[strategy] || 'Number of periods for indicator calculation';
    },

    /**
     * Get strategy parameters
     */
    getParameters() {
        return {
            indicator_period: parseInt(document.getElementById('config-indicator-period')?.value || 20),
            position_sizing: document.getElementById('config-position-sizing')?.value || 'fixed',
            base_position_size: parseFloat(document.getElementById('config-base-position-size')?.value || 10000),
            take_profit: parseFloat(document.getElementById('config-take-profit')?.value || 2.0),
            stop_loss: parseFloat(document.getElementById('config-stop-loss')?.value || 1.0),
            loop_interval: parseInt(document.getElementById('config-loop-interval')?.value || 60),
            rsi_period: parseInt(document.getElementById('config-rsi-period')?.value || 14),
            rsi_overbought: parseInt(document.getElementById('config-rsi-overbought')?.value || 70),
            rsi_oversold: parseInt(document.getElementById('config-rsi-oversold')?.value || 30),
            macd_min_histogram: parseFloat(document.getElementById('config-macd-min-histogram')?.value || 0.0005),
            roc_threshold: parseFloat(document.getElementById('config-roc-threshold')?.value || 0.15),
            min_trend_confidence: parseFloat(document.getElementById('config-min-trend-confidence')?.value || 0.6),
            trend_detection_sensitivity: parseInt(document.getElementById('config-trend-sensitivity')?.value || 5),
            adx_period: parseInt(document.getElementById('config-adx-period')?.value || 14),
            adx_min_strength: parseInt(document.getElementById('config-adx-min-strength')?.value || 25),
            paper_trading_initial_balance: parseFloat(document.getElementById('config-paper-trading-initial-balance')?.value || 5000000)
        };
    },

    /**
     * Set strategy parameters
     */
    setParameters(params) {
        if (!params) return;

        if (params.indicator_period !== undefined) {
            const field = document.getElementById('config-indicator-period');
            if (field) field.value = params.indicator_period;
        }

        if (params.position_sizing !== undefined) {
            const field = document.getElementById('config-position-sizing');
            if (field) {
                field.value = params.position_sizing;
                // Trigger change event to update labels
                field.dispatchEvent(new Event('change'));
            }
        }

        if (params.base_position_size !== undefined) {
            const field = document.getElementById('config-base-position-size');
            if (field) field.value = params.base_position_size;
        }

        if (params.take_profit !== undefined) {
            const field = document.getElementById('config-take-profit');
            if (field) field.value = params.take_profit;
        }

        if (params.stop_loss !== undefined) {
            const field = document.getElementById('config-stop-loss');
            if (field) field.value = params.stop_loss;
        }

        // New Indicator Fields
        const indicatorFields = [
            'loop_interval', 'rsi_period', 'rsi_overbought', 'rsi_oversold',
            'macd_min_histogram', 'roc_threshold', 'min_trend_confidence',
            'trend_detection_sensitivity', 'adx_period', 'adx_min_strength',
            'paper_trading_initial_balance'
        ];

        indicatorFields.forEach(key => {
            if (params[key] !== undefined) {
                const field = document.getElementById(`config-${key.replace(/_/g, '-')}`);
                if (field) field.value = params[key];
            }
        });

        // Recalculate metrics
        this.updateDependentFields();
        if (typeof RiskManagement !== 'undefined') {
            RiskManagement.calculateMetrics();
        }
    },

    /**
     * Validate all strategy parameters
     */
    validateAll() {
        const errors = [];

        const indicatorPeriod = parseInt(document.getElementById('config-indicator-period')?.value || 20);
        if (indicatorPeriod < 5 || indicatorPeriod > 200) {
            errors.push('Indicator period must be between 5 and 200');
        }

        const basePositionSize = parseFloat(document.getElementById('config-base-position-size')?.value || 10000);
        if (basePositionSize < 1000) {
            errors.push('Base position size must be at least ₹1,000');
        }

        const takeProfit = parseFloat(document.getElementById('config-take-profit')?.value || 2.0);
        if (takeProfit < 0.5 || takeProfit > 20) {
            errors.push('Take profit must be between 0.5% and 20%');
        }

        const stopLoss = parseFloat(document.getElementById('config-stop-loss')?.value || 1.0);
        if (stopLoss < 0.5 || stopLoss > 10) {
            errors.push('Stop loss must be between 0.5% and 10%');
        }

        if (stopLoss >= takeProfit) {
            errors.push('Stop loss must be less than take profit');
        }

        const riskRewardRatio = takeProfit / stopLoss;
        if (riskRewardRatio < 1) {
            errors.push('Risk/Reward ratio should be at least 1:1');
        }

        return {
            valid: errors.length === 0,
            errors
        };
    }
};

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => StrategyParameters.init());
} else {
    StrategyParameters.init();
}
