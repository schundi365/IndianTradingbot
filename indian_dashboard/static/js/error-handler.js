/**
 * Frontend Error Handler for Indian Market Trading Dashboard
 * Provides comprehensive error display and graceful degradation
 */

class ErrorHandler {
    constructor() {
        this.errorLog = [];
        this.maxLogSize = 100;
        this.retryAttempts = new Map();
        this.maxRetries = 3;
        this.retryDelay = 1000; // 1 second
        
        // Initialize error display container
        this.initErrorContainer();
        
        // Set up global error listeners
        this.setupGlobalErrorHandlers();
    }
    
    /**
     * Initialize error display container
     */
    initErrorContainer() {
        if (!document.getElementById('error-container')) {
            const container = document.createElement('div');
            container.id = 'error-container';
            container.className = 'error-container';
            document.body.appendChild(container);
        }
    }
    
    /**
     * Set up global error handlers
     */
    setupGlobalErrorHandlers() {
        // Handle unhandled promise rejections
        window.addEventListener('unhandledrejection', (event) => {
            this.handleAPIError({
                message: event.reason?.message || 'Unhandled promise rejection',
                type: 'unknown_error',
                details: { reason: event.reason }
            });
            event.preventDefault();
        });
        
        // Handle global JavaScript errors
        window.addEventListener('error', (event) => {
            this.handleAPIError({
                message: event.message || 'JavaScript error',
                type: 'unknown_error',
                details: {
                    filename: event.filename,
                    lineno: event.lineno,
                    colno: event.colno
                }
            });
        });
    }
    
    /**
     * Handle API errors
     */
    handleAPIError(error, context = {}) {
        const errorInfo = this.parseAPIError(error);
        
        // Log error
        this.logError(errorInfo, context);
        
        // Display error to user
        this.displayError(errorInfo);
        
        // Handle specific error types
        this.handleSpecificError(errorInfo, context);
        
        return errorInfo;
    }
    
    /**
     * Parse API error response
     */
    parseAPIError(error) {
        // Default error structure
        const errorInfo = {
            message: 'An unexpected error occurred',
            type: 'unknown_error',
            status: 500,
            details: {},
            timestamp: new Date().toISOString()
        };
        
        // Parse error from different sources
        if (error.response) {
            // HTTP error response
            errorInfo.status = error.response.status;
            errorInfo.message = error.response.data?.error || error.response.statusText;
            errorInfo.type = error.response.data?.error_type || 'server_error';
            errorInfo.details = error.response.data?.details || {};
        } else if (error.error) {
            // API error object
            errorInfo.message = error.error;
            errorInfo.type = error.error_type || 'unknown_error';
            errorInfo.details = error.details || {};
        } else if (error.message) {
            // JavaScript error
            errorInfo.message = error.message;
            errorInfo.type = 'client_error';
        } else if (typeof error === 'string') {
            // String error
            errorInfo.message = error;
        }
        
        return errorInfo;
    }
    
    /**
     * Handle specific error types
     */
    handleSpecificError(errorInfo, context) {
        switch (errorInfo.type) {
            case 'authentication_error':
                this.handleAuthenticationError(errorInfo, context);
                break;
            case 'authorization_error':
                this.handleAuthorizationError(errorInfo, context);
                break;
            case 'broker_error':
                this.handleBrokerError(errorInfo, context);
                break;
            case 'rate_limit_error':
                this.handleRateLimitError(errorInfo, context);
                break;
            case 'timeout_error':
                this.handleTimeoutError(errorInfo, context);
                break;
            case 'network_error':
                this.handleNetworkError(errorInfo, context);
                break;
            case 'validation_error':
                this.handleValidationError(errorInfo, context);
                break;
            default:
                // Generic error handling
                break;
        }
    }
    
    /**
     * Handle authentication errors
     */
    handleAuthenticationError(errorInfo, context) {
        // Clear session
        if (window.appState) {
            appState.setBrokerConnected(false);
        }
        
        // Show reconnect option
        this.showReconnectPrompt();
    }
    
    /**
     * Handle authorization errors
     */
    handleAuthorizationError(errorInfo, context) {
        notifications.error('Access denied. Please check your permissions.');
    }
    
    /**
     * Handle broker errors
     */
    handleBrokerError(errorInfo, context) {
        // Suggest broker reconnection
        this.showBrokerReconnectPrompt();
    }
    
