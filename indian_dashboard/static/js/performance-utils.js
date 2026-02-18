/**
 * Performance Utilities
 * Debouncing, throttling, and rendering optimizations
 */

/**
 * Advanced debounce with immediate option
 */
function debounceAdvanced(func, wait, options = {}) {
    let timeout;
    let lastArgs;
    let lastThis;
    let result;
    let lastCallTime;
    let lastInvokeTime = 0;
    
    const { leading = false, trailing = true, maxWait } = options;

    function invokeFunc(time) {
        const args = lastArgs;
        const thisArg = lastThis;

        lastArgs = lastThis = undefined;
        lastInvokeTime = time;
        result = func.apply(thisArg, args);
        return result;
    }

    function leadingEdge(time) {
        lastInvokeTime = time;
        timeout = setTimeout(timerExpired, wait);
        return leading ? invokeFunc(time) : result;
    }

    function remainingWait(time) {
        const timeSinceLastCall = time - lastCallTime;
        const timeSinceLastInvoke = time - lastInvokeTime;
        const timeWaiting = wait - timeSinceLastCall;

        return maxWait !== undefined
            ? Math.min(timeWaiting, maxWait - timeSinceLastInvoke)
            : timeWaiting;
    }

    function shouldInvoke(time) {
        const timeSinceLastCall = time - lastCallTime;
        const timeSinceLastInvoke = time - lastInvokeTime;

        return (
            lastCallTime === undefined ||
            timeSinceLastCall >= wait ||
            timeSinceLastCall < 0 ||
            (maxWait !== undefined && timeSinceLastInvoke >= maxWait)
        );
    }

    function timerExpired() {
        const time = Date.now();
        if (shouldInvoke(time)) {
            return trailingEdge(time);
        }
        timeout = setTimeout(timerExpired, remainingWait(time));
    }

    function trailingEdge(time) {
        timeout = undefined;

        if (trailing && lastArgs) {
            return invokeFunc(time);
        }
        lastArgs = lastThis = undefined;
        return result;
    }

    function cancel() {
        if (timeout !== undefined) {
            clearTimeout(timeout);
        }
        lastInvokeTime = 0;
        lastArgs = lastCallTime = lastThis = timeout = undefined;
    }

    function flush() {
        return timeout === undefined ? result : trailingEdge(Date.now());
    }

    function debounced(...args) {
        const time = Date.now();
        const isInvoking = shouldInvoke(time);

        lastArgs = args;
        lastThis = this;
        lastCallTime = time;

        if (isInvoking) {
            if (timeout === undefined) {
                return leadingEdge(lastCallTime);
            }
            if (maxWait !== undefined) {
                timeout = setTimeout(timerExpired, wait);
                return invokeFunc(lastCallTime);
            }
        }
        if (timeout === undefined) {
            timeout = setTimeout(timerExpired, wait);
        }
        return result;
    }

    debounced.cancel = cancel;
    debounced.flush = flush;
    return debounced;
}

/**
 * Advanced throttle with leading/trailing options
 */
function throttleAdvanced(func, wait, options = {}) {
    let timeout;
    let previous = 0;
    const { leading = true, trailing = true } = options;

    const throttled = function(...args) {
        const now = Date.now();
        if (!previous && !leading) previous = now;
        
        const remaining = wait - (now - previous);

        if (remaining <= 0 || remaining > wait) {
            if (timeout) {
                clearTimeout(timeout);
                timeout = null;
            }
            previous = now;
            func.apply(this, args);
        } else if (!timeout && trailing) {
            timeout = setTimeout(() => {
                previous = leading ? Date.now() : 0;
                timeout = null;
                func.apply(this, args);
            }, remaining);
        }
    };

    throttled.cancel = function() {
        clearTimeout(timeout);
        previous = 0;
        timeout = null;
    };

    return throttled;
}

/**
 * Request Animation Frame throttle for smooth rendering
 */
function rafThrottle(func) {
    let rafId = null;
    let lastArgs = null;

    const throttled = function(...args) {
        lastArgs = args;
        
        if (rafId === null) {
            rafId = requestAnimationFrame(() => {
                func.apply(this, lastArgs);
                rafId = null;
                lastArgs = null;
            });
        }
    };

    throttled.cancel = function() {
        if (rafId !== null) {
            cancelAnimationFrame(rafId);
            rafId = null;
            lastArgs = null;
        }
    };

    return throttled;
}

/**
 * Batch DOM updates to minimize reflows
 */
class DOMBatcher {
    constructor() {
        this.queue = [];
        this.scheduled = false;
    }

    add(updateFn) {
        this.queue.push(updateFn);
        this.schedule();
    }

    schedule() {
        if (this.scheduled) return;
        
        this.scheduled = true;
        requestAnimationFrame(() => {
            this.flush();
        });
    }

    flush() {
        const updates = this.queue.slice();
        this.queue = [];
        this.scheduled = false;

        // Execute all updates in batch
        updates.forEach(fn => {
            try {
                fn();
            } catch (error) {
                console.error('DOM batch update error:', error);
            }
        });
    }

    clear() {
        this.queue = [];
        this.scheduled = false;
    }
}

/**
 * Virtual Scroll Manager for large lists
 */
