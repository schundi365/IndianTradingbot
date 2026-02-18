/**
 * State Management for Indian Market Trading Dashboard
 */

class AppState {
    constructor() {
        this.state = {
            broker: {
                connected: false,
                type: null,
                userInfo: {}
            },
            instruments: {
                all: [],        // All instruments from API
                list: [],       // Filtered/searched instruments
                selected: [],
                filters: {
                    search: '',
                    exchange: [],
                    type: []
                },
                pagination: {
                    page: 1,
                    perPage: 50
                },
                sort: {
                    field: 'symbol',
                    direction: 'asc'
                }
            },
            config: {
                current: null,
                saved: []
            },
            bot: {
                running: false,
                status: {},
                positions: [],
                trades: []
            }
        };
        
        this.listeners = {};
        this.loadFromStorage();
    }

    /**
     * Get state value
     */
    get(path) {
        const keys = path.split('.');
        let value = this.state;
        
        for (const key of keys) {
            if (value && typeof value === 'object' && key in value) {
                value = value[key];
            } else {
                return undefined;
            }
        }
        
        return value;
    }

    /**
     * Set state value
     */
    set(path, value) {
        const keys = path.split('.');
        const lastKey = keys.pop();
        let target = this.state;
        
        for (const key of keys) {
            if (!(key in target)) {
                target[key] = {};
            }
            target = target[key];
        }
        
        target[lastKey] = value;
        this.saveToStorage();
        this.notify(path, value);
    }

    /**
     * Update state (merge with existing)
     */
    update(path, updates) {
        const current = this.get(path);
        const newValue = { ...current, ...updates };
        this.set(path, newValue);
    }

    /**
     * Subscribe to state changes
     */
    subscribe(path, callback) {
        if (!this.listeners[path]) {
            this.listeners[path] = [];
        }
        this.listeners[path].push(callback);
        
        // Return unsubscribe function
        return () => {
            this.listeners[path] = this.listeners[path].filter(cb => cb !== callback);
        };
    }

    /**
     * Notify listeners of state change
     */
    notify(path, value) {
        if (this.listeners[path]) {
            this.listeners[path].forEach(callback => callback(value));
        }
        
        // Notify parent paths
        const parts = path.split('.');
        for (let i = parts.length - 1; i > 0; i--) {
            const parentPath = parts.slice(0, i).join('.');
            if (this.listeners[parentPath]) {
                const parentValue = this.get(parentPath);
                this.listeners[parentPath].forEach(callback => callback(parentValue));
            }
        }
    }

    /**
     * Save state to sessionStorage
     */
    saveToStorage() {
        try {
            sessionStorage.setItem('dashboardState', JSON.stringify(this.state));
        } catch (error) {
            console.error('Failed to save state:', error);
        }
    }

    /**
     * Load state from sessionStorage
     */
    loadFromStorage() {
        try {
            const saved = sessionStorage.getItem('dashboardState');
            if (saved) {
                this.state = { ...this.state, ...JSON.parse(saved) };
            }
        } catch (error) {
            console.error('Failed to load state:', error);
        }
    }

    /**
     * Clear state
     */
    clear() {
        this.state = {
            broker: {
                connected: false,
                type: null,
                userInfo: {}
            },
            instruments: {
                all: [],        // All instruments from API
                list: [],       // Filtered/searched instruments
                selected: [],
                filters: {
                    search: '',
                    exchange: [],
                    type: []
                },
                pagination: {
                    page: 1,
                    perPage: 50
                },
                sort: {
                    field: 'symbol',
                    direction: 'asc'
                }
            },
            config: {
                current: null,
                saved: []
            },
            bot: {
                running: false,
                status: {},
                positions: [],
                trades: []
            }
        };
        this.saveToStorage();
    }

    // Convenience methods for common operations
    
    setBrokerConnected(connected, type = null, userInfo = {}) {
        this.update('broker', { connected, type, userInfo });
    }

    setInstruments(instruments) {
        this.set('instruments.list', instruments);
    }
    
    setAllInstruments(instruments) {
        this.set('instruments.all', instruments);
        this.set('instruments.list', instruments);
    }

    addSelectedInstrument(instrument) {
        const selected = this.get('instruments.selected') || [];
        if (!selected.find(i => i.token === instrument.token)) {
            this.set('instruments.selected', [...selected, instrument]);
        }
    }

    removeSelectedInstrument(token) {
        const selected = this.get('instruments.selected') || [];
        this.set('instruments.selected', selected.filter(i => i.token !== token));
    }

    clearSelectedInstruments() {
        this.set('instruments.selected', []);
    }

    setConfig(config) {
        this.set('config.current', config);
    }

    setBotRunning(running) {
        this.set('bot.running', running);
    }

    setBotStatus(status) {
        this.set('bot.status', status);
    }

    setPositions(positions) {
        this.set('bot.positions', positions);
    }

    setTrades(trades) {
        this.set('bot.trades', trades);
    }
}

// Create global state instance
const appState = new AppState();
window.appState = appState;
