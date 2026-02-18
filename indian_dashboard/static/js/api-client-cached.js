/**
 * Cached API Client for Indian Market Trading Dashboard
 * Extends base API client with caching and request deduplication
 */

class CachedAPIClient extends APIClient {
    constructor() {
        super();
        
        // Cache TTL configurations (in milliseconds)
        this.cacheTTL = {
            brokers: 3600000,        // 1 hour - brokers list rarely changes
            instruments: 300000,      // 5 minutes - instrument data
            brokerStatus: 10000,      // 10 seconds - broker status
            botStatus: 5000,          // 5 seconds - bot status
            accountInfo: 5000,        // 5 seconds - account info
            positions: 5000,          // 5 seconds - positions
            config: 60000,            // 1 minute - configuration
            presets: 3600000,         // 1 hour - presets rarely change
            trades: 30000             // 30 seconds - trade history
        };

        // Endpoints that should not be cached
        this.noCacheEndpoints = [
            '/broker/connect',
            '/broker/disconnect',
            '/broker/oauth/initiate',
            '/instruments/refresh',
            '/config',  // POST requests
            '/bot/start',
            '/bot/stop',
            '/bot/restart'
        ];
    }

    /**
     * Enhanced request with caching and deduplication
     */
    async request(endpoint, options = {}) {
        const method = options.method || 'GET';
        const cacheKey = cacheManager.generateKey(endpoint, options.body ? JSON.parse(options.body) : {});
        
        // Only cache GET requests
        const shouldCache = method === 'GET' && !this.shouldSkipCache(endpoint);
        
        // Check cache first
        if (shouldCache) {
            const cached = cacheManager.get(cacheKey);
            if (cached) {
                performanceMonitor.recordAPICall(0, true);
                return cached;
            }
        }

        // Use request deduplication for GET requests
        if (method === 'GET') {
            return requestDeduplicator.execute(cacheKey, async () => {
                return this.executeRequest(endpoint, options, cacheKey, shouldCache);
            });
        }

        // Execute request directly for non-GET
        return this.executeRequest(endpoint, options, cacheKey, shouldCache);
    }

    /**
     * Execute the actual request
     */
    async executeRequest(endpoint, options, cacheKey, shouldCache) {
        const startTime = performance.now();
        
        try {
            const response = await super.request(endpoint, options);
            const duration = performance.now() - startTime;
            
            performanceMonitor.recordAPICall(duration, false);

            // Cache successful GET responses
            if (shouldCache && response) {
                const ttl = this.getCacheTTL(endpoint);
                cacheManager.set(cacheKey, response, ttl);
            }

            return response;
        } catch (error) {
            throw error;
        }
    }

    /**
     * Check if endpoint should skip cache
     */
    shouldSkipCache(endpoint) {
        return this.noCacheEndpoints.some(pattern => endpoint.includes(pattern));
    }

    /**
     * Get cache TTL for endpoint
     */
    getCacheTTL(endpoint) {
        if (endpoint.includes('/broker/list')) return this.cacheTTL.brokers;
        if (endpoint.includes('/broker/status')) return this.cacheTTL.brokerStatus;
        if (endpoint.includes('/instruments')) return this.cacheTTL.instruments;
        if (endpoint.includes('/bot/status')) return this.cacheTTL.botStatus;
        if (endpoint.includes('/bot/account')) return this.cacheTTL.accountInfo;
        if (endpoint.includes('/bot/positions')) return this.cacheTTL.positions;
        if (endpoint.includes('/bot/trades')) return this.cacheTTL.trades;
        if (endpoint.includes('/config/presets')) return this.cacheTTL.presets;
        if (endpoint.includes('/config')) return this.cacheTTL.config;
        
        return cacheManager.defaultTTL;
    }

    /**
     * Invalidate cache for specific patterns
     */
    invalidateCache(pattern) {
        if (pattern === 'broker') {
            cacheManager.invalidatePattern('/broker/');
        } else if (pattern === 'instruments') {
            cacheManager.invalidatePattern('/instruments');
        } else if (pattern === 'bot') {
            cacheManager.invalidatePattern('/bot/');
        } else if (pattern === 'config') {
            cacheManager.invalidatePattern('/config');
        } else if (pattern === 'all') {
            cacheManager.clear();
        } else {
            cacheManager.invalidatePattern(pattern);
        }
    }

    // Override methods that should invalidate cache

    async connectBroker(broker, credentials) {
        const result = await super.connectBroker(broker, credentials);
        this.invalidateCache('broker');
        this.invalidateCache('instruments'); // Instruments depend on broker
        return result;
    }

    async disconnectBroker() {
        const result = await super.disconnectBroker();
        this.invalidateCache('broker');
        this.invalidateCache('instruments');
        return result;
    }

    async refreshInstruments() {
        const result = await super.refreshInstruments();
        this.invalidateCache('instruments');
        return result;
    }

    async saveConfig(config, name = null) {
        const result = await super.saveConfig(config, name);
        this.invalidateCache('config');
        return result;
    }

    async deleteConfig(name) {
        const result = await super.deleteConfig(name);
        this.invalidateCache('config');
        return result;
    }

    async startBot(config) {
        const result = await super.startBot(config);
        this.invalidateCache('bot');
        return result;
    }

    async stopBot() {
        const result = await super.stopBot();
        this.invalidateCache('bot');
        return result;
    }

    async restartBot() {
        const result = await super.restartBot();
        this.invalidateCache('bot');
        return result;
    }

    async closePosition(symbol) {
        const result = await super.closePosition(symbol);
        // Invalidate positions and account info
        cacheManager.invalidatePattern('/bot/positions');
        cacheManager.invalidatePattern('/bot/account');
        return result;
    }

    /**
     * Get cache statistics
     */
    getCacheStats() {
        return cacheManager.getStats();
    }

    /**
     * Get performance statistics
     */
    getPerformanceStats() {
        return performanceMonitor.getStats();
    }
}

// Replace global API client with cached version
if (typeof api !== 'undefined') {
    // Preserve any existing configuration
    const oldApi = api;
    window.api = new CachedAPIClient();
    
    // Copy any custom properties
    if (oldApi.baseURL) {
        window.api.baseURL = oldApi.baseURL;
    }
} else {
    window.api = new CachedAPIClient();
}

console.log('[Performance] Cached API client initialized');
