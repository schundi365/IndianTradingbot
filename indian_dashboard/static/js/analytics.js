/**
 * Analytics Dashboard Controller
 * Manages analytics data fetching and chart rendering
 */

class AnalyticsDashboard {
    constructor() {
        this.charts = {};
        this.dateRange = {
            from: null,
            to: null
        };
        this.refreshInterval = null;
        this.isLoading = false;
    }

    /**
     * Initialize analytics dashboard
     */
    async init() {
        console.log('Initializing Analytics Dashboard...');
        
        // Setup date range controls
        this.setupDateRangeControls();
        
        // Load initial data
        await this.loadAllAnalytics();
        
        // Setup auto-refresh (every 30 seconds)
        this.startAutoRefresh();
        
        console.log('Analytics Dashboard initialized');
    }

    /**
     * Setup date range controls
     */
    setupDateRangeControls() {
        const fromDateInput = document.getElementById('analytics-from-date');
        const toDateInput = document.getElementById('analytics-to-date');
        const applyBtn = document.getElementById('analytics-apply-date');
        const resetBtn = document.getElementById('analytics-reset-date');
        
        // Set default dates (last 7 days)
        const today = new Date();
        const weekAgo = new Date(today);
        weekAgo.setDate(weekAgo.getDate() - 7);
        
        if (toDateInput) {
            toDateInput.valueAsDate = today;
            this.dateRange.to = this.formatDate(today);
        }
        
        if (fromDateInput) {
            fromDateInput.valueAsDate = weekAgo;
            this.dateRange.from = this.formatDate(weekAgo);
        }
        
        // Apply button
        if (applyBtn) {
            applyBtn.addEventListener('click', () => {
                if (fromDateInput) this.dateRange.from = fromDateInput.value;
                if (toDateInput) this.dateRange.to = toDateInput.value;
                this.loadAllAnalytics();
            });
        }
        
        // Reset button
        if (resetBtn) {
            resetBtn.addEventListener('click', () => {
                this.dateRange.from = null;
                this.dateRange.to = null;
                if (fromDateInput) fromDateInput.value = '';
                if (toDateInput) toDateInput.value = '';
                this.loadAllAnalytics();
            });
        }
        
        // Quick filters
        this.setupQuickFilters();
    }

    /**
     * Setup quick date filter buttons
     */
    setupQuickFilters() {
        const todayBtn = document.getElementById('analytics-filter-today');
        const weekBtn = document.getElementById('analytics-filter-week');
        const monthBtn = document.getElementById('analytics-filter-month');
        
        if (todayBtn) {
            todayBtn.addEventListener('click', () => this.applyQuickFilter('today'));
        }
        
        if (weekBtn) {
            weekBtn.addEventListener('click', () => this.applyQuickFilter('week'));
        }
        
        if (monthBtn) {
            monthBtn.addEventListener('click', () => this.applyQuickFilter('month'));
        }
    }

    /**
     * Apply quick date filter
     */
    applyQuickFilter(period) {
        const today = new Date();
        const fromDate = new Date(today);
        
        switch (period) {
            case 'today':
                fromDate.setHours(0, 0, 0, 0);
                break;
            case 'week':
                fromDate.setDate(fromDate.getDate() - 7);
                break;
            case 'month':
                fromDate.setMonth(fromDate.getMonth() - 1);
                break;
        }
        
        this.dateRange.from = this.formatDate(fromDate);
        this.dateRange.to = this.formatDate(today);
        
        // Update inputs
        const fromInput = document.getElementById('analytics-from-date');
        const toInput = document.getElementById('analytics-to-date');
        
        if (fromInput) fromInput.value = this.dateRange.from;
        if (toInput) toInput.value = this.dateRange.to;
        
        this.loadAllAnalytics();
    }

    /**
     * Load all analytics data
     */
    async loadAllAnalytics() {
        if (this.isLoading) return;
        
        this.isLoading = true;
        this.showLoading();
        
        try {
            // Load all analytics in parallel
            await Promise.all([
                this.loadPerformanceMetrics(),
                this.loadProfitBySymbol(),
                this.loadWinLossBySymbol(),
                this.loadDailyProfit(),
                this.loadHourlyPerformance(),
                this.loadTradeDistribution()
            ]);
            
            this.hideLoading();
        } catch (error) {
            console.error('Error loading analytics:', error);
            this.hideLoading();
            showNotification('Error loading analytics data', 'error');
        } finally {
            this.isLoading = false;
        }
    }

    /**
     * Load performance metrics
     */
    async loadPerformanceMetrics() {
        try {
            const url = this.buildUrl('/api/analytics/performance');
            const response = await fetch(url);
            const data = await response.json();
            
            if (data.success) {
                this.updatePerformanceMetrics(data.metrics);
            }
        } catch (error) {
            console.error('Error loading performance metrics:', error);
        }
    }