    /**
     * Handle rate limit errors
     */
    handleRateLimitError(errorInfo, context) {
        const retryAfter = errorInfo.details.retry_after || 60;
        notifications.error(`Rate limit exceeded. Please wait ${retryAfter} seconds.`, 5000);
        
        // Disable actions temporarily
        this.disableActionsTemporarily(retryAfter * 1000);
    }
    
    /**
     * Handle timeout errors
     */
    handleTimeoutError(errorInfo, context) {
        // Offer retry option
        if (context.retryable !== false) {
            this.offerRetry(context);
        }
    }
    
    /**
     * Handle network errors
     */
    handleNetworkError(errorInfo, context) {
        // Check if online
        if (!navigator.onLine) {
            this.showOfflineMessage();
        } else {
            // Offer retry
            if (context.retryable !== false) {
                this.offerRetry(context);
            }
        }
    }
    
    /**
     * Handle validation errors
     */
    handleValidationError(errorInfo, context) {
        // Display validation errors inline if possible
        if (context.formId && errorInfo.details.fields) {
            this.displayInlineValidationErrors(context.formId, errorInfo.details.fields);
        }
    }
    
    /**
     * Display error to user
     */
    displayError(errorInfo) {
        const container = document.getElementById('error-container');
        const errorElement = document.createElement('div');
        errorElement.className = `error-message ${this.getErrorClass(errorInfo.type)}`;
        
        errorElement.innerHTML = `
            <div class="error-content">
                <span class="error-icon">${this.getErrorIcon(errorInfo.type)}</span>
                <div class="error-text">
                    <strong>${this.getErrorTitle(errorInfo.type)}</strong>
                    <p>${this.sanitizeHTML(errorInfo.message)}</p>
                </div>
                <button class="error-close" onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
        `;
        
        container.appendChild(errorElement);
        
        // Auto-remove after delay
        setTimeout(() => {
            errorElement.style.opacity = '0';
            setTimeout(() => errorElement.remove(), 300);
        }, 5000);
    }
    
    /**
     * Get error CSS class
     */
    getErrorClass(errorType) {
        const classMap = {
            'validation_error': 'error-warning',
            'authentication_error': 'error-danger',
            'authorization_error': 'error-danger',
            'broker_error': 'error-danger',
            'rate_limit_error': 'error-warning',
            'timeout_error': 'error-warning',
            'network_error': 'error-danger',
            'server_error': 'error-danger'
        };
        return classMap[errorType] || 'error-danger';
    }
    
    /**
     * Get error icon
     */
    getErrorIcon(errorType) {
        const iconMap = {
            'validation_error': '⚠️',
            'authentication_error': '🔒',
            'authorization_error': '🚫',
            'broker_error': '📡',
            'rate_limit_error': '⏱️',
            'timeout_error': '⏰',
            'network_error': '🌐',
            'server_error': '❌'
        };
        return iconMap[errorType] || '❌';
    }
    
    /**
     * Get error title
     */
    getErrorTitle(errorType) {
        const titleMap = {
            'validation_error': 'Validation Error',
            'authentication_error': 'Authentication Required',
            'authorization_error': 'Access Denied',
            'broker_error': 'Broker Error',
            'rate_limit_error': 'Rate Limit Exceeded',
            'timeout_error': 'Request Timeout',
            'network_error': 'Network Error',
            'server_error': 'Server Error'
        };
        return titleMap[errorType] || 'Error';
    }
    
