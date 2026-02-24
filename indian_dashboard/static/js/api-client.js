/**
 * API Client for Indian Market Trading Dashboard
 */

const API_BASE = '/api';

class APIClient {
    constructor() {
        this.baseURL = API_BASE;
    }

    /**
     * Make HTTP request
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;

        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        try {
            const response = await fetch(url, config);
            const data = await response.json();

            if (!response.ok) {
                // Create error object with response details
                const error = {
                    response: {
                        status: response.status,
                        statusText: response.statusText,
                        data: data
                    }
                };

                // Handle error through error handler
                if (window.errorHandler) {
                    window.errorHandler.handleAPIError(error, {
                        endpoint,
                        method: options.method || 'GET'
                    });
                }

                throw error;
            }

            return data;
        } catch (error) {
            // Handle network errors
            if (!error.response) {
                const networkError = {
                    message: error.message || 'Network error',
                    type: 'network_error'
                };

                if (window.errorHandler) {
                    window.errorHandler.handleAPIError(networkError, {
                        endpoint,
                        method: options.method || 'GET',
                        retryable: true,
                        retryFunction: () => this.request(endpoint, options),
                        retryKey: endpoint
                    });
                }
            }

            throw error;
        }
    }

    // Broker API
    async getBrokers() {
        return this.request('/broker/list');
    }

    async getCredentialsForm(broker) {
        return this.request(`/broker/credentials-form/${broker}`);
    }

    async connectBroker(broker, credentials) {
        return this.request('/broker/connect', {
            method: 'POST',
            body: JSON.stringify({ broker, credentials })
        });
    }

    async disconnectBroker() {
        return this.request('/broker/disconnect', {
            method: 'POST'
        });
    }

    async getBrokerStatus() {
        return this.request('/broker/status');
    }

    async testConnection() {
        return this.request('/broker/test', {
            method: 'POST'
        });
    }

    async initiateOAuth(broker, apiKey, apiSecret) {
        return this.request('/broker/oauth/initiate', {
            method: 'POST',
            body: JSON.stringify({
                broker,
                api_key: apiKey,
                api_secret: apiSecret
            })
        });
    }

    // Instruments API
    async getInstruments(params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.request(`/instruments${query ? '?' + query : ''}`);
    }

    async refreshInstruments() {
        return this.request('/instruments/refresh', {
            method: 'POST'
        });
    }

    async getInstrumentByToken(token) {
        return this.request(`/instruments/${token}`);
    }

    async getQuote(symbol) {
        return this.request(`/instruments/quote/${symbol}`);
    }

    async getCacheInfo() {
        return this.request('/instruments/cache-info');
    }

    // Configuration API
    async getCurrentConfig() {
        return this.request('/config');
    }

    async saveConfig(config, name = null) {
        return this.request('/config', {
            method: 'POST',
            body: JSON.stringify({ config, name })
        });
    }

    async listConfigs() {
        return this.request('/config/list');
    }

    async getConfig(name) {
        return this.request(`/config/${name}`);
    }

    async deleteConfig(name) {
        return this.request(`/config/${name}`, {
            method: 'DELETE'
        });
    }

    async getPresets() {
        return this.request('/config/presets');
    }

    async getPreset(presetName) {
        return this.request(`/config/presets/${presetName}`);
    }

    async validateConfig(config) {
        return this.request('/config/validate', {
            method: 'POST',
            body: JSON.stringify({ config })
        });
    }

    // Bot API
    async startBot(config) {
        return this.request('/bot/start', {
            method: 'POST',
            body: JSON.stringify({ config })
        });
    }

    async stopBot() {
        return this.request('/bot/stop', {
            method: 'POST'
        });
    }

    async restartBot() {
        return this.request('/bot/restart', {
            method: 'POST'
        });
    }

    async getBotStatus() {
        return this.request('/bot/status');
    }

    async getAccountInfo() {
        return this.request('/bot/account');
    }

    async getPositions() {
        return this.request('/bot/positions');
    }

    async closePosition(symbol) {
        return this.request(`/bot/positions/${symbol}`, {
            method: 'DELETE'
        });
    }

    async getTrades(fromDate = null, toDate = null) {
        const params = {};
        if (fromDate) params.from_date = fromDate;
        if (toDate) params.to_date = toDate;

        const query = new URLSearchParams(params).toString();
        return this.request(`/bot/trades${query ? '?' + query : ''}`);
    }

    async getBotConfig() {
        return this.request('/bot/config');
    }

    // Logs API
    async getLogs(params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.request(`/logs${query ? '?' + query : ''}`);
    }

    async setLogLevel(level) {
        return this.request('/logs/level', {
            method: 'POST',
            body: JSON.stringify({ level })
        });
    }

    async clearLogs() {
        return this.request('/logs/clear', {
            method: 'POST'
        });
    }

    getDownloadLogsUrl(params = {}) {
        const query = new URLSearchParams(params).toString();
        return `${this.baseURL}/logs/download${query ? '?' + query : ''}`;
    }
}

// Create global API client instance
const api = new APIClient();
