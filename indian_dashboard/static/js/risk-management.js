/**
 * Risk Management Module
 * Handles risk calculations, slider synchronization, and metrics display
 */

const RiskManagement = {
    // Default capital for calculations (can be updated from account info)
    capital: 100000,

    /**
     * Initialize risk management
     */
    init() {
        this.setupSliders();
        this.setupInputListeners();
        this.calculateMetrics();
    },

    /**
     * Setup slider synchronization
     */
    setupSliders() {
        // Risk per trade slider
        const riskSlider = document.getElementById('config-risk-per-trade-slider');
        const riskInput = document.getElementById('config-risk-per-trade');
        
        if (riskSlider && riskInput) {
            // Sync slider to input
            riskSlider.addEventListener('input', (e) => {
                riskInput.value = e.target.value;
                this.calculateMetrics();
            });
            
            // Sync input to slider
            riskInput.addEventListener('input', (e) => {
                riskSlider.value = e.target.value;
                this.calculateMetrics();
            });
        }

        // Max daily loss slider
        const dailyLossSlider = document.getElementById('config-max-daily-loss-slider');
        const dailyLossInput = document.getElementById('config-max-daily-loss');
        
        if (dailyLossSlider && dailyLossInput) {
            // Sync slider to input
            dailyLossSlider.addEventListener('input', (e) => {
                dailyLossInput.value = e.target.value;
                this.calculateMetrics();
            });
            
            // Sync input to slider
            dailyLossInput.addEventListener('input', (e) => {
                dailyLossSlider.value = e.target.value;
                this.calculateMetrics();
            });
        }
    },

    /**
     * Setup input listeners for all risk-related fields
     */
    setupInputListeners() {
        const inputs = [
            'config-risk-per-trade',
            'config-max-positions',
            'config-max-daily-loss',
            'config-base-position-size',
            'config-stop-loss',
            'config-take-profit'
        ];

        inputs.forEach(id => {
            const input = document.getElementById(id);
            if (input) {
                input.addEventListener('change', () => this.calculateMetrics());
                input.addEventListener('input', () => this.calculateMetrics());
            }
        });
    },

    /**
     * Calculate and display risk metrics
     */
    calculateMetrics() {
        const riskPerTrade = parseFloat(document.getElementById('config-risk-per-trade')?.value || 1.0);
        const maxPositions = parseInt(document.getElementById('config-max-positions')?.value || 3);
        const maxDailyLoss = parseFloat(document.getElementById('config-max-daily-loss')?.value || 3.0);
        const basePositionSize = parseFloat(document.getElementById('config-base-position-size')?.value || 10000);
        const stopLoss = parseFloat(document.getElementById('config-stop-loss')?.value || 1.0);
        const takeProfit = parseFloat(document.getElementById('config-take-profit')?.value || 2.0);

        // Calculate risk amount per trade
        const riskAmount = (this.capital * riskPerTrade) / 100;

        // Calculate max position size based on risk and stop loss
        // Position Size = Risk Amount / (Stop Loss %)
        const maxPositionSize = (riskAmount / stopLoss) * 100;

        // Calculate total risk exposure (all positions)
        const totalRiskExposure = riskAmount * maxPositions;

        // Calculate max daily loss amount
        const maxDailyLossAmount = (this.capital * maxDailyLoss) / 100;

        // Calculate capital required (for all positions)
        const capitalRequired = basePositionSize * maxPositions;

        // Calculate risk/reward ratio
        const riskRewardRatio = takeProfit / stopLoss;

        // Update display
        this.updateMetricDisplay('risk-amount-value', riskAmount, '₹');
        this.updateMetricDisplay('max-position-value', maxPositionSize, '₹');
        this.updateMetricDisplay('total-risk-value', totalRiskExposure, '₹');
        this.updateMetricDisplay('max-daily-loss-value', maxDailyLossAmount, '₹');
        this.updateMetricDisplay('capital-required-value', capitalRequired, '₹');
        this.updateMetricDisplay('risk-reward-value', riskRewardRatio, '', 2);

        // Apply color coding
        this.applyColorCoding(totalRiskExposure, maxDailyLossAmount, riskRewardRatio);
    },

    /**
     * Update metric display
     */
    updateMetricDisplay(elementId, value, prefix = '', decimals = 0) {
        const element = document.getElementById(elementId);
        if (element) {
            const formattedValue = this.formatNumber(value, decimals);
            element.textContent = prefix ? `${prefix}${formattedValue}` : formattedValue;
        }
    },

    /**
     * Format number with commas and decimals
     */
    formatNumber(value, decimals = 0) {
        if (isNaN(value)) return '--';
        return value.toLocaleString('en-IN', {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        });
    },

    /**
     * Apply color coding to metrics based on risk levels
     */
    applyColorCoding(totalRisk, maxDailyLoss, riskReward) {
        // Total risk exposure
        const totalRiskElement = document.getElementById('total-risk-value');
        if (totalRiskElement) {
            totalRiskElement.classList.remove('positive', 'negative', 'warning');
            if (totalRisk > maxDailyLoss) {
                totalRiskElement.classList.add('warning');
            } else {
                totalRiskElement.classList.add('positive');
            }
        }

        // Risk/Reward ratio
        const riskRewardElement = document.getElementById('risk-reward-value');
        if (riskRewardElement) {
            riskRewardElement.classList.remove('positive', 'negative', 'warning');
            if (riskReward >= 2) {
                riskRewardElement.classList.add('positive');
            } else if (riskReward >= 1.5) {
                riskRewardElement.classList.add('warning');
            } else {
                riskRewardElement.classList.add('negative');
            }
        }

        // Max daily loss
        const maxDailyLossElement = document.getElementById('max-daily-loss-value');
        if (maxDailyLossElement) {
            maxDailyLossElement.classList.remove('positive', 'negative', 'warning');
            const dailyLossPercent = (maxDailyLoss / this.capital) * 100;
            if (dailyLossPercent > 5) {
                maxDailyLossElement.classList.add('negative');
            } else if (dailyLossPercent > 3) {
                maxDailyLossElement.classList.add('warning');
            } else {
                maxDailyLossElement.classList.add('positive');
            }
        }
    },

    /**
     * Update capital for calculations
     */
    updateCapital(newCapital) {
        if (newCapital && newCapital > 0) {
            this.capital = newCapital;
            this.calculateMetrics();
        }
    },

    /**
     * Get current risk metrics
     */
    getMetrics() {
        const riskPerTrade = parseFloat(document.getElementById('config-risk-per-trade')?.value || 1.0);
        const maxPositions = parseInt(document.getElementById('config-max-positions')?.value || 3);
        const maxDailyLoss = parseFloat(document.getElementById('config-max-daily-loss')?.value || 3.0);
        const stopLoss = parseFloat(document.getElementById('config-stop-loss')?.value || 1.0);
        const takeProfit = parseFloat(document.getElementById('config-take-profit')?.value || 2.0);

        const riskAmount = (this.capital * riskPerTrade) / 100;
        const maxPositionSize = (riskAmount / stopLoss) * 100;
        const totalRiskExposure = riskAmount * maxPositions;
        const maxDailyLossAmount = (this.capital * maxDailyLoss) / 100;
        const riskRewardRatio = takeProfit / stopLoss;

        return {
            riskPerTrade,
            riskAmount,
            maxPositions,
            maxPositionSize,
            totalRiskExposure,
            maxDailyLoss,
            maxDailyLossAmount,
            riskRewardRatio,
            capital: this.capital
        };
    },

    /**
     * Validate risk parameters
     */
    validateRiskParameters() {
        const metrics = this.getMetrics();
        const errors = [];

        // Check if total risk exceeds daily loss limit
        if (metrics.totalRiskExposure > metrics.maxDailyLossAmount) {
            errors.push('Total risk exposure exceeds max daily loss limit');
        }

        // Check if risk/reward ratio is acceptable
        if (metrics.riskRewardRatio < 1) {
            errors.push('Risk/Reward ratio should be at least 1:1');
        }

        // Check if risk per trade is reasonable
        if (metrics.riskPerTrade > 5) {
            errors.push('Risk per trade exceeds 5% (high risk)');
        }

        return {
            valid: errors.length === 0,
            errors
        };
    }
};

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => RiskManagement.init());
} else {
    RiskManagement.init();
}
