/**
 * Dynamic Credentials Form Generator
 * Handles broker-specific credential forms with validation and tooltips
 */

const CredentialsForm = {
    /**
     * Generate dynamic credentials form based on broker
     * @param {string} broker - Broker ID
     * @param {Array} fields - Form field definitions
     * @param {HTMLElement} container - Container element
     */
    generate(broker, fields, container) {
        container.innerHTML = '';
        container.dataset.broker = broker;
        
        fields.forEach(field => {
            if (field.type === 'button') {
                this._createButton(field, container);
            } else {
                this._createInputField(field, container);
            }
        });
        
        // Add validation listeners
        this._attachValidationListeners(container);
    },
    
    /**
     * Create input field with label, validation, and tooltip
     * @param {Object} field - Field definition
     * @param {HTMLElement} container - Container element
     */
    _createInputField(field, container) {
        const group = document.createElement('div');
        group.className = 'form-group';
        group.dataset.fieldName = field.name;
        
        // Create label with tooltip
        const labelWrapper = document.createElement('div');
        labelWrapper.style.display = 'flex';
        labelWrapper.style.alignItems = 'center';
        
        const label = document.createElement('label');
        label.textContent = field.label;
        
        if (field.required) {
            const required = document.createElement('span');
            required.className = 'required';
            required.textContent = '*';
            label.appendChild(required);
        }
        
        labelWrapper.appendChild(label);
        
        // Add tooltip if help text exists
        if (field.help) {
            const tooltip = this._createTooltip(field.help);
            labelWrapper.appendChild(tooltip);
        }
        
        group.appendChild(labelWrapper);
        
        // Create input wrapper for password toggle
        const inputWrapper = document.createElement('div');
        if (field.type === 'password') {
            inputWrapper.className = 'password-toggle-wrapper';
        }
        
        // Create input
        const input = document.createElement('input');
        input.type = field.type;
        input.name = field.name;
        input.className = 'form-control';
        input.placeholder = field.placeholder || '';
        
        if (field.required) {
            input.required = true;
        }
        
        if (field.pattern) {
            input.pattern = field.pattern;
        }
        
        if (field.minlength) {
            input.minLength = field.minlength;
        }
        
        if (field.maxlength) {
            input.maxLength = field.maxlength;
        }
        
        inputWrapper.appendChild(input);
        
        // Add password toggle button
        if (field.type === 'password') {
            const toggleBtn = this._createPasswordToggle(input);
            inputWrapper.appendChild(toggleBtn);
        }
        
        group.appendChild(inputWrapper);
        
        // Add help text
        if (field.help) {
            const helpText = document.createElement('small');
            helpText.className = 'form-help';
            helpText.textContent = field.help;
            group.appendChild(helpText);
        }
        
        // Add error message placeholder
        const errorMsg = document.createElement('small');
        errorMsg.className = 'form-error';
        errorMsg.style.display = 'none';
        group.appendChild(errorMsg);
        
        container.appendChild(group);
    },
    
    /**
     * Create button field (for OAuth)
     * @param {Object} field - Field definition
     * @param {HTMLElement} container - Container element
     */
    _createButton(field, container) {
        const group = document.createElement('div');
        group.className = 'form-group';
        
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'btn btn-primary';
        button.textContent = field.label;
        button.dataset.action = field.action;
        
        if (field.action === 'oauth') {
            button.onclick = () => this._handleOAuth(container.dataset.broker);
        }
        
        group.appendChild(button);
        
        // Add help text
        if (field.help) {
            const helpText = document.createElement('small');
            helpText.className = 'form-help';
            helpText.style.display = 'block';
            helpText.style.marginTop = '0.5rem';
            helpText.textContent = field.help;
            group.appendChild(helpText);
        }
        
        container.appendChild(group);
    },
    
    /**
     * Create tooltip element
     * @param {string} text - Tooltip text
     * @returns {HTMLElement} Tooltip wrapper
     */
    _createTooltip(text) {
        const wrapper = document.createElement('span');
        wrapper.className = 'tooltip-wrapper';
        
        const icon = document.createElement('span');
        icon.className = 'tooltip-icon';
        icon.textContent = '?';
        
        const content = document.createElement('span');
        content.className = 'tooltip-content';
        content.textContent = text;
        
        wrapper.appendChild(icon);
        wrapper.appendChild(content);
        
        return wrapper;
    },
    
    /**
     * Create password toggle button
     * @param {HTMLInputElement} input - Password input element
     * @returns {HTMLElement} Toggle button
     */
    _createPasswordToggle(input) {
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'password-toggle-btn';
        button.innerHTML = '👁️';
        button.title = 'Show/Hide password';
        
        button.onclick = () => {
            if (input.type === 'password') {
                input.type = 'text';
                button.innerHTML = '🙈';
            } else {
                input.type = 'password';
                button.innerHTML = '👁️';
            }
        };
        
        return button;
    },
    
    /**
     * Attach validation listeners to form inputs
     * @param {HTMLElement} container - Form container
     */
    _attachValidationListeners(container) {
        const inputs = container.querySelectorAll('input.form-control');
        
        inputs.forEach(input => {
            // Validate on blur
            input.addEventListener('blur', () => {
                this._validateField(input);
            });
            
            // Clear error on input
            input.addEventListener('input', () => {
                const group = input.closest('.form-group');
                const errorMsg = group.querySelector('.form-error');
                if (errorMsg) {
                    errorMsg.style.display = 'none';
                    input.classList.remove('invalid');
                }
            });
        });
    },
    
    /**
     * Validate a single field
     * @param {HTMLInputElement} input - Input element
     * @returns {boolean} True if valid
     */
    _validateField(input) {
        const group = input.closest('.form-group');
        const errorMsg = group.querySelector('.form-error');
        const value = input.value.trim();
        
        // Clear previous validation
        input.classList.remove('invalid', 'valid');
        errorMsg.style.display = 'none';
        
        // Required validation
        if (input.required && !value) {
            this._showError(input, errorMsg, 'This field is required');
            return false;
        }
        
        // Pattern validation
        if (input.pattern && value && !new RegExp(input.pattern).test(value)) {
            this._showError(input, errorMsg, 'Invalid format');
            return false;
        }
        
        // Min length validation
        if (input.minLength && input.minLength > 0 && value.length < input.minLength) {
            this._showError(input, errorMsg, `Minimum ${input.minLength} characters required`);
            return false;
        }
        
        // Max length validation
        if (input.maxLength && input.maxLength > 0 && value.length > input.maxLength) {
            this._showError(input, errorMsg, `Maximum ${input.maxLength} characters allowed`);
            return false;
        }
        
        // Field-specific validation
        const fieldName = input.name;
        
        if (fieldName === 'api_key' && value) {
            if (value.length < 10) {
                this._showError(input, errorMsg, 'API Key seems too short');
                return false;
            }
        }
        
        if (fieldName === 'totp' && value) {
            if (!/^\d{6}$/.test(value)) {
                this._showError(input, errorMsg, 'TOTP must be 6 digits');
                return false;
            }
        }
        
        if (fieldName === 'redirect_uri' && value) {
            try {
                new URL(value);
            } catch (e) {
                this._showError(input, errorMsg, 'Invalid URL format');
                return false;
            }
        }
        
        // Mark as valid if value exists
        if (value) {
            input.classList.add('valid');
        }
        
        return true;
    },
    
    /**
     * Show validation error
     * @param {HTMLInputElement} input - Input element
     * @param {HTMLElement} errorMsg - Error message element
     * @param {string} message - Error message
     */
    _showError(input, errorMsg, message) {
        input.classList.add('invalid');
        errorMsg.textContent = message;
        errorMsg.style.display = 'block';
    },
    
    /**
     * Validate entire form
     * @param {HTMLElement} container - Form container
     * @returns {boolean} True if all fields are valid
     */
    validateForm(container) {
        const inputs = container.querySelectorAll('input.form-control');
        let isValid = true;
        
        inputs.forEach(input => {
            if (!this._validateField(input)) {
                isValid = false;
            }
        });
        
        return isValid;
    },
    
    /**
     * Get form data
     * @param {HTMLElement} container - Form container
     * @returns {Object} Form data
     */
    getFormData(container) {
        const data = {};
        const inputs = container.querySelectorAll('input.form-control');
        
        inputs.forEach(input => {
            data[input.name] = input.value.trim();
        });
        
        return data;
    },
    
    /**
     * Clear form
     * @param {HTMLElement} container - Form container
     */
    clear(container) {
        container.innerHTML = '';
        delete container.dataset.broker;
    },
    
    /**
     * Handle OAuth flow
     * @param {string} broker - Broker ID
     */
    async _handleOAuth(broker) {
        if (broker === 'kite') {
            // Get API key and secret from form
            const container = document.getElementById('credentials-form');
            const apiKeyInput = container.querySelector('input[name="api_key"]');
            const apiSecretInput = container.querySelector('input[name="api_secret"]');
            
            if (!apiKeyInput || !apiSecretInput) {
                notifications.error('Please enter API Key and Secret first');
                return;
            }
            
            const apiKey = apiKeyInput.value.trim();
            const apiSecret = apiSecretInput.value.trim();
            
            if (!apiKey || !apiSecret) {
                notifications.error('Please enter API Key and Secret first');
                return;
            }
            
            // Validate API key and secret
            if (apiKey.length < 10) {
                notifications.error('API Key seems invalid');
                return;
            }
            
            if (apiSecret.length < 10) {
                notifications.error('API Secret seems invalid');
                return;
            }
            
            try {
                // Show loading state
                notifications.info('Redirecting to Kite authentication...');
                
                // Initiate OAuth flow
                const response = await api.initiateOAuth(broker, apiKey, apiSecret);
                
                if (response.success && response.oauth_url) {
                    // Directly redirect to Kite authentication page
                    window.location.href = response.oauth_url;
                } else {
                    notifications.error('Failed to initiate OAuth: ' + (response.error || 'Unknown error'));
                }
            } catch (error) {
                notifications.error('OAuth initiation failed: ' + error.message);
            }
        } else {
            notifications.info(`OAuth flow for ${broker} not yet implemented`);
        }
    },
    
    /**
     * Handle OAuth callback message from popup
     * @param {MessageEvent} event - Message event
     */
    async _handleOAuthCallback(event) {
        // Verify origin (in production, check against expected origin)
        // For now, we'll accept messages from same origin
        
        const data = event.data;
        
        if (data.type === 'oauth_success') {
            notifications.success('Authentication successful!');
            
            // Show token expiry info
            if (data.token_expiry) {
                notifications.info(`Token expires: ${data.token_expiry}`);
            }
            
            // Reload broker status
            if (typeof updateBrokerStatus === 'function') {
                await updateBrokerStatus();
            }
            
            // Reload brokers to update UI
            if (typeof loadBrokers === 'function') {
                await loadBrokers();
            }
            
            // Hide credentials section
            const credentialsSection = document.getElementById('credentials-section');
            if (credentialsSection) {
                credentialsSection.style.display = 'none';
            }
            
            // Show connection status
            const connectionStatus = document.getElementById('connection-status');
            if (connectionStatus) {
                connectionStatus.style.display = 'block';
            }
            
            // Show change broker section
            const changeBrokerSection = document.getElementById('change-broker-section');
            if (changeBrokerSection) {
                changeBrokerSection.style.display = 'block';
            }
            
        } else if (data.type === 'oauth_error') {
            notifications.error('Authentication failed: ' + (data.error || 'Unknown error'));
        }
    },
    
    /**
     * Show/hide fields based on conditions
     * @param {HTMLElement} container - Form container
     * @param {string} fieldName - Field name to show/hide
     * @param {boolean} show - True to show, false to hide
     */
    toggleField(container, fieldName, show) {
        const group = container.querySelector(`[data-field-name="${fieldName}"]`);
        if (group) {
            group.style.display = show ? 'block' : 'none';
        }
    }
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CredentialsForm;
}
