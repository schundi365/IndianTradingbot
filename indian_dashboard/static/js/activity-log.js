/**
 * Activity Log Component
 * Displays real-time bot activities in the dashboard
 */

class ActivityLog {
    constructor() {
        this.container = null;
        this.activities = [];
        this.refreshInterval = null;
        this.isAutoScroll = true;
        this.filterType = null;
    }

    /**
     * Initialize activity log
     */
    init() {
        this.container = document.getElementById('activity-log-container');
        if (!this.container) {
            console.error('Activity log container not found');
            return;
        }

        this.setupUI();
        this.startAutoRefresh();
    }

    /**
     * Setup UI elements
     */
    setupUI() {
        // Add filter buttons
        const filterBar = this.container.querySelector('.activity-filter-bar');
        if (filterBar) {
            filterBar.addEventListener('click', (e) => {
                if (e.target.classList.contains('filter-btn')) {
                    this.handleFilterClick(e.target);
                }
            });
        }

        // Add clear button handler
        const clearBtn = this.container.querySelector('.clear-activities-btn');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => this.clearActivities());
        }

        // Add auto-scroll toggle
        const logContent = this.container.querySelector('.activity-log-content');
        if (logContent) {
            logContent.addEventListener('scroll', () => {
                const isAtBottom = logContent.scrollHeight - logContent.scrollTop <= logContent.clientHeight + 50;
                this.isAutoScroll = isAtBottom;
            });
        }
    }

    /**
     * Handle filter button click
     */
    handleFilterClick(button) {
        const filterType = button.dataset.type;
        
        // Toggle filter
        if (this.filterType === filterType) {
            this.filterType = null;
            button.classList.remove('active');
        } else {
            // Remove active from all buttons
            this.container.querySelectorAll('.filter-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            
            this.filterType = filterType;
            button.classList.add('active');
        }

        // Refresh display
        this.fetchActivities();
    }

    /**
     * Start auto-refresh
     */
    startAutoRefresh() {
        // Initial fetch
        this.fetchActivities();

        // Refresh every 3 seconds
        this.refreshInterval = setInterval(() => {
            this.fetchActivities();
        }, 3000);
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
     * Fetch activities from API
     */
    async fetchActivities() {
        try {
            let url = '/api/bot/activities?limit=100';
            if (this.filterType) {
                url += `&type=${this.filterType}`;
            }

            const response = await fetch(url);
            const data = await response.json();

            if (data.success) {
                this.activities = data.activities || [];
                this.renderActivities();
            }
        } catch (error) {
            console.error('Error fetching activities:', error);
        }
    }

    /**
     * Render activities
     */
    renderActivities() {
        const logContent = this.container.querySelector('.activity-log-content');
        if (!logContent) return;

        if (this.activities.length === 0) {
            logContent.innerHTML = '<div class="no-activities">No activities yet. Start the bot to see live updates.</div>';
            return;
        }

        const html = this.activities.map(activity => this.renderActivity(activity)).join('');
        logContent.innerHTML = html;

        // Auto-scroll to bottom if enabled
        if (this.isAutoScroll) {
            logContent.scrollTop = logContent.scrollHeight;
        }

        // Update count
        const countElement = this.container.querySelector('.activity-count');
        if (countElement) {
            countElement.textContent = this.activities.length;
        }
    }

    /**
     * Render single activity
     */
    renderActivity(activity) {
        const icon = this.getActivityIcon(activity.type);
        const levelClass = this.getLevelClass(activity.level);
        const time = this.formatTime(activity.timestamp);
        const symbol = activity.symbol ? `<span class="activity-symbol">${activity.symbol}</span>` : '';

        return `
            <div class="activity-item ${levelClass}" data-type="${activity.type}">
                <div class="activity-icon">${icon}</div>
                <div class="activity-content">
                    <div class="activity-header">
                        <span class="activity-time">${time}</span>
                        ${symbol}
                        <span class="activity-type-badge">${activity.type}</span>
                    </div>
                    <div class="activity-message">${this.escapeHtml(activity.message)}</div>
                </div>
            </div>
        `;
    }

    /**
     * Get icon for activity type
     */
    getActivityIcon(type) {
        const icons = {
            'analysis': '📊',
            'signal': '⚡',
            'order': '✅',
            'position': '📈',
            'error': '❌',
            'warning': '⚠️'
        };
        return icons[type] || '📝';
    }

    /**
     * Get CSS class for level
     */
    getLevelClass(level) {
        return `activity-level-${level}`;
    }

    /**
     * Format timestamp
     */
    formatTime(timestamp) {
        const date = new Date(timestamp);
        const hours = date.getHours().toString().padStart(2, '0');
        const minutes = date.getMinutes().toString().padStart(2, '0');
        const seconds = date.getSeconds().toString().padStart(2, '0');
        return `${hours}:${minutes}:${seconds}`;
    }

    /**
     * Escape HTML to prevent XSS
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Clear all activities
     */
    async clearActivities() {
        try {
            const response = await fetch('/api/bot/activities/clear', {
                method: 'POST'
            });

            const data = await response.json();

            if (data.success) {
                this.activities = [];
                this.renderActivities();
                showNotification('Activities cleared', 'success');
            } else {
                showNotification('Failed to clear activities', 'error');
            }
        } catch (error) {
            console.error('Error clearing activities:', error);
            showNotification('Error clearing activities', 'error');
        }
    }

    /**
     * Destroy activity log
     */
    destroy() {
        this.stopAutoRefresh();
    }
}

// Global instance
let activityLog = null;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    activityLog = new ActivityLog();
    activityLog.init();
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (activityLog) {
        activityLog.destroy();
    }
});
