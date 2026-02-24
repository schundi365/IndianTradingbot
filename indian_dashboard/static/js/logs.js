/**
 * Log Viewer component for Indian Market Trading Dashboard
 */

class LogViewer {
    constructor() {
        this.currentPage = 1;
        this.limit = 100;
        this.elements = {
            tab: document.getElementById('logs-tab'),
            tbody: document.getElementById('logs-tbody'),
            levelFilter: document.getElementById('log-level-filter'),
            search: document.getElementById('log-search'),
            globalLevel: document.getElementById('log-global-level'),
            refreshBtn: document.getElementById('logs-refresh-btn'),
            downloadBtn: document.getElementById('logs-download-btn'),
            clearBtn: document.getElementById('logs-clear-btn'),
            applyGlobalBtn: document.getElementById('apply-global-level-btn'),
            prevPage: document.getElementById('logs-prev-page'),
            nextPage: document.getElementById('logs-next-page'),
            pageInfo: document.getElementById('logs-page-info'),
            loading: document.getElementById('logs-loading')
        };

        this.init();
    }

    init() {
        if (!this.elements.tab) return;

        // Event listeners
        this.elements.refreshBtn.addEventListener('click', () => this.loadLogs(1));
        this.elements.levelFilter.addEventListener('change', () => this.loadLogs(1));
        this.elements.search.addEventListener('input', debounce(() => this.loadLogs(1), 500));

        this.elements.prevPage.addEventListener('click', () => {
            if (this.currentPage > 1) this.loadLogs(this.currentPage - 1);
        });

        this.elements.nextPage.addEventListener('click', () => {
            this.loadLogs(this.currentPage + 1);
        });

        this.elements.applyGlobalBtn.addEventListener('click', () => this.setGlobalLogLevel());
        this.elements.clearBtn.addEventListener('click', () => this.clearLogs());
        this.elements.downloadBtn.addEventListener('click', () => this.downloadLogs());
    }

    async loadLogs(page = 1) {
        this.currentPage = page;
        const offset = (page - 1) * this.limit;

        const params = {
            limit: this.limit,
            offset: offset,
            level: this.elements.levelFilter.value,
            search: this.elements.search.value
        };

        this.showLoading(true);
        try {
            const response = await api.getLogs(params);
            if (response.success) {
                this.renderLogs(response.logs);
                this.updatePagination(response.total);
            }
        } catch (error) {
            console.error('Error loading logs:', error);
        } finally {
            this.showLoading(false);
        }
    }

    renderLogs(logs) {
        this.elements.tbody.innerHTML = '';

        if (logs.length === 0) {
            this.elements.tbody.innerHTML = '<tr><td colspan="5" class="text-center">No logs found</td></tr>';
            return;
        }

        logs.forEach(log => {
            const tr = document.createElement('tr');
            tr.className = `log-row log-${log.level.toLowerCase()}`;

            // Format timestamp (take only the date/time part from ISO string)
            const date = new Date(log.timestamp);
            const formattedTime = date.toLocaleString();

            tr.innerHTML = `
                <td class="log-timestamp">${formattedTime}</td>
                <td class="log-level"><span class="badge badge-${log.level.toLowerCase()}">${log.level}</span></td>
                <td class="log-logger">${log.logger_name}</td>
                <td class="log-message">${this.escapeHtml(log.message)}</td>
                <td class="log-symbol">${log.symbol || '-'}</td>
            `;
            this.elements.tbody.appendChild(tr);
        });
    }

    updatePagination(total) {
        const totalPages = Math.ceil(total / this.limit) || 1;
        this.elements.pageInfo.innerText = `Page ${this.currentPage} of ${totalPages} (${total} logs)`;

        this.elements.prevPage.disabled = this.currentPage <= 1;
        this.elements.nextPage.disabled = this.currentPage >= totalPages;
    }

    async setGlobalLogLevel() {
        const level = this.elements.globalLevel.value;
        try {
            const response = await api.setLogLevel(level);
            if (response.success) {
                if (window.ui && window.ui.showNotification) {
                    window.ui.showNotification(`Bot logging level set to ${level}`, 'success');
                } else {
                    alert(`Bot logging level set to ${level}`);
                }
            }
        } catch (error) {
            console.error('Error setting global log level:', error);
        }
    }

    async clearLogs() {
        if (!confirm('Are you sure you want to clear the entire log database? This cannot be undone.')) {
            return;
        }

        try {
            const response = await api.clearLogs();
            if (response.success) {
                this.loadLogs(1);
                if (window.ui && window.ui.showNotification) {
                    window.ui.showNotification('Logs cleared successfully', 'success');
                }
            }
        } catch (error) {
            console.error('Error clearing logs:', error);
        }
    }

    downloadLogs() {
        const params = {
            level: this.elements.levelFilter.value,
            search: this.elements.search.value
        };
        const url = api.getDownloadLogsUrl(params);
        window.location.href = url;
    }

    showLoading(show) {
        this.elements.loading.style.display = show ? 'flex' : 'none';
        if (show) this.elements.tbody.style.opacity = '0.5';
        else this.elements.tbody.style.opacity = '1';
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Global instance
window.logViewer = new LogViewer();
