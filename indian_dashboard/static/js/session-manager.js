/**
 * Session Management Client
 * Handles CSRF tokens, session info, and session lifecycle
 */

class SessionManagerClient {
    constructor() {
        this.csrfToken = null;
        this.sessionInfo = null;
        this.sessionCheckInterval = null;
        this.autoExtendEnabled = true;
        this.sessionWarningThreshold = 300; // 5 minutes
    }

    /**
     * Initialize session manager
     */
    async init() {
        try {
            // Get CSRF token
            await this.refreshCSRFToken();
            
            // Get session info
            await this.refreshSessionInfo();
            
            // Start session monitoring
            this.startSessionMonitoring();
            
            console.log('SessionManager initialized');
        } catch (error) {
            console.error('Failed to initialize SessionManager:', error);
        }
    }

    /**
     * Get CSRF token from server
     */
    async refreshCSRFToken() {
        try {
            const response = await fetch('/api/session/csrf-token');
            const data = await response.json();
            
            if (data.status === 'success') {
                this.csrfToken = data.csrf_token;
                return this.csrfToken;
            } else {
                throw new Error('Failed to get CSRF token');
            }
        } catch (error) {
            console.error('Error refreshing CSRF token:', error);
            throw error;
        }
    }

    /**
     * Get current CSRF token
     */
    getCSRFToken() {
        return this.csrfToken;
    }

    /**
     * Get session information from server
     */
    async refreshSessionInfo() {
        try {
            const response = await fetch('/api/session/info');
            const data = await response.json();
            
            if (data.status === 'success') {
                this.sessionInfo = data.session;
                return this.sessionInfo;
            } else {
                throw new Error('Failed to get session info');
            }
        } catch (error) {
            console.error('Error refreshing session info:', error);
            throw error;
        }
    }

    /**
     * Get current session info
     */
    getSessionInfo() {
        return this.sessionInfo;
    }

    /**
     * Extend current session
     */
    async extendSession() {
        try {
            const response = await fetch('/api/session/extend', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRF-Token': this.csrfToken
                }
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                this.sessionInfo = data.session;
                console.log('Session extended');
                return true;
            } else {
                console.error('Failed to extend session:', data.message);
                return false;
            }
        } catch (error) {
            console.error('Error extending session:', error);
            return false;
        }
    }

    /**
     * Clear current session (logout)
     */
    async clearSession() {
        try {
            const response = await fetch('/api/session/clear', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRF-Token': this.csrfToken
                }
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                this.sessionInfo = null;
                this.csrfToken = null;
                console.log('Session cleared');
                return true;
            } else {
                console.error('Failed to clear session:', data.message);
                return false;
            }
        } catch (error) {
            console.error('Error clearing session:', error);
            return false;
        }
    }

    /**
     * Start monitoring session status
     */
    startSessionMonitoring(interval = 30000) {
        // Clear existing interval
        if (this.sessionCheckInterval) {
            clearInterval(this.sessionCheckInterval);
        }

        // Check session every interval
        this.sessionCheckInterval = setInterval(async () => {
            await this.checkSession();
        }, interval);

        console.log(`Session monitoring started (interval: ${interval}ms)`);
    }

    /**
     * Stop monitoring session status
     */
    stopSessionMonitoring() {
        if (this.sessionCheckInterval) {
            clearInterval(this.sessionCheckInterval);
            this.sessionCheckInterval = null;
            console.log('Session monitoring stopped');
        }
    }

    /**
     * Check session status and handle expiration
     */
    async checkSession() {
        try {
            await this.refreshSessionInfo();

            if (!this.sessionInfo || !this.sessionInfo.is_active) {
                this.handleSessionExpired();
                return;
            }

            // Check if session is about to expire
            if (this.sessionInfo.remaining_seconds < this.sessionWarningThreshold) {
                this.handleSessionWarning(this.sessionInfo.remaining_seconds);
                
                // Auto-extend if enabled
                if (this.autoExtendEnabled) {
                    await this.extendSession();
                }
            }
        } catch (error) {
            console.error('Error checking session:', error);
        }
    }

    /**
     * Handle session expiration
     */
    handleSessionExpired() {
        console.warn('Session expired');
        
        // Dispatch custom event
        window.dispatchEvent(new CustomEvent('sessionExpired', {
            detail: { message: 'Your session has expired. Please refresh the page.' }
        }));

        // Show notification if available
        if (window.showNotification) {
            window.showNotification('Session expired. Please refresh the page.', 'warning');
        }

        // Stop monitoring
        this.stopSessionMonitoring();
    }

    /**
     * Handle session warning (about to expire)
     */
    handleSessionWarning(remainingSeconds) {
        console.warn(`Session expiring in ${remainingSeconds} seconds`);
        
        // Dispatch custom event
        window.dispatchEvent(new CustomEvent('sessionWarning', {
            detail: { remainingSeconds }
        }));
    }

    /**
     * Add CSRF token to fetch request options
     */
    addCSRFToken(options = {}) {
        if (!options.headers) {
            options.headers = {};
        }

        options.headers['X-CSRF-Token'] = this.csrfToken;
        return options;
    }

    /**
     * Make authenticated fetch request with CSRF token
     */
    async fetch(url, options = {}) {
        // Add CSRF token for state-changing methods
        if (['POST', 'PUT', 'DELETE', 'PATCH'].includes(options.method?.toUpperCase())) {
            options = this.addCSRFToken(options);
        }

        try {
            const response = await fetch(url, options);

            // Handle session expired
            if (response.status === 401) {
                const data = await response.json();
                if (data.code === 'SESSION_EXPIRED' || data.code === 'SESSION_REQUIRED') {
                    this.handleSessionExpired();
                }
            }

            // Handle CSRF error
            if (response.status === 403) {
                const data = await response.json();
                if (data.code === 'CSRF_INVALID') {
                    console.error('CSRF validation failed, refreshing token...');
                    await this.refreshCSRFToken();
                }
            }

            return response;
        } catch (error) {
            console.error('Fetch error:', error);
            throw error;
        }
    }

    /**
     * Enable/disable auto session extension
     */
    setAutoExtend(enabled) {
        this.autoExtendEnabled = enabled;
        console.log(`Auto session extension ${enabled ? 'enabled' : 'disabled'}`);
    }

    /**
     * Set session warning threshold (seconds before expiry)
     */
    setWarningThreshold(seconds) {
        this.sessionWarningThreshold = seconds;
        console.log(`Session warning threshold set to ${seconds} seconds`);
    }
}

// Create global instance
window.sessionManager = new SessionManagerClient();

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    window.sessionManager.init();
});

// Handle session events
window.addEventListener('sessionExpired', (event) => {
    console.log('Session expired event:', event.detail);
});

window.addEventListener('sessionWarning', (event) => {
    console.log('Session warning event:', event.detail);
});
