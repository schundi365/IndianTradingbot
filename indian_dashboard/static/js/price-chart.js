/**
 * Price Chart Component
 * TradingView Lightweight Charts for candlestick display
 */

class PriceChart {
    constructor(containerId) {
        this.containerId = containerId;
        this.chart = null;
        this.candlestickSeries = null;
        this.volumeSeries = null;
        this.indicators = {};
        this.currentSymbol = null;
        this.currentTimeframe = '15min';
        this.tradeMarkers = [];
    }

    /**
     * Initialize chart
     */
    init() {
        const container = document.getElementById(this.containerId);
        if (!container) {
            console.error(`Container ${this.containerId} not found`);
            return;
        }

        // Create chart
        this.chart = LightweightCharts.createChart(container, {
            width: container.clientWidth,
            height: 600,
            layout: {
                background: { color: '#181A20' },
                textColor: '#EAECEF',
            },
            grid: {
                vertLines: { color: '#2B3139' },
                horzLines: { color: '#2B3139' },
            },
            crosshair: {
                mode: LightweightCharts.CrosshairMode.Normal,
            },
            rightPriceScale: {
                borderColor: '#2B3139',
            },
            timeScale: {
                borderColor: '#2B3139',
                timeVisible: true,
                secondsVisible: false,
            },
        });

        // Create candlestick series
        this.candlestickSeries = this.chart.addCandlestickSeries({
            upColor: '#0ECB81',
            downColor: '#F6465D',
            borderUpColor: '#0ECB81',
            borderDownColor: '#F6465D',
            wickUpColor: '#0ECB81',
            wickDownColor: '#F6465D',
        });

        // Create volume series
        this.volumeSeries = this.chart.addHistogramSeries({
            color: '#26a69a',
            priceFormat: {
                type: 'volume',
            },
            priceScaleId: 'volume',
            scaleMargins: {
                top: 0.8,
                bottom: 0,
            },
        });

        // Handle window resize
        window.addEventListener('resize', () => this.handleResize());

        console.log('Price chart initialized');
    }

    /**
     * Load price data for symbol
     */
    async loadData(symbol, timeframe = '15min', indicators = []) {
        try {
            this.currentSymbol = symbol;
            this.currentTimeframe = timeframe;

            // Show loading
            this.showLoading();

            // Fetch price data
            const indicatorsParam = indicators.join(',');
            const url = `/api/charts/price-data/${symbol}?timeframe=${timeframe}&bars=500&indicators=${indicatorsParam}`;
            
            const response = await fetch(url);
            const result = await response.json();

            if (!result.success) {
                throw new Error(result.error || 'Failed to load price data');
            }

            // Update chart
            this.updateChart(result.data);

            // Load trade markers
            await this.loadTradeMarkers(symbol);

            this.hideLoading();

        } catch (error) {
            console.error('Error loading price data:', error);
            this.hideLoading();
            showNotification(`Error loading chart: ${error.message}`, 'error');
        }
    }

    /**
     * Update chart with data
     */
    updateChart(data) {
        if (!data || !data.data) return;

        // Prepare candlestick data
        const candleData = data.data.map(d => ({
            time: this.parseTime(d.time),
            open: d.open,
            high: d.high,
            low: d.low,
            close: d.close
        }));

        // Prepare volume data
        const volumeData = data.data.map(d => ({
            time: this.parseTime(d.time),
            value: d.volume,
            color: d.close >= d.open ? 'rgba(14, 203, 129, 0.5)' : 'rgba(246, 70, 93, 0.5)'
        }));

        // Update series
        this.candlestickSeries.setData(candleData);
        this.volumeSeries.setData(volumeData);

        // Update indicators
        if (data.indicators) {
            this.updateIndicators(data.indicators, data.data);
        }

        // Fit content
        this.chart.timeScale().fitContent();
    }