    /**
     * Log error
     */
    logError(errorInfo, context) {
        const logEntry = {
            ...errorInfo,
            context,
            userAgent: navigator.userAgent,
            url: window.location.href
        };
        
        this.errorLog.push(logEntry);
        
        // Limit log size
        if (this.errorLog.length > this.maxLogSize) {
            this.errorLog.shift();
        }
        
        // Console log in development
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            console.error('Error logged:', logEntry);
        }
    }
    
    /**
     * Show reconnect prompt
     */
    showReconnectPrompt() {
        const modal = this.createModal(
            'Session Expired',
            'Your session has expired. Please reconnect to continue.',
            [
                {
                    text: 'Reconnect',
                    class: 'btn-primary',
                    onclick: () => {
                        window.location.reload();
                    }
                }
            ]
        );
        document.body.appendChild(modal);
    }
    
    /**
     * Show broker reconnect prompt
     */
    showBrokerReconnectPrompt() {
        const modal = this.createModal(
            'Broker Connection Lost',
            'Connection to broker was lost. Please reconnect.',
            [
                {
                    text: 'Go to Broker Tab',
                    class: 'btn-primary',
                    onclick: () => {
                        if (window.switchTab) {
                            window.switchTab('broker');
                        }
                        modal.remove();
                    }
                },
                {
                    text: 'Cancel',
                    class: 'btn-secondary',
                    onclick: () => modal.remove()
                }
            ]
        );
        document.body.appendChild(modal);
    }
    
    /**
     * Show offline message
     */
    showOfflineMessage() {
        notifications.error('You are offline. Please check your internet connection.', 10000);
    }
    
    /**
     * Offer retry option
     */
    offerRetry(context) {
        if (!context.retryFunction) return;
        
        const retryKey = context.retryKey || 'default';
        const attempts = this.retryAttempts.get(retryKey) || 0;
        
        if (attempts >= this.maxRetries) {
            notifications.error('Maximum retry attempts reached. Please try again later.');
            this.retryAttempts.delete(retryKey);
            return;
        }
        
        const modal = this.createModal(
            'Request Failed',
            `The request failed. Would you like to retry? (Attempt ${attempts + 1}/${this.maxRetries})`,
            [
                {
                    text: 'Retry',
                    class: 'btn-primary',
                    onclick: () => {
                        this.retryAttempts.set(retryKey, attempts + 1);
                        setTimeout(() => {
                            context.retryFunction();
                        }, this.retryDelay);
                        modal.remove();
                    }
                },
                {
                    text: 'Cancel',
                    class: 'btn-secondary',
                    onclick: () => {
                        this.retryAttempts.delete(retryKey);
                        modal.remove();
                    }
                }
            ]
        );
        document.body.appendChild(modal);
    }
    
    /**
     * Disable actions temporarily
     */
    disableActionsTemporarily(duration) {
        const buttons = document.querySelectorAll('button:not(.error-close)');
        buttons.forEach(btn => {
            btn.disabled = true;
            btn.classList.add('disabled-temporarily');
        });
        
        setTimeout(() => {
            buttons.forEach(btn => {
                btn.disabled = false;
                btn.classList.remove('disabled-temporarily');
            });
        }, duration);
    }
    
    /**
     * Display inline validation errors
     */
    displayInlineValidationErrors(formId, fields) {
        const form = document.getElementById(formId);
        if (!form) return;
        
        // Clear existing errors
        form.querySelectorAll('.validation-error').forEach(el => el.remove());
        
        // Display new errors
        Object.keys(fields).forEach(fieldName => {
            const field = form.querySelector(`[name="${fieldName}"]`);
            if (field) {
                const errorElement = document.createElement('div');
                errorElement.className = 'validation-error';
                errorElement.textContent = fields[fieldName];
                field.parentElement.appendChild(errorElement);
                field.classList.add('error');
            }
        });
    }
    
    /**
     * Create modal dialog
     */
    createModal(title, message, buttons) {
        const modal = document.createElement('div');
        modal.className = 'error-modal';
        
        const buttonsHTML = buttons.map(btn => 
            `<button class="btn ${btn.class}" data-action="${btn.text}">${btn.text}</button>`
        ).join('');
        
        modal.innerHTML = `
            <div class="error-modal-content">
                <h3>${this.sanitizeHTML(title)}</h3>
                <p>${this.sanitizeHTML(message)}</p>
                <div class="error-modal-buttons">
                    ${buttonsHTML}
                </div>
            </div>
        `;
        
        // Attach button handlers
        buttons.forEach(btn => {
            const buttonElement = modal.querySelector(`[data-action="${btn.text}"]`);
            if (buttonElement) {
                buttonElement.onclick = btn.onclick;
            }
        });
        
        return modal;
    }
    
    /**
     * Sanitize HTML to prevent XSS
     */
    sanitizeHTML(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }
    
    /**
     * Get error log
     */
    getErrorLog() {
        return [...this.errorLog];
    }
    
    /**
     * Clear error log
     */
    clearErrorLog() {
        this.errorLog = [];
    }
    
    /**
     * Export error log
     */
    exportErrorLog() {
        const data = JSON.stringify(this.errorLog, null, 2);
        const blob = new Blob([data], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `error-log-${new Date().toISOString()}.json`;
        a.click();
        URL.revokeObjectURL(url);
    }
}

// Create global error handler instance
const errorHandler = new ErrorHandler();

// Export for use in other modules
window.errorHandler = errorHandler;
