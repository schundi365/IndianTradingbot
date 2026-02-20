/**
 * Configuration Form Module
 * Handles configuration form UI interactions including tab switching
 */

const ConfigForm = {
    /**
     * Initialize configuration form
     */
    init() {
        this.setupConfigTabs();
        this.setupFormHandlers();
        this.loadSelectedInstruments();
    },

    /**
     * Setup configuration sub-tabs
     */
    setupConfigTabs() {
        const tabButtons = document.querySelectorAll('.config-tab-button');
        const sections = document.querySelectorAll('.config-section');

        tabButtons.forEach(button => {
            button.addEventListener('click', () => {
                const targetTab = button.getAttribute('data-config-tab');
                
                // Remove active class from all buttons and sections
                tabButtons.forEach(btn => btn.classList.remove('active'));
                sections.forEach(section => section.classList.remove('active'));
                
                // Add active class to clicked button and corresponding section
                button.classList.add('active');
                const targetSection = document.querySelector(`[data-config-section="${targetTab}"]`);
                if (targetSection) {
                    targetSection.classList.add('active');
                }
            });
        });
    },

    /**
     * Setup form handlers
     */
    setupFormHandlers() {
        // Save configuration button
        const saveBtn = document.getElementById('save-config-btn');
        if (saveBtn) {
            saveBtn.addEventListener('click', () => this.saveConfiguration());
        }

        // Load configuration button
        const loadBtn = document.getElementById('load-config-btn');
        if (loadBtn) {
            loadBtn.addEventListener('click', () => this.loadConfiguration());
        }

        // Note: Preset selector is handled by presets.js module

        // Real-time validation
        this.setupValidation();
    },

    /**
     * Setup real-time validation
     */
    setupValidation() {
        // Validation is now handled by the Validation module
        // This method is kept for backward compatibility
        if (typeof Validation !== 'undefined') {
            // Validation module will handle all validation
            console.log('Validation module initialized');
        }
    },

    /**
     * Load selected instruments from state
     */
    loadSelectedInstruments() {
        const container = document.getElementById('config-selected-instruments');
        if (!container) return;

        let selectedInstruments = appState.get('instruments.selected') || [];
        
        // Remove duplicates based on token or symbol+exchange
        const seen = new Set();
        selectedInstruments = selectedInstruments.filter(inst => {
            const key = inst.token || `${inst.symbol}_${inst.exchange}`;
            if (seen.has(key)) {
                return false;
            }
            seen.add(key);
            return true;
        });
        
        // Update state with deduplicated list
        if (selectedInstruments.length !== (appState.get('instruments.selected') || []).length) {
            appState.set('instruments.selected', selectedInstruments);
        }
        
        if (selectedInstruments.length === 0) {
            container.innerHTML = '<p class="text-muted">No instruments selected. Go to Instruments tab to select.</p>';
            return;
        }

        // Display selected instruments as chips
        container.innerHTML = selectedInstruments.map(inst => `
            <div class="instrument-chip">
                <span class="symbol">${inst.symbol}</span>
                <span class="exchange">${inst.exchange}</span>
            </div>
        `).join('');
    },

    /**
     * Get form data
     */
    getFormData() {
        const form = document.getElementById('config-form');
        if (!form) return null;

        const formData = new FormData(form);
        const data = {};

        // Convert FormData to object
        for (let [key, value] of formData.entries()) {
            // Handle checkboxes
            const field = form.querySelector(`[name="${key}"]`);
            if (field && field.type === 'checkbox') {
                data[key] = field.checked;
            } else if (field && field.type === 'number') {
                data[key] = parseFloat(value);
            } else {
                data[key] = value;
            }
        }

        // Add broker from app state (required field)
        const brokerType = appState.get('broker.type');
        if (brokerType) {
            data.broker = brokerType;
        } else {
            // Default to 'paper' if no broker is connected
            data.broker = 'paper';
        }

        // Add selected instruments
        data.instruments = appState.get('instruments.selected') || [];

        // Add strategy parameters
        if (typeof StrategyParameters !== 'undefined') {
            data.strategy_parameters = StrategyParameters.getParameters();
        }

        // Add risk metrics
        if (typeof RiskManagement !== 'undefined') {
            data.risk_metrics = RiskManagement.getMetrics();
        }

        return data;
    },

    /**
     * Set form data
     */
    setFormData(data) {
        const form = document.getElementById('config-form');
        if (!form || !data) return;

        // Set each field value
        Object.keys(data).forEach(key => {
            const field = form.querySelector(`[name="${key}"]`);
            if (field) {
                if (field.type === 'checkbox') {
                    field.checked = data[key];
                } else {
                    field.value = data[key];
                }
            }
        });

        // Update selected instruments display
        if (data.instruments) {
            // Remove duplicates based on token or symbol+exchange
            const seen = new Set();
            const uniqueInstruments = data.instruments.filter(inst => {
                const key = inst.token || `${inst.symbol}_${inst.exchange}`;
                if (seen.has(key)) {
                    return false;
                }
                seen.add(key);
                return true;
            });
            
            appState.set('instruments.selected', uniqueInstruments);
            this.loadSelectedInstruments();
        }

        // Update strategy parameters
        if (data.strategy_parameters && typeof StrategyParameters !== 'undefined') {
            StrategyParameters.setParameters(data.strategy_parameters);
        }

        // Recalculate risk metrics
        if (typeof RiskManagement !== 'undefined') {
            RiskManagement.calculateMetrics();
        }
    },

    /**
     * Save configuration
     */
    async saveConfiguration() {
        // Validate using the Validation module
        if (typeof Validation !== 'undefined') {
            if (!Validation.validateBeforeSave()) {
                showNotification('Please fix validation errors before saving', 'error');
                return;
            }
        }

        const data = this.getFormData();
        if (!data) {
            showNotification('Failed to get form data', 'error');
            return;
        }

        // Log the data being sent for debugging
        console.log('Saving configuration:', data);

        try {
            const response = await api.saveConfig(data);
            if (response.success) {
                showNotification('Configuration saved successfully', 'success');
                appState.setConfig(data);
                appState.set('config.isDirty', false);
            } else {
                console.error('Save failed:', response);
                const errorMsg = response.error || 'Unknown error';
                const details = response.details ? '\n' + response.details.join('\n') : '';
                showNotification('Failed to save configuration: ' + errorMsg + details, 'error');
            }
        } catch (error) {
            console.error('Save configuration error:', error);
            // Extract error details from the error object
            let errorMsg = 'Unknown error';
            if (error.response && error.response.data) {
                const errorData = error.response.data;
                console.error('Server error details:', errorData);
                errorMsg = errorData.error || errorMsg;
                if (errorData.details && Array.isArray(errorData.details)) {
                    errorMsg += ':\n• ' + errorData.details.join('\n• ');
                }
            } else if (error.message) {
                errorMsg = error.message;
            }
            showNotification('Error saving configuration: ' + errorMsg, 'error');
        }
    },

    /**
     * Load configuration
     */
    async loadConfiguration() {
        try {
            // Show dialog to select configuration
            // For now, load the current configuration
            const response = await api.getConfig('_current');
            if (response) {
                this.setFormData(response);
                showNotification('Configuration loaded successfully', 'success');
            } else {
                showNotification('No configuration found', 'info');
            }
        } catch (error) {
            console.error('Load configuration error:', error);
            showNotification('Error loading configuration: ' + error.message, 'error');
        }
    },

    /**
     * Set form data from configuration object
     */    /**
     * Refresh selected instruments display
     */
    refreshSelectedInstruments() {
        this.loadSelectedInstruments();
    }
};

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => ConfigForm.init());
} else {
    ConfigForm.init();
}