class VirtualScrollManager {
    constructor(options = {}) {
        this.container = options.container;
        this.itemHeight = options.itemHeight || 50;
        this.buffer = options.buffer || 5;
        this.items = [];
        this.visibleRange = { start: 0, end: 0 };
        this.scrollTop = 0;
    }

    setItems(items) {
        this.items = items;
        this.updateVisibleRange();
    }

    updateVisibleRange() {
        if (!this.container) return;

        const containerHeight = this.container.clientHeight;
        const scrollTop = this.container.scrollTop;

        const startIndex = Math.max(0, Math.floor(scrollTop / this.itemHeight) - this.buffer);
        const visibleCount = Math.ceil(containerHeight / this.itemHeight);
        const endIndex = Math.min(
            this.items.length,
            startIndex + visibleCount + this.buffer * 2
        );

        this.visibleRange = { start: startIndex, end: endIndex };
        this.scrollTop = scrollTop;
    }

    getVisibleItems() {
        return this.items.slice(this.visibleRange.start, this.visibleRange.end);
    }

    getOffsetTop() {
        return this.visibleRange.start * this.itemHeight;
    }

    getTotalHeight() {
        return this.items.length * this.itemHeight;
    }
}

/**
 * Memoization helper for expensive computations
 */
function memoize(func, resolver) {
    const cache = new Map();

    const memoized = function(...args) {
        const key = resolver ? resolver.apply(this, args) : JSON.stringify(args);
        
        if (cache.has(key)) {
            return cache.get(key);
        }

        const result = func.apply(this, args);
        cache.set(key, result);
        return result;
    };

    memoized.cache = cache;
    memoized.clear = () => cache.clear();
    
    return memoized;
}

/**
 * Lazy loader for images and heavy content
 */
class LazyLoader {
    constructor(options = {}) {
        this.rootMargin = options.rootMargin || '50px';
        this.threshold = options.threshold || 0.01;
        this.observer = null;
        this.init();
    }

    init() {
        if ('IntersectionObserver' in window) {
            this.observer = new IntersectionObserver(
                this.handleIntersection.bind(this),
                {
                    rootMargin: this.rootMargin,
                    threshold: this.threshold
                }
            );
        }
    }

    observe(element) {
        if (this.observer) {
            this.observer.observe(element);
        }
    }

    unobserve(element) {
        if (this.observer) {
            this.observer.unobserve(element);
        }
    }

    handleIntersection(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const element = entry.target;
                
                // Load image
                if (element.dataset.src) {
                    element.src = element.dataset.src;
                    delete element.dataset.src;
                }

                // Execute load callback
                if (element.dataset.onload) {
                    const callback = window[element.dataset.onload];
                    if (typeof callback === 'function') {
                        callback(element);
                    }
                }

                this.unobserve(element);
            }
        });
    }

    disconnect() {
        if (this.observer) {
            this.observer.disconnect();
        }
    }
}

/**
 * Performance monitor
 */
class PerformanceMonitor {
    constructor() {
        this.metrics = {
            apiCalls: 0,
            cacheHits: 0,
            cacheMisses: 0,
            renderTime: [],
            apiTime: []
        };
    }

    recordAPICall(duration, cached = false) {
        this.metrics.apiCalls++;
        if (cached) {
            this.metrics.cacheHits++;
        } else {
            this.metrics.cacheMisses++;
            this.metrics.apiTime.push(duration);
        }
    }

    recordRenderTime(duration) {
        this.metrics.renderTime.push(duration);
        
        // Keep only last 100 measurements
        if (this.metrics.renderTime.length > 100) {
            this.metrics.renderTime.shift();
        }
    }

    getStats() {
        const avgRenderTime = this.metrics.renderTime.length > 0
            ? this.metrics.renderTime.reduce((a, b) => a + b, 0) / this.metrics.renderTime.length
            : 0;

        const avgAPITime = this.metrics.apiTime.length > 0
            ? this.metrics.apiTime.reduce((a, b) => a + b, 0) / this.metrics.apiTime.length
            : 0;

        const cacheHitRate = this.metrics.apiCalls > 0
            ? (this.metrics.cacheHits / this.metrics.apiCalls) * 100
            : 0;

        return {
            totalAPICalls: this.metrics.apiCalls,
            cacheHits: this.metrics.cacheHits,
            cacheMisses: this.metrics.cacheMisses,
            cacheHitRate: cacheHitRate.toFixed(2) + '%',
            avgRenderTime: avgRenderTime.toFixed(2) + 'ms',
            avgAPITime: avgAPITime.toFixed(2) + 'ms'
        };
    }

    reset() {
        this.metrics = {
            apiCalls: 0,
            cacheHits: 0,
            cacheMisses: 0,
            renderTime: [],
            apiTime: []
        };
    }
}

// Create global instances
window.domBatcher = new DOMBatcher();
window.lazyLoader = new LazyLoader();
window.performanceMonitor = new PerformanceMonitor();

// Export utilities
window.debounceAdvanced = debounceAdvanced;
window.throttleAdvanced = throttleAdvanced;
window.rafThrottle = rafThrottle;
window.memoize = memoize;
window.VirtualScrollManager = VirtualScrollManager;
window.DOMBatcher = DOMBatcher;
window.LazyLoader = LazyLoader;
window.PerformanceMonitor = PerformanceMonitor;