    /**
     * Update indicators
     */
    updateIndicators(indicators, priceData) {
        // Clear existing indicators
        Object.values(this.indicators).forEach(series => {
            this.chart.removeSeries(series);
        });
        this.indicators = {};

        // Add MA indicators
        Object.keys(indicators).forEach(key => {
            if (key.startsWith('ma_') || key.startsWith('ema_')) {
                const values = indicators[key];
                const lineData = priceData.map((d, i) => ({
                    time: this.parseTime(d.time),
                    value: values[i]
                })).filter(d => d.value > 0);

                const color = key.startsWith('ma_') ? '#2196F3' : '#FF9800';
                const series = this.chart.addLineSeries({
                    color: color,
                    lineWidth: 2,
                    title: key.toUpperCase()
                });
                series.setData(lineData);
                this.indicators[key] = series;
            }

            // Bollinger Bands
            if (key === 'bb_upper' || key === 'bb_middle' || key === 'bb_lower') {
                const values = indicators[key];
                const lineData = priceData.map((d, i) => ({
                    time: this.parseTime(d.time),
                    value: values[i]
                })).filter(d => d.value > 0);

                const colors = {
                    'bb_upper': '#9C27B0',
                    'bb_middle': '#2196F3',
                    'bb_lower': '#9C27B0'
                };

                const series = this.chart.addLineSeries({
                    color: colors[key],
                    lineWidth: 1,
                    lineStyle: key === 'bb_middle' ? 0 : 2, // Solid for middle, dashed for bands
                    title: key.toUpperCase().replace('_', ' ')
                });
                series.setData(lineData);
                this.indicators[key] = series;
            }
        });
    }

    /**
     * Load trade markers
     */
    async loadTradeMarkers(symbol) {
        try {
            const response = await fetch(`/api/charts/trade-markers/${symbol}`);
            const result = await response.json();

            if (result.success && result.markers) {
                this.addTradeMarkers(result.markers);
            }
        } catch (error) {
            console.error('Error loading trade markers:', error);
        }
    }

    /**
     * Add trade markers to chart
     */
    addTradeMarkers(markers) {
        const chartMarkers = markers.map(m => {
            const isEntry = m.type === 'entry';
            const isBuy = m.side === 'BUY';

            return {
                time: this.parseTime(m.time),
                position: isEntry ? 'belowBar' : 'aboveBar',
                color: isEntry ? (isBuy ? '#0ECB81' : '#F6465D') : '#FCD535',
                shape: isEntry ? 'arrowUp' : 'arrowDown',
                text: isEntry ? `${m.side} ${m.quantity}` : `Exit ${m.quantity}`
            };
        });

        this.candlestickSeries.setMarkers(chartMarkers);
        this.tradeMarkers = markers;
    }

    /**
     * Toggle indicator
     */
    toggleIndicator(indicator, params = {}) {
        // Check if indicator already exists
        if (this.indicators[indicator]) {
            // Remove indicator
            this.chart.removeSeries(this.indicators[indicator]);
            delete this.indicators[indicator];
        } else {
            // Add indicator
            this.loadData(this.currentSymbol, this.currentTimeframe, [indicator]);
        }
    }

    /**
     * Change timeframe
     */
    changeTimeframe(timeframe) {
        if (this.currentSymbol) {
            this.loadData(this.currentSymbol, timeframe, Object.keys(this.indicators));
        }
    }

    /**
     * Parse time string to timestamp
     */
    parseTime(timeStr) {
        const date = new Date(timeStr);
        return Math.floor(date.getTime() / 1000);
    }

    /**
     * Handle window resize
     */
    handleResize() {
        if (this.chart) {
            const container = document.getElementById(this.containerId);
            if (container) {
                this.chart.applyOptions({
                    width: container.clientWidth
                });
            }
        }
    }

    /**
     * Show loading indicator
     */
    showLoading() {
        const loader = document.getElementById('chart-loading');
        if (loader) {
            loader.style.display = 'flex';
        }
    }

    /**
     * Hide loading indicator
     */
    hideLoading() {
        const loader = document.getElementById('chart-loading');
        if (loader) {
            loader.style.display = 'none';
        }
    }

    /**
     * Destroy chart
     */
    destroy() {
        if (this.chart) {
            this.chart.remove();
            this.chart = null;
        }
        window.removeEventListener('resize', () => this.handleResize());
    }
}

// Global instance
window.PriceChart = PriceChart;
