/**
 * Cache Manager for API Responses
 * Implements request caching with TTL and LRU eviction
 */

class CacheManager {
    constructor(options = {}) {
        this.maxSize = options.maxSize || 100; // Maximum cache entries
        this.defaultTTL = options.defaultTTL || 300000; // 5 minutes default
        this.cache = new Map();
        this.accessOrder = []; // For LRU tracking
    }

    /**
     * Generate cache key from endpoint and params
     */
    generateKey(endpoint, params = {}) {
        const sortedParams = Object.keys(params)
            .sort()
            .map(key => `${key}=${JSON.stringify(params[key])}`)
            .join('&');
        return `${endpoint}?${sortedParams}`;
    }

    /**
     * Get cached value if valid
     */
    get(key) {
        const entry = this.cache.get(key);
        
        if (!entry) {
            return null;
        }

        // Check if expired
        if (Date.now() > entry.expiresAt) {
            this.cache.delete(key);
            this.removeFromAccessOrder(key);
            return null;
        }

        // Update access order for LRU
        this.updateAccessOrder(key);
        
        return entry.data;
    }

    /**
     * Set cache value with TTL
     */
    set(key, data, ttl = null) {
        const expiresAt = Date.now() + (ttl || this.defaultTTL);
        
        // Evict oldest if at capacity
        if (this.cache.size >= this.maxSize && !this.cache.has(key)) {
            this.evictOldest();
        }

        this.cache.set(key, {
            data,
            expiresAt,
            cachedAt: Date.now()
        });

        this.updateAccessOrder(key);
    }

    /**
     * Check if key exists and is valid
     */
    has(key) {
        return this.get(key) !== null;
    }

    /**
     * Invalidate specific cache entry
     */
    invalidate(key) {
        this.cache.delete(key);
        this.removeFromAccessOrder(key);
    }

    /**
     * Invalidate all entries matching pattern
     */
    invalidatePattern(pattern) {
        const regex = new RegExp(pattern);
        const keysToDelete = [];

        for (const key of this.cache.keys()) {
            if (regex.test(key)) {
                keysToDelete.push(key);
            }
        }

        keysToDelete.forEach(key => this.invalidate(key));
    }

    /**
     * Clear all cache
     */
    clear() {
        this.cache.clear();
        this.accessOrder = [];
    }

    /**
     * Get cache statistics
     */
    getStats() {
        let validEntries = 0;
        let expiredEntries = 0;
        const now = Date.now();

        for (const entry of this.cache.values()) {
            if (now > entry.expiresAt) {
                expiredEntries++;
            } else {
                validEntries++;
            }
        }

        return {
            size: this.cache.size,
            maxSize: this.maxSize,
            validEntries,
            expiredEntries,
            hitRate: this.hitRate || 0
        };
    }

    /**
     * Update access order for LRU
     */
    updateAccessOrder(key) {
        this.removeFromAccessOrder(key);
        this.accessOrder.push(key);
    }

    /**
     * Remove from access order
     */
    removeFromAccessOrder(key) {
        const index = this.accessOrder.indexOf(key);
        if (index > -1) {
            this.accessOrder.splice(index, 1);
        }
    }

    /**
     * Evict oldest entry (LRU)
     */
    evictOldest() {
        if (this.accessOrder.length === 0) {
            return;
        }

        const oldestKey = this.accessOrder[0];
        this.cache.delete(oldestKey);
        this.accessOrder.shift();
    }

    /**
     * Clean expired entries
     */
    cleanExpired() {
        const now = Date.now();
        const keysToDelete = [];

        for (const [key, entry] of this.cache.entries()) {
            if (now > entry.expiresAt) {
                keysToDelete.push(key);
            }
        }

        keysToDelete.forEach(key => this.invalidate(key));
        
        return keysToDelete.length;
    }
}

/**
 * Request Deduplication Manager
 * Prevents duplicate simultaneous requests
 */
class RequestDeduplicator {
    constructor() {
        this.pendingRequests = new Map();
    }

    /**
     * Execute request with deduplication
     */
    async execute(key, requestFn) {
        // Check if request is already pending
        if (this.pendingRequests.has(key)) {
            return this.pendingRequests.get(key);
        }

        // Create new request promise
        const promise = requestFn()
            .finally(() => {
                // Remove from pending after completion
                this.pendingRequests.delete(key);
            });

        this.pendingRequests.set(key, promise);
        return promise;
    }

    /**
     * Check if request is pending
     */
    isPending(key) {
        return this.pendingRequests.has(key);
    }

    /**
     * Clear all pending requests
     */
    clear() {
        this.pendingRequests.clear();
    }
}

// Create global instances
window.cacheManager = new CacheManager({
    maxSize: 100,
    defaultTTL: 300000 // 5 minutes
});

window.requestDeduplicator = new RequestDeduplicator();

// Auto-clean expired entries every minute
setInterval(() => {
    const cleaned = window.cacheManager.cleanExpired();
    if (cleaned > 0) {
        console.log(`[Cache] Cleaned ${cleaned} expired entries`);
    }
}, 60000);
