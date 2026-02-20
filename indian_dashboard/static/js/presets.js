/**
 * Configuration Presets Module
 * Handles loading and applying preset configurations
 */

const Presets = {
    presets: [],
    
    /**
     * Initialize presets module
     */
    async init() {
        await this.loadPresets();
        this.populatePresetSelector();
        this.setupEventHandlers();
    },
    
    /**
     * Load presets from API
     */
    async loadPresets() {
        try {
            const response = await api.getPresets();
            if (response.success) {
                this.presets = response.presets;
                console.log('Loaded presets:', this.presets);
            } else {
                console.error('Failed to load presets:', response.error);
                showNotification('Failed to load presets', 'error');
            }
        } catch (error) {
            console.error('Error loading presets:', error);
            showNotification('Error loading presets: ' + error.message, 'error');
        }
    },
    
    /**
     * Populate preset selector dropdown
     */
    populatePresetSelector() {
        const selector = document.getElementById('preset-selector');
        if (!selector) return;
        
        // Clear existing options except the first one
        selector.innerHTML = '<option value="">-- Select Preset --</option>';
        
        // Add preset options
        this.presets.forEach(preset => {
            const option = document.createElement('option');
            option.value = preset.id;
            option.textContent = preset.name;
            option.title = preset.description;
            selector.appendChild(option);
        });
    },
    
    /**
     * Setup event handlers
     */
    setupEventHandlers() {
        const selector = document.getElementById('preset-selector');
        if (selector) {
            selector.addEventListener('change', (e) => {
                if (e.target.value) {
                    this.applyPreset(e.target.value);
                }
            });
        }
    },
    
    /**
     * Apply preset configuration
     */
    async applyPreset(presetId) {
        const preset = this.presets.find(p => p.id === presetId);
        if (!preset) {
            showNotification('Preset not found', 'error');
            return;
        }
        
        try {
            // Show confirmation
            if (!confirm(`Load preset "${preset.name}"?\n\n${preset.description}\n\nThis will replace your current configuration.`)) {
                // Reset selector
                document.getElementById('preset-selector').value = '';
                return;
            }
            
            // Apply preset configuration
            this.loadPresetConfig(preset.config);
            
            showNotification(`Preset "${preset.name}" loaded successfully`, 'success');
            
            // Reset selector
            document.getElementById('preset-selector').value = '';
            
        } catch (error) {
            console.error('Error applying preset:', error);
            showNotification('Error applying preset: ' + error.message, 'error');
        }
    },
    
    /**
     * Load preset configuration into form
     */
    loadPresetConfig(config) {
        // Update form fields
        const form = document.getElementById('config-form');
        if (!form) return;
        
        // Basic settings
        if (config.timeframe) {
            const timeframeField = form.querySelector('[name="timeframe"]');
            if (timeframeField) timeframeField.value = config.timeframe;
        }
        
        if (config.strategy) {
            const strategyField = form.querySelector('[name="strategy"]');
            if (strategyField) strategyField.value = config.strategy;
        }
        
        if (config.trading_hours) {
            const startField = form.querySelector('[name="trading_start"]');
            const endField = form.querySelector('[name="trading_end"]');
            if (startField && config.trading_hours.start) {
                startField.value = config.trading_hours.start;
            }
            if (endField && config.trading_hours.end) {
                endField.value = config.trading_hours.end;
            }
        }
        
        // Strategy parameters
        if (config.indicator_period) {
            const field = form.querySelector('[name="indicator_period"]');
            if (field) field.value = config.indicator_period;
        }
        
        if (config.position_sizing) {
            const field = form.querySelector('[name="position_sizing"]');
            if (field) field.value = config.position_sizing;
        }
        
        if (config.base_position_size) {
            const field = form.querySelector('[name="base_position_size"]');
            if (field) field.value = config.base_position_size;
        }
        
        if (config.take_profit) {
            const field = form.querySelector('[name="take_profit"]');
            if (field) field.value = config.take_profit;
        }
        
        if (config.stop_loss) {
            const field = form.querySelector('[name="stop_loss"]');
            if (field) field.value = config.stop_loss;
        }
        
        // Risk management
        if (config.risk_per_trade !== undefined) {
            const field = form.querySelector('[name="risk_per_trade"]');
            const slider = document.getElementById('config-risk-per-trade-slider');
            if (field) field.value = config.risk_per_trade;
            if (slider) slider.value = config.risk_per_trade;
        }
        
        if (config.max_positions) {
            const field = form.querySelector('[name="max_positions"]');
            if (field) field.value = config.max_positions;
        }
        
        if (config.max_daily_loss !== undefined) {
            const field = form.querySelector('[name="max_daily_loss"]');
            const slider = document.getElementById('config-max-daily-loss-slider');
            if (field) field.value = config.max_daily_loss;
            if (slider) slider.value = config.max_daily_loss;
        }
        
        // Advanced settings
        if (config.paper_trading !== undefined) {
            const field = form.querySelector('[name="paper_trading"]');
            if (field) field.checked = config.paper_trading;
        }
        
        if (config.log_level) {
            const field = form.querySelector('[name="log_level"]');
            if (field) field.value = config.log_level;
        }
        
        if (config.data_refresh_interval) {
            const field = form.querySelector('[name="data_refresh_interval"]');
            if (field) field.value = config.data_refresh_interval;
        }
        
        if (config.enable_notifications !== undefined) {
            const field = form.querySelector('[name="enable_notifications"]');
            if (field) field.checked = config.enable_notifications;
        }
        
        // Update instruments if provided
        if (config.instruments && Array.isArray(config.instruments)) {
            // Remove duplicates based on token or symbol+exchange
            const seen = new Set();
            const uniqueInstruments = config.instruments.filter(inst => {
                const key = inst.token || `${inst.symbol}_${inst.exchange}`;
                if (seen.has(key)) {
                    return false;
                }
                seen.add(key);
                return true;
            });
            
            appState.set('instruments.selected', uniqueInstruments);
            if (typeof ConfigForm !== 'undefined' && ConfigForm.refreshSelectedInstruments) {
                ConfigForm.refreshSelectedInstruments();
            }
        }
        
        // Recalculate risk metrics
        if (typeof RiskManagement !== 'undefined' && RiskManagement.calculateMetrics) {
            RiskManagement.calculateMetrics();
        }
        
        // Trigger validation
        if (typeof Validation !== 'undefined' && Validation.validateAll) {
            Validation.validateAll();
        }
        
        // Mark config as dirty
        appState.set('config.isDirty', true);
    },
    
    /**
     * Get preset by ID
     */
    getPreset(presetId) {
        return this.presets.find(p => p.id === presetId);
    },
    
    /**
     * Get all presets
     */
    getAllPresets() {
        return this.presets;
    }
};

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => Presets.init());
} else {
    Presets.init();
}
