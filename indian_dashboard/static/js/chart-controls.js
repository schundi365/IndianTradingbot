/**
 * Chart Controls Component
 * Handles symbol selection, timeframe changes, and indicator toggles
 */

class ChartControls {
    constructor(priceChart) {
        this.priceChart = priceChart;
        this.selectedSymbol = null;
        this.selectedTimeframe = '15min';
        this.activeIndicators = [];
        this.availableIndicators = [
            { id: 'ma_20', name: 'MA(20)', type: 'overlay' },
            { id: 'ema_20', name: 'EMA(20)', type: 'overlay' },
            { id: 'bb', name: 'Bollinger Bands', type: 'overlay' },
            { id: 'macd', name: 'MACD', type: 'panel' },
            { id: 'rsi', name: 'RSI', type: 'panel' },
            { id: 'atr', name: 'ATR', type: 'panel' }
        ];
    }

    /**
     * Initialize controls
     */
    init() {
        this.setupSymbolSelector();
        this.setupTimeframeSelector();
        this.setupIndicatorToggles();
        this.setupRefreshButton();
        
        console.log('Chart controls initialized');
    }

    /**
     * Setup symbol selector
     */
    setupSymbolSelector() {
        const selector = document.getElementById('chart-symbol-selector');
        if (!selector) return;

        // Populate with selected instruments
        const instruments = appState.get('selectedInstruments') || [];
        
        selector.innerHTML = '<option value="">-- Select Symbol --</option>';
        
        instruments.forEach(inst => {
            const option = document.createElement('option');
            option.value = inst.tradingsymbol;
            option.textContent = `${inst.tradingsymbol} (${inst.exchange})`;
            selector.appendChild(option);
        });

        // Handle selection change
        selector.addEventListener('change', (e) => {
            this.handleSymbolChange(e.target.value);
        });

        // Auto-select first instrument
        if (instruments.length > 0) {
            selector.value = instruments[0].tradingsymbol;
            this.handleSymbolChange(instruments[0].tradingsymbol);
        }
    }

    /**
     * Setup timeframe selector
     */
    setupTimeframeSelector() {
        const buttons = document.querySelectorAll('.timeframe-btn');
        
        buttons.forEach(btn => {
            btn.addEventListener('click', () => {
                // Remove active class from all buttons
                buttons.forEach(b => b.classList.remove('active'));
                
                // Add active class to clicked button
                btn.classList.add('active');
                
                // Handle timeframe change
                const timeframe = btn.dataset.timeframe;
                this.handleTimeframeChange(timeframe);
            });
        });

        // Set default active
        const defaultBtn = document.querySelector('.timeframe-btn[data-timeframe="15min"]');
        if (defaultBtn) {
            defaultBtn.classList.add('active');
        }
    }

    /**
     * Setup indicator toggles
     */
    setupIndicatorToggles() {
        const container = document.getElementById('indicator-toggles');
        if (!container) return;

        this.availableIndicators.forEach(indicator => {
            const toggle = document.createElement('button');
            toggle.className = 'indicator-toggle-btn';
            toggle.dataset.indicator = indicator.id;
            toggle.textContent = indicator.name;
            
            toggle.addEventListener('click', () => {
                this.handleIndicatorToggle(indicator.id, toggle);
            });
            
            container.appendChild(toggle);
        });
    }

    /**
     * Setup refresh button
     */
    setupRefreshButton() {
        const btn = document.getElementById('chart-refresh-btn');
        if (!btn) return;

        btn.addEventListener('click', () => {
            if (this.selectedSymbol) {
                this.refreshChart();
            }
        });
    }

    /**
     * Handle symbol change
     */
    handleSymbolChange(symbol) {
        if (!symbol) return;
        
        this.selectedSymbol = symbol;
        this.loadChart();
    }

    /**
     * Handle timeframe change
     */
    handleTimeframeChange(timeframe) {
        this.selectedTimeframe = timeframe;
        
        if (this.selectedSymbol) {
            this.loadChart();
        }
    }

    /**
     * Handle indicator toggle
     */
    handleIndicatorToggle(indicatorId, button) {
        const index = this.activeIndicators.indexOf(indicatorId);
        
        if (index > -1) {
            // Remove indicator
            this.activeIndicators.splice(index, 1);
            button.classList.remove('active');
        } else {
            // Add indicator
            this.activeIndicators.push(indicatorId);
            button.classList.add('active');
        }
        
        // Reload chart with updated indicators
        if (this.selectedSymbol) {
            this.loadChart();
        }
    }

    /**
     * Load chart with current settings
     */
    async loadChart() {
        try {
            await this.priceChart.loadData(
                this.selectedSymbol,
                this.selectedTimeframe,
                this.activeIndicators
            );
        } catch (error) {
            console.error('Error loading chart:', error);
            showNotification('Failed to load chart', 'error');
        }
    }

    /**
     * Refresh chart
     */
    async refreshChart() {
        await this.loadChart();
        showNotification('Chart refreshed', 'success');
    }

    /**
     * Update symbol list
     */
    updateSymbolList() {
        this.setupSymbolSelector();
    }
}

// Global instance
window.ChartControls = ChartControls;
