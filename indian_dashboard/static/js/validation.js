/**
 * Real-time Validation Module
 * Handles form validation with inline error display and validation summary
 */

const Validation = {
    // Validation rules for each field
    rules: {
        // Basic Settings
        timeframe: {
            required: true,
            message: 'Timeframe is required'
        },
        strategy: {
            required: true,
            message: 'Strategy is required'
        },
        trading_start: {
            required: true,
            custom: (value, formData) => {
                if (!value) return 'Trading start time is required';
                const start = Validation.parseTime(value);
                const marketOpen = Validation.parseTime('09:15');
                const marketClose = Validation.parseTime('15:30');
                if (start < marketOpen || start > marketClose) {
                    return 'Trading start must be between 09:15 and 15:30';
                }
                return null;
            }
        },
        trading_end: {
            required: true,
            custom: (value, formData) => {
                if (!value) return 'Trading end time is required';
                const end = Validation.parseTime(value);
                const start = Validation.parseTime(formData.trading_start);
                const marketClose = Validation.parseTime('15:30');
                if (end > marketClose) {
                    return 'Trading end must be before 15:30';
                }
                if (end <= start) {
                    return 'Trading end must be after trading start';
                }
                return null;
            }
        },
        
        // Strategy Parameters
        indicator_period: {
            required: true,
            min: 5,
            max: 200,
            message: 'Indicator period must be between 5 and 200'
        },
        position_sizing: {
            required: true,
            message: 'Position sizing method is required'
        },
        base_position_size: {
            required: true,
            min: 1000,
            message: 'Base position size must be at least ₹1,000'
        },
        take_profit: {
            required: true,
            min: 0.5,
            max: 20,
            message: 'Take profit must be between 0.5% and 20%'
        },
        stop_loss: {
            required: true,
            min: 0.5,
            max: 10,
            message: 'Stop loss must be between 0.5% and 10%',
            custom: (value, formData) => {
                const tp = parseFloat(formData.take_profit);
                const sl = parseFloat(value);
                if (sl >= tp) {
                    return 'Stop loss should be less than take profit for positive risk/reward';
                }
                return null;
            }
        },
        
        // Risk Management
        risk_per_trade: {
            required: true,
            min: 0.1,
            max: 10,
            message: 'Risk per trade must be between 0.1% and 10%',
            warning: (value) => {
                const risk = parseFloat(value);
                if (risk > 5) {
                    return 'Risk per trade above 5% is considered high';
                }
                if (risk > 2) {
                    return 'Risk per trade above 2% is considered moderate';
                }
                return null;
            }
        },
        max_positions: {
            required: true,
            min: 1,
            max: 20,
            message: 'Max positions must be between 1 and 20',
            warning: (value) => {
                const positions = parseInt(value);
                if (positions > 10) {
                    return 'More than 10 positions may be difficult to manage';
                }
                return null;
            }
        },
        max_daily_loss: {
            required: true,
            min: 0.5,
            max: 20,
            message: 'Max daily loss must be between 0.5% and 20%',
            warning: (value) => {
                const loss = parseFloat(value);
                if (loss > 10) {
                    return 'Max daily loss above 10% is considered high';
                }
                return null;
            }
        },
        
        // Advanced Settings
        data_refresh_interval: {
            required: true,
            min: 1,
            max: 300,
            message: 'Data refresh interval must be between 1 and 300 seconds'
        }
    },

    // Validation state
    errors: {},
    warnings: {},
    isValid: true,

    /**
     * Initialize validation
     */
    init() {
        this.setupFieldValidation();
        this.createValidationSummary();
        this.updateSaveButtonState();
    },

    /**
     * Setup validation for all form fields
     */
    setupFieldValidation() {
        const form = document.getElementById('config-form');
        if (!form) return;

        // Get all input fields
        const fields = form.querySelectorAll('input[type="number"], input[type="time"], select');
        
        fields.forEach(field => {
            // Validate on change
            field.addEventListener('change', () => {
                this.validateField(field);
                this.updateValidationSummary();
                this.updateSaveButtonState();
            });

            // Validate on blur
            field.addEventListener('blur', () => {
                this.validateField(field);
                this.updateValidationSummary();
                this.updateSaveButtonState();
            });

            // Clear error on input (for better UX)
            field.addEventListener('input', () => {
                this.clearFieldError(field);
            });
        });

        // Sync slider and number inputs
        this.setupSliderSync();
    },

    /**
     * Setup slider and number input synchronization
     */
    setupSliderSync() {
        const sliderPairs = [
            { slider: 'config-risk-per-trade-slider', input: 'config-risk-per-trade' },
            { slider: 'config-max-daily-loss-slider', input: 'config-max-daily-loss' }
        ];

        sliderPairs.forEach(pair => {
            const slider = document.getElementById(pair.slider);
            const input = document.getElementById(pair.input);

            if (slider && input) {
                slider.addEventListener('input', () => {
                    input.value = slider.value;
                    this.validateField(input);
                    this.updateValidationSummary();
                    this.updateSaveButtonState();
                });

                input.addEventListener('input', () => {
                    slider.value = input.value;
                });
            }
        });
    },

    /**
     * Validate a single field
     */
    validateField(field) {
        const fieldName = field.name || field.id.replace('config-', '');
        const value = field.value;
        const rule = this.rules[fieldName];

        if (!rule) {
            // No validation rule for this field
            return true;
        }

        // Clear previous errors and warnings
        delete this.errors[fieldName];
        delete this.warnings[fieldName];
        this.removeFieldError(field);
        this.removeFieldWarning(field);

        // Get all form data for cross-field validation
        const formData = this.getFormData();

        // Required validation
        if (rule.required && !value) {
            this.errors[fieldName] = rule.message || `${fieldName} is required`;
            this.showFieldError(field, this.errors[fieldName]);
            return false;
        }

        // Min/Max validation for numbers
        if (field.type === 'number' && value) {
            const numValue = parseFloat(value);
            
            if (rule.min !== undefined && numValue < rule.min) {
                this.errors[fieldName] = rule.message || `Value must be at least ${rule.min}`;
                this.showFieldError(field, this.errors[fieldName]);
                return false;
            }
            
            if (rule.max !== undefined && numValue > rule.max) {
                this.errors[fieldName] = rule.message || `Value must be at most ${rule.max}`;
                this.showFieldError(field, this.errors[fieldName]);
                return false;
            }
        }

        // Custom validation
        if (rule.custom && value) {
            const customError = rule.custom(value, formData);
            if (customError) {
                this.errors[fieldName] = customError;
                this.showFieldError(field, customError);
                return false;
            }
        }

        // Warning validation (doesn't prevent saving)
        if (rule.warning && value) {
            const warningMessage = rule.warning(value);
            if (warningMessage) {
                this.warnings[fieldName] = warningMessage;
                this.showFieldWarning(field, warningMessage);
            }
        }

        // Field is valid
        this.showFieldValid(field);
        return true;
    },

    /**
     * Validate all fields
     */
    validateAll() {
        const form = document.getElementById('config-form');
        if (!form) return false;

        this.errors = {};
        this.warnings = {};

        const fields = form.querySelectorAll('input[type="number"], input[type="time"], select');
        let allValid = true;

        fields.forEach(field => {
            if (!this.validateField(field)) {
                allValid = false;
            }
        });

        // Validate instruments selection
        const selectedInstruments = appState.get('instruments.selected') || [];
        if (selectedInstruments.length === 0) {
            this.errors['instruments'] = 'At least one instrument must be selected';
            allValid = false;
        }

        this.isValid = allValid;
        this.updateValidationSummary();
        this.updateSaveButtonState();

        return allValid;
    },

    /**
     * Show field error
     */
    showFieldError(field, message) {
        field.classList.remove('valid');
        field.classList.add('invalid');

        // Remove existing error message
        this.removeFieldError(field);

        // Add error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'form-error';
        errorDiv.textContent = message;
        errorDiv.setAttribute('data-error-for', field.id || field.name);
        
        field.parentNode.appendChild(errorDiv);
    },

    /**
     * Show field warning
     */
    showFieldWarning(field, message) {
        field.classList.remove('invalid');
        field.classList.add('valid');

        // Remove existing warning
        this.removeFieldWarning(field);

        // Add warning message
        const warningDiv = document.createElement('div');
        warningDiv.className = 'form-warning';
        warningDiv.textContent = '⚠️ ' + message;
        warningDiv.setAttribute('data-warning-for', field.id || field.name);
        
        field.parentNode.appendChild(warningDiv);
    },

    /**
     * Show field as valid
     */
    showFieldValid(field) {
        field.classList.remove('invalid');
        field.classList.add('valid');
        this.removeFieldError(field);
        this.removeFieldWarning(field);
    },

    /**
     * Clear field error styling
     */
    clearFieldError(field) {
        field.classList.remove('invalid', 'valid');
    },

    /**
     * Remove field error message
     */
    removeFieldError(field) {
        const fieldId = field.id || field.name;
        const existingError = field.parentNode.querySelector(`[data-error-for="${fieldId}"]`);
        if (existingError) {
            existingError.remove();
        }
    },

    /**
     * Remove field warning message
     */
    removeFieldWarning(field) {
        const fieldId = field.id || field.name;
        const existingWarning = field.parentNode.querySelector(`[data-warning-for="${fieldId}"]`);
        if (existingWarning) {
            existingWarning.remove();
        }
    },

    /**
     * Create validation summary container
     */
    createValidationSummary() {
        const form = document.getElementById('config-form');
        if (!form) return;

        // Check if summary already exists
        let summary = document.getElementById('validation-summary');
        if (summary) return;

        // Create summary container
        summary = document.createElement('div');
        summary.id = 'validation-summary';
        summary.className = 'validation-summary';
        summary.style.display = 'none';

        // Insert at the top of the form
        form.insertBefore(summary, form.firstChild);
    },

    /**
     * Update validation summary
     */
    updateValidationSummary() {
        const summary = document.getElementById('validation-summary');
        if (!summary) return;

        const errorCount = Object.keys(this.errors).length;
        const warningCount = Object.keys(this.warnings).length;

        if (errorCount === 0 && warningCount === 0) {
            summary.style.display = 'none';
            return;
        }

        let html = '';

        // Show errors
        if (errorCount > 0) {
            html += '<div class="validation-summary-errors">';
            html += `<h4 class="validation-summary-title error">❌ ${errorCount} Error${errorCount > 1 ? 's' : ''} Found</h4>`;
            html += '<ul class="validation-summary-list">';
            for (const [field, message] of Object.entries(this.errors)) {
                html += `<li class="validation-error-item">${this.getFieldLabel(field)}: ${message}</li>`;
            }
            html += '</ul>';
            html += '</div>';
        }

        // Show warnings
        if (warningCount > 0) {
            html += '<div class="validation-summary-warnings">';
            html += `<h4 class="validation-summary-title warning">⚠️ ${warningCount} Warning${warningCount > 1 ? 's' : ''}</h4>`;
            html += '<ul class="validation-summary-list">';
            for (const [field, message] of Object.entries(this.warnings)) {
                html += `<li class="validation-warning-item">${this.getFieldLabel(field)}: ${message}</li>`;
            }
            html += '</ul>';
            html += '</div>';
        }

        summary.innerHTML = html;
        summary.style.display = 'block';

        // Scroll to summary if there are errors
        if (errorCount > 0) {
            summary.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
    },

    /**
     * Update save button state
     */
    updateSaveButtonState() {
        const saveBtn = document.getElementById('save-config-btn');
        if (!saveBtn) return;

        const hasErrors = Object.keys(this.errors).length > 0;

        if (hasErrors) {
            saveBtn.disabled = true;
            saveBtn.classList.add('disabled');
            saveBtn.title = 'Please fix validation errors before saving';
        } else {
            saveBtn.disabled = false;
            saveBtn.classList.remove('disabled');
            saveBtn.title = 'Save configuration';
        }
    },

    /**
     * Get field label for display
     */
    getFieldLabel(fieldName) {
        const labels = {
            timeframe: 'Timeframe',
            strategy: 'Strategy',
            trading_start: 'Trading Start Time',
            trading_end: 'Trading End Time',
            indicator_period: 'Indicator Period',
            position_sizing: 'Position Sizing',
            base_position_size: 'Base Position Size',
            take_profit: 'Take Profit',
            stop_loss: 'Stop Loss',
            risk_per_trade: 'Risk Per Trade',
            max_positions: 'Max Positions',
            max_daily_loss: 'Max Daily Loss',
            data_refresh_interval: 'Data Refresh Interval',
            instruments: 'Instruments'
        };

        return labels[fieldName] || fieldName;
    },

    /**
     * Get all form data
     */
    getFormData() {
        const form = document.getElementById('config-form');
        if (!form) return {};

        const formData = new FormData(form);
        const data = {};

        for (let [key, value] of formData.entries()) {
            const field = form.querySelector(`[name="${key}"]`);
            if (field && field.type === 'checkbox') {
                data[key] = field.checked;
            } else if (field && field.type === 'number') {
                data[key] = parseFloat(value);
            } else {
                data[key] = value;
            }
        }

        return data;
    },

    /**
     * Parse time string to minutes
     */
    parseTime(timeStr) {
        if (!timeStr) return 0;
        const [hours, minutes] = timeStr.split(':').map(Number);
        return hours * 60 + minutes;
    },

    /**
     * Validate before save
     */
    validateBeforeSave() {
        return this.validateAll();
    }
};

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => Validation.init());
} else {
    Validation.init();
}