    /**
     * Update performance metrics display
     */
    updatePerformanceMetrics(metrics) {
        // Update metric cards
        this.updateElement('metric-total-trades', metrics.total_trades);
        this.updateElement('metric-win-rate', `${metrics.win_rate}%`);
        this.updateElement('metric-total-pnl', `₹${this.formatNumber(metrics.total_pnl)}`);
        this.updateElement('metric-avg-trade', `₹${this.formatNumber(metrics.avg_trade)}`);
        this.updateElement('metric-profit-factor', metrics.profit_factor);
        this.updateElement('metric-largest-win', `₹${this.formatNumber(metrics.largest_win)}`);
        this.updateElement('metric-largest-loss', `₹${this.formatNumber(metrics.largest_loss)}`);
        
        // Color code P&L
        const pnlElement = document.getElementById('metric-total-pnl');
        if (pnlElement) {
            pnlElement.style.color = metrics.total_pnl >= 0 ? '#0ECB81' : '#F6465D';
        }
    }

    /**
     * Load profit by symbol data
     */
    async loadProfitBySymbol() {
        try {
            const url = this.buildUrl('/api/analytics/profit-by-symbol');
            const response = await fetch(url);
            const data = await response.json();
            
            if (data.success && window.ProfitBySymbolChart) {
                window.ProfitBySymbolChart.render(data.data);
            }
        } catch (error) {
            console.error('Error loading profit by symbol:', error);
        }
    }

    /**
     * Load win/loss by symbol data
     */
    async loadWinLossBySymbol() {
        try {
            const url = this.buildUrl('/api/analytics/win-loss-by-symbol');
            const response = await fetch(url);
            const data = await response.json();
            
            if (data.success && window.WinLossChart) {
                window.WinLossChart.render(data.data);
            }
        } catch (error) {
            console.error('Error loading win/loss by symbol:', error);
        }
    }

    /**
     * Load daily profit data
     */
    async loadDailyProfit() {
        try {
            const url = this.buildUrl('/api/analytics/daily-profit');
            const response = await fetch(url);
            const data = await response.json();
            
            if (data.success && window.DailyProfitChart) {
                window.DailyProfitChart.render(data.data);
            }
        } catch (error) {
            console.error('Error loading daily profit:', error);
        }
    }

    /**
     * Load hourly performance data
     */
    async loadHourlyPerformance() {
        try {
            const url = this.buildUrl('/api/analytics/hourly-performance');
            const response = await fetch(url);
            const data = await response.json();
            
            if (data.success && window.HourlyPerformanceChart) {
                window.HourlyPerformanceChart.render(data.data);
            }
        } catch (error) {
            console.error('Error loading hourly performance:', error);
        }
    }

    /**
     * Load trade distribution data
     */
    async loadTradeDistribution() {
        try {
            const url = this.buildUrl('/api/analytics/trade-distribution');
            const response = await fetch(url);
            const data = await response.json();
            
            if (data.success && window.TradeDistributionChart) {
                window.TradeDistributionChart.render(data.data);
            }
        } catch (error) {
            console.error('Error loading trade distribution:', error);
        }
    }

    /**
     * Build URL with date range parameters
     */
    buildUrl(endpoint) {
        const params = new URLSearchParams();
        
        if (this.dateRange.from) {
            params.append('from_date', this.dateRange.from);
        }
        
        if (this.dateRange.to) {
            params.append('to_date', this.dateRange.to);
        }
        
        return params.toString() ? `${endpoint}?${params.toString()}` : endpoint;
    }

    /**
     * Start auto-refresh
     */
    startAutoRefresh() {
        // Refresh every 30 seconds
        this.refreshInterval = setInterval(() => {
            this.loadAllAnalytics();
        }, 30000);
    }

    /**
     * Stop auto-refresh
     */
    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }

    /**
     * Show loading indicator
     */
    showLoading() {
        const loader = document.getElementById('analytics-loading');
        if (loader) {
            loader.style.display = 'flex';
        }
    }

    /**
     * Hide loading indicator
     */
    hideLoading() {
        const loader = document.getElementById('analytics-loading');
        if (loader) {
            loader.style.display = 'none';
        }
    }

    /**
     * Update element text content
     */
    updateElement(id, value) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    }

    /**
     * Format date to YYYY-MM-DD
     */
    formatDate(date) {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    }

    /**
     * Format number with commas
     */
    formatNumber(num) {
        return Number(num).toLocaleString('en-IN', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
    }

    /**
     * Destroy analytics dashboard
     */
    destroy() {
        this.stopAutoRefresh();
        
        // Destroy all charts
        Object.values(this.charts).forEach(chart => {
            if (chart && chart.destroy) {
                chart.destroy();
            }
        });
        
        this.charts = {};
    }
}

// Global instance
let analyticsDashboard = null;

// Initialize when Analytics tab is shown
document.addEventListener('DOMContentLoaded', () => {
    // Listen for tab changes
    const analyticsTab = document.querySelector('[data-tab="analytics"]');
    
    if (analyticsTab) {
        analyticsTab.addEventListener('click', () => {
            // Initialize analytics dashboard if not already done
            if (!analyticsDashboard) {
                analyticsDashboard = new AnalyticsDashboard();
                
                // Wait for tab content to be visible
                setTimeout(() => {
                    analyticsDashboard.init();
                }, 100);
            }
        });
    }
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (analyticsDashboard) {
        analyticsDashboard.destroy();
    }
});
