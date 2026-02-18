/**
 * Trade History Module
 * Handles trade history table with sorting and pagination
 */

const TradeHistory = {
    // State
    allTrades: [],
    filteredTrades: [],
    currentPage: 1,
    itemsPerPage: 20,
    sortColumn: 'timestamp',
    sortDirection: 'desc',
    
    /**
     * Initialize trade history module
     */
    init() {
        this.setupEventListeners();
        this.setupSorting();
        this.setupPagination();
    },
    
    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Filter button
        const filterBtn = document.getElementById('filter-trades-btn');
        if (filterBtn) {
            filterBtn.addEventListener('click', () => this.loadTrades());
        }
        
        // Date inputs - load trades when dates change
        const fromDate = document.getElementById('from-date');
        const toDate = document.getElementById('to-date');
        
        if (fromDate) {
            fromDate.addEventListener('change', () => this.loadTrades());
        }
        
        if (toDate) {
            toDate.addEventListener('change', () => this.loadTrades());
        }
        
        // Quick filter buttons
        const todayBtn = document.getElementById('filter-today-btn');
        const weekBtn = document.getElementById('filter-week-btn');
        const monthBtn = document.getElementById('filter-month-btn');
        const clearBtn = document.getElementById('filter-clear-btn');
        
        if (todayBtn) {
            todayBtn.addEventListener('click', () => this.applyQuickFilter('today'));
        }
        
        if (weekBtn) {
            weekBtn.addEventListener('click', () => this.applyQuickFilter('week'));
        }
        
        if (monthBtn) {
            monthBtn.addEventListener('click', () => this.applyQuickFilter('month'));
        }
        
        if (clearBtn) {
            clearBtn.addEventListener('click', () => this.clearDateFilter());
        }
    },
    
    /**
     * Apply quick filter (Today, Week, Month)
     */
    applyQuickFilter(period) {
        const today = new Date();
        const fromDate = new Date();
        
        // Calculate from date based on period
        switch (period) {
            case 'today':
                // From today 00:00:00
                fromDate.setHours(0, 0, 0, 0);
                break;
            case 'week':
                // From 7 days ago
                fromDate.setDate(today.getDate() - 7);
                break;
            case 'month':
                // From 30 days ago
                fromDate.setDate(today.getDate() - 30);
                break;
        }
        
        // Format dates as YYYY-MM-DD
        const fromDateStr = this.formatDate(fromDate);
        const toDateStr = this.formatDate(today);
        
        // Set date inputs
        const fromDateInput = document.getElementById('from-date');
        const toDateInput = document.getElementById('to-date');
        
        if (fromDateInput) {
            fromDateInput.value = fromDateStr;
        }
        
        if (toDateInput) {
            toDateInput.value = toDateStr;
        }
        
        // Load trades with new filter
        this.loadTrades();
    },
    
    /**
     * Clear date filter
     */
    clearDateFilter() {
        const fromDateInput = document.getElementById('from-date');
        const toDateInput = document.getElementById('to-date');
        
        if (fromDateInput) {
            fromDateInput.value = '';
        }
        
        if (toDateInput) {
            toDateInput.value = '';
        }
        
        // Load all trades
        this.loadTrades();
    },
    
    /**
     * Format date as YYYY-MM-DD
     */
    formatDate(date) {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    },
    
    /**
     * Setup sorting functionality
     */
    setupSorting() {
        const headers = document.querySelectorAll('#trades-table th.sortable');
        
        headers.forEach(header => {
            header.addEventListener('click', () => {
                const column = header.dataset.sort;
                this.sortBy(column);
            });
        });
    },
    
    /**
     * Setup pagination controls
     */
    setupPagination() {
        const prevBtn = document.getElementById('trades-prev-page');
        const nextBtn = document.getElementById('trades-next-page');
        
        if (prevBtn) {
            prevBtn.addEventListener('click', () => this.previousPage());
        }
        
        if (nextBtn) {
            nextBtn.addEventListener('click', () => this.nextPage());
        }
    },
    
    /**
     * Load trades from API
     */
    async loadTrades() {
        const fromDate = document.getElementById('from-date').value;
        const toDate = document.getElementById('to-date').value;
        
        try {
            // Show loading state
            this.showLoading(true);
            
            const response = await api.getTrades(fromDate, toDate);
            
            // Store all trades
            this.allTrades = response.trades || [];
            this.filteredTrades = [...this.allTrades];
            
            // Reset to first page
            this.currentPage = 1;
            
            // Apply current sort
            this.applySorting();
            
            // Calculate and display statistics
            this.updateStatistics();
            
            // Render table
            this.renderTable();
            
            // Update pagination
            this.updatePagination();
            
        } catch (error) {
            notifications.error('Failed to load trades: ' + error.message);
            this.showEmptyState('Error loading trades');
            this.clearStatistics();
        } finally {
            this.showLoading(false);
        }
    },
    
    /**
     * Sort trades by column
     */
    sortBy(column) {
        // Toggle direction if same column
        if (this.sortColumn === column) {
            this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
        } else {
            this.sortColumn = column;
            this.sortDirection = 'desc'; // Default to descending for new column
        }
        
        // Update sort icons
        this.updateSortIcons();
        
        // Apply sorting
        this.applySorting();
        
        // Reset to first page
        this.currentPage = 1;
        
        // Re-render table
        this.renderTable();
        this.updatePagination();
    },
    
    /**
     * Apply current sorting to filtered trades
     */
    applySorting() {
        this.filteredTrades.sort((a, b) => {
            let aVal = a[this.sortColumn];
            let bVal = b[this.sortColumn];
            
            // Handle different data types
            if (this.sortColumn === 'timestamp') {
                aVal = new Date(aVal).getTime();
                bVal = new Date(bVal).getTime();
            } else if (typeof aVal === 'string') {
                aVal = aVal.toLowerCase();
                bVal = bVal.toLowerCase();
            } else if (typeof aVal === 'number') {
                // Numbers are already comparable
            }
            
            // Compare
            if (aVal < bVal) {
                return this.sortDirection === 'asc' ? -1 : 1;
            }
            if (aVal > bVal) {
                return this.sortDirection === 'asc' ? 1 : -1;
            }
            return 0;
        });
    },
    
    /**
     * Update sort icons in table headers
     */
    updateSortIcons() {
        const headers = document.querySelectorAll('#trades-table th.sortable');
        
        headers.forEach(header => {
            const icon = header.querySelector('.sort-icon');
            if (!icon) return;
            
            const column = header.dataset.sort;
            
            if (column === this.sortColumn) {
                icon.textContent = this.sortDirection === 'asc' ? '▲' : '▼';
                icon.style.opacity = '1';
            } else {
                icon.textContent = '▼';
                icon.style.opacity = '0.3';
            }
        });
    },
    
    /**
     * Render trade table
     */
    renderTable() {
        const tbody = document.getElementById('trades-tbody');
        
        if (!tbody) return;
        
        // Clear table
        tbody.innerHTML = '';
        
        // Check if no trades
        if (this.filteredTrades.length === 0) {
            this.showEmptyState('No trades found');
            return;
        }
        
        // Calculate pagination
        const start = (this.currentPage - 1) * this.itemsPerPage;
        const end = start + this.itemsPerPage;
        const pageTrades = this.filteredTrades.slice(start, end);
        
        // Render rows
        pageTrades.forEach(trade => {
            const row = this.createTradeRow(trade);
            tbody.appendChild(row);
        });
    },
    
    /**
     * Create a trade row element
     */
    createTradeRow(trade) {
        const row = document.createElement('tr');
        
        // Format date
        const date = formatters.datetime(trade.timestamp || trade.order_timestamp);
        
        // Get trade type
        const type = trade.transaction_type || trade.order_type || '--';
        
        // Format prices
        const entryPrice = trade.price || trade.average_price || 0;
        const exitPrice = trade.exit_price || 0;
        
        // Calculate P&L
        let pnl = 0;
        let pnlClass = '';
        let pnlDisplay = '--';
        
        if (trade.pnl !== undefined) {
            pnl = trade.pnl;
        } else if (exitPrice > 0 && entryPrice > 0) {
            // Calculate P&L based on entry and exit
            const quantity = trade.quantity || 0;
            if (type.toUpperCase() === 'BUY' || type.toUpperCase() === 'LONG') {
                pnl = (exitPrice - entryPrice) * quantity;
            } else {
                pnl = (entryPrice - exitPrice) * quantity;
            }
        }
        
        // Format P&L display
        if (pnl !== 0 || trade.pnl !== undefined) {
            pnlClass = pnl >= 0 ? 'positive' : 'negative';
            pnlDisplay = formatters.currency(pnl);
        }
        
        // Create row HTML
        row.innerHTML = `
            <td>${date}</td>
            <td>${trade.symbol || '--'}</td>
            <td><span class="trade-type ${type.toLowerCase()}">${type}</span></td>
            <td>${trade.quantity || 0}</td>
            <td>${formatters.currency(entryPrice)}</td>
            <td>${exitPrice > 0 ? formatters.currency(exitPrice) : '--'}</td>
            <td><span class="pnl ${pnlClass}">${pnlDisplay}</span></td>
        `;
        
        return row;
    },
    
    /**
     * Show empty state message
     */
    showEmptyState(message) {
        const tbody = document.getElementById('trades-tbody');
        if (!tbody) return;
        
        tbody.innerHTML = `
            <tr>
                <td colspan="7" style="text-align: center; padding: 2rem; color: var(--text-muted);">
                    ${message}
                </td>
            </tr>
        `;
    },
    
    /**
     * Show/hide loading state
     */
    showLoading(show) {
        const tbody = document.getElementById('trades-tbody');
        if (!tbody) return;
        
        if (show) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="7" style="text-align: center; padding: 2rem;">
                        <div class="spinner"></div>
                        <p style="margin-top: 1rem; color: var(--text-muted);">Loading trades...</p>
                    </td>
                </tr>
            `;
        }
    },
    
    /**
     * Update pagination controls
     */
    updatePagination() {
        const totalPages = Math.ceil(this.filteredTrades.length / this.itemsPerPage);
        
        // Update page info
        const pageInfo = document.getElementById('trades-page-info');
        if (pageInfo) {
            pageInfo.textContent = `Page ${this.currentPage} of ${totalPages || 1}`;
        }
        
        // Update buttons
        const prevBtn = document.getElementById('trades-prev-page');
        const nextBtn = document.getElementById('trades-next-page');
        
        if (prevBtn) {
            prevBtn.disabled = this.currentPage === 1;
        }
        
        if (nextBtn) {
            nextBtn.disabled = this.currentPage >= totalPages;
        }
        
        // Show/hide pagination if only one page
        const paginationContainer = document.querySelector('#trades-tab .pagination');
        if (paginationContainer) {
            paginationContainer.style.display = totalPages <= 1 ? 'none' : 'flex';
        }
    },
    
    /**
     * Go to previous page
     */
    previousPage() {
        if (this.currentPage > 1) {
            this.currentPage--;
            this.renderTable();
            this.updatePagination();
        }
    },
    
    /**
     * Go to next page
     */
    nextPage() {
        const totalPages = Math.ceil(this.filteredTrades.length / this.itemsPerPage);
        if (this.currentPage < totalPages) {
            this.currentPage++;
            this.renderTable();
            this.updatePagination();
        }
    },
    
    /**
     * Calculate and update trade statistics
     */
    updateStatistics() {
        const stats = this.calculateStatistics(this.filteredTrades);
        this.displayStatistics(stats);
    },
    
    /**
     * Calculate statistics from trades
     */
    calculateStatistics(trades) {
        if (!trades || trades.length === 0) {
            return {
                totalTrades: 0,
                winRate: 0,
                totalPnL: 0,
                avgPnL: 0
            };
        }
        
        let totalPnL = 0;
        let winningTrades = 0;
        let completedTrades = 0;
        
        trades.forEach(trade => {
            let pnl = 0;
            
            // Get P&L from trade
            if (trade.pnl !== undefined && trade.pnl !== null) {
                pnl = trade.pnl;
                completedTrades++;
            } else if (trade.exit_price && trade.price) {
                // Calculate P&L if we have entry and exit prices
                const entryPrice = trade.price || trade.average_price || 0;
                const exitPrice = trade.exit_price || 0;
                const quantity = trade.quantity || 0;
                const type = (trade.transaction_type || trade.order_type || '').toUpperCase();
                
                if (exitPrice > 0 && entryPrice > 0 && quantity > 0) {
                    if (type === 'BUY' || type === 'LONG') {
                        pnl = (exitPrice - entryPrice) * quantity;
                    } else if (type === 'SELL' || type === 'SHORT') {
                        pnl = (entryPrice - exitPrice) * quantity;
                    }
                    completedTrades++;
                }
            }
            
            // Add to totals
            totalPnL += pnl;
            
            // Count winning trades
            if (pnl > 0) {
                winningTrades++;
            }
        });
        
        // Calculate win rate (only for completed trades)
        const winRate = completedTrades > 0 ? (winningTrades / completedTrades) * 100 : 0;
        
        // Calculate average P&L per trade
        const avgPnL = completedTrades > 0 ? totalPnL / completedTrades : 0;
        
        return {
            totalTrades: trades.length,
            winRate: winRate,
            totalPnL: totalPnL,
            avgPnL: avgPnL
        };
    },
    
    /**
     * Display statistics in the UI
     */
    displayStatistics(stats) {
        // Total trades
        const totalTradesEl = document.getElementById('stat-total-trades');
        if (totalTradesEl) {
            totalTradesEl.textContent = stats.totalTrades;
        }
        
        // Win rate
        const winRateEl = document.getElementById('stat-win-rate');
        if (winRateEl) {
            winRateEl.textContent = stats.winRate.toFixed(1) + '%';
            // Color code win rate
            if (stats.winRate >= 50) {
                winRateEl.classList.add('positive');
                winRateEl.classList.remove('negative');
            } else if (stats.winRate > 0) {
                winRateEl.classList.remove('positive', 'negative');
            }
        }
        
        // Total P&L
        const totalPnLEl = document.getElementById('stat-total-pnl');
        if (totalPnLEl) {
            totalPnLEl.textContent = formatters.currency(stats.totalPnL);
            // Color code P&L
            if (stats.totalPnL > 0) {
                totalPnLEl.classList.add('positive');
                totalPnLEl.classList.remove('negative');
            } else if (stats.totalPnL < 0) {
                totalPnLEl.classList.add('negative');
                totalPnLEl.classList.remove('positive');
            } else {
                totalPnLEl.classList.remove('positive', 'negative');
            }
        }
        
        // Average P&L per trade
        const avgPnLEl = document.getElementById('stat-avg-pnl');
        if (avgPnLEl) {
            avgPnLEl.textContent = formatters.currency(stats.avgPnL);
            // Color code average P&L
            if (stats.avgPnL > 0) {
                avgPnLEl.classList.add('positive');
                avgPnLEl.classList.remove('negative');
            } else if (stats.avgPnL < 0) {
                avgPnLEl.classList.add('negative');
                avgPnLEl.classList.remove('positive');
            } else {
                avgPnLEl.classList.remove('positive', 'negative');
            }
        }
    },
    
    /**
     * Clear statistics display
     */
    clearStatistics() {
        this.displayStatistics({
            totalTrades: 0,
            winRate: 0,
            totalPnL: 0,
            avgPnL: 0
        });
    },
    
    /**
     * Export trades to CSV
     */
    exportToCSV() {
        if (!this.filteredTrades || this.filteredTrades.length === 0) {
            notifications.warning('No trades to export');
            return;
        }
        
        try {
            // Create CSV header
            const headers = ['Date', 'Symbol', 'Type', 'Quantity', 'Entry Price', 'Exit Price', 'P&L'];
            
            // Create CSV rows
            const rows = this.filteredTrades.map(trade => {
                const date = trade.timestamp || trade.order_timestamp || '';
                const symbol = trade.symbol || '';
                const type = trade.transaction_type || trade.order_type || '';
                const quantity = trade.quantity || 0;
                const entryPrice = trade.price || trade.average_price || 0;
                const exitPrice = trade.exit_price || 0;
                
                // Calculate P&L
                let pnl = 0;
                if (trade.pnl !== undefined) {
                    pnl = trade.pnl;
                } else if (exitPrice > 0 && entryPrice > 0) {
                    const qty = trade.quantity || 0;
                    if (type.toUpperCase() === 'BUY' || type.toUpperCase() === 'LONG') {
                        pnl = (exitPrice - entryPrice) * qty;
                    } else {
                        pnl = (entryPrice - exitPrice) * qty;
                    }
                }
                
                return [
                    date,
                    symbol,
                    type,
                    quantity,
                    entryPrice.toFixed(2),
                    exitPrice > 0 ? exitPrice.toFixed(2) : '',
                    pnl.toFixed(2)
                ];
            });
            
            // Combine headers and rows
            const csvContent = [
                headers.join(','),
                ...rows.map(row => row.map(cell => this.escapeCSVCell(cell)).join(','))
            ].join('\n');
            
            // Create blob and download
            const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
            const filename = `trades_${this.getExportFilename()}.csv`;
            this.downloadFile(blob, filename);
            
            notifications.success(`Exported ${this.filteredTrades.length} trades to CSV`);
        } catch (error) {
            notifications.error('Failed to export CSV: ' + error.message);
        }
    },
    
    /**
     * Export trades to Excel (XLSX format)
     */
    exportToExcel() {
        if (!this.filteredTrades || this.filteredTrades.length === 0) {
            notifications.warning('No trades to export');
            return;
        }
        
        try {
            // Create workbook data
            const headers = ['Date', 'Symbol', 'Type', 'Quantity', 'Entry Price', 'Exit Price', 'P&L'];
            
            const rows = this.filteredTrades.map(trade => {
                const date = trade.timestamp || trade.order_timestamp || '';
                const symbol = trade.symbol || '';
                const type = trade.transaction_type || trade.order_type || '';
                const quantity = trade.quantity || 0;
                const entryPrice = trade.price || trade.average_price || 0;
                const exitPrice = trade.exit_price || 0;
                
                // Calculate P&L
                let pnl = 0;
                if (trade.pnl !== undefined) {
                    pnl = trade.pnl;
                } else if (exitPrice > 0 && entryPrice > 0) {
                    const qty = trade.quantity || 0;
                    if (type.toUpperCase() === 'BUY' || type.toUpperCase() === 'LONG') {
                        pnl = (exitPrice - entryPrice) * qty;
                    } else {
                        pnl = (entryPrice - exitPrice) * qty;
                    }
                }
                
                return [
                    date,
                    symbol,
                    type,
                    quantity,
                    entryPrice,
                    exitPrice > 0 ? exitPrice : '',
                    pnl
                ];
            });
            
            // Create XML content for Excel
            const xmlContent = this.createExcelXML(headers, rows);
            
            // Create blob and download
            const blob = new Blob([xmlContent], { type: 'application/vnd.ms-excel' });
            const filename = `trades_${this.getExportFilename()}.xls`;
            this.downloadFile(blob, filename);
            
            notifications.success(`Exported ${this.filteredTrades.length} trades to Excel`);
        } catch (error) {
            notifications.error('Failed to export Excel: ' + error.message);
        }
    },
    
    /**
     * Escape CSV cell content
     */
    escapeCSVCell(cell) {
        if (cell === null || cell === undefined) {
            return '';
        }
        
        const str = String(cell);
        
        // If cell contains comma, quote, or newline, wrap in quotes and escape quotes
        if (str.includes(',') || str.includes('"') || str.includes('\n')) {
            return `"${str.replace(/"/g, '""')}"`;
        }
        
        return str;
    },
    
    /**
     * Create Excel XML content
     */
    createExcelXML(headers, rows) {
        let xml = '<?xml version="1.0"?>\n';
        xml += '<?mso-application progid="Excel.Sheet"?>\n';
        xml += '<Workbook xmlns="urn:schemas-microsoft-com:office:spreadsheet"\n';
        xml += ' xmlns:ss="urn:schemas-microsoft-com:office:spreadsheet">\n';
        xml += '<Worksheet ss:Name="Trades">\n';
        xml += '<Table>\n';
        
        // Add header row
        xml += '<Row>\n';
        headers.forEach(header => {
            xml += `<Cell><Data ss:Type="String">${this.escapeXML(header)}</Data></Cell>\n`;
        });
        xml += '</Row>\n';
        
        // Add data rows
        rows.forEach(row => {
            xml += '<Row>\n';
            row.forEach((cell, index) => {
                // Determine cell type
                let type = 'String';
                let value = cell;
                
                // Numeric columns: Quantity, Entry Price, Exit Price, P&L
                if (index >= 3 && index <= 6 && cell !== '' && !isNaN(cell)) {
                    type = 'Number';
                    value = cell;
                } else {
                    value = this.escapeXML(String(cell));
                }
                
                xml += `<Cell><Data ss:Type="${type}">${value}</Data></Cell>\n`;
            });
            xml += '</Row>\n';
        });
        
        xml += '</Table>\n';
        xml += '</Worksheet>\n';
        xml += '</Workbook>\n';
        
        return xml;
    },
    
    /**
     * Escape XML special characters
     */
    escapeXML(str) {
        if (!str) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&apos;');
    },
    
    /**
     * Get filename for export (based on date range)
     */
    getExportFilename() {
        const fromDate = document.getElementById('from-date')?.value;
        const toDate = document.getElementById('to-date')?.value;
        
        if (fromDate && toDate) {
            return `${fromDate}_to_${toDate}`;
        } else if (fromDate) {
            return `from_${fromDate}`;
        } else if (toDate) {
            return `until_${toDate}`;
        } else {
            // Use current date
            const now = new Date();
            return this.formatDate(now);
        }
    },
    
    /**
     * Download file to user's computer
     */
    downloadFile(blob, filename) {
        // Create download link
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        
        link.href = url;
        link.download = filename;
        link.style.display = 'none';
        
        // Trigger download
        document.body.appendChild(link);
        link.click();
        
        // Cleanup
        setTimeout(() => {
            document.body.removeChild(link);
            URL.revokeObjectURL(url);
        }, 100);
    }
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TradeHistory;
}
