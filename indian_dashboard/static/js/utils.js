/**
 * Utility functions for Indian Market Trading Dashboard
 */

// Notification system
const notifications = {
    show(message, type = 'info', duration = 3000) {
        const container = document.getElementById('notification-container');
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        
        container.appendChild(notification);
        
        setTimeout(() => {
            notification.style.opacity = '0';
            setTimeout(() => notification.remove(), 300);
        }, duration);
    },
    
    success(message, duration) {
        this.show(message, 'success', duration);
    },
    
    error(message, duration) {
        this.show(message, 'error', duration);
    },
    
    info(message, duration) {
        this.show(message, 'info', duration);
    }
};

// Formatting helpers
const formatters = {
    currency(value, decimals = 2) {
        return `₹${parseFloat(value).toFixed(decimals).replace(/\B(?=(\d{3})+(?!\d))/g, ',')}`;
    },
    
    number(value, decimals = 2) {
        return parseFloat(value).toFixed(decimals);
    },
    
    percentage(value, decimals = 2) {
        return `${parseFloat(value).toFixed(decimals)}%`;
    },
    
    date(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-IN');
    },
    
    datetime(dateString) {
        const date = new Date(dateString);
        return date.toLocaleString('en-IN');
    },
    
    time(dateString) {
        const date = new Date(dateString);
        return date.toLocaleTimeString('en-IN');
    },
    
    uptime(seconds) {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;
        
        if (hours > 0) {
            return `${hours}h ${minutes}m ${secs}s`;
        } else if (minutes > 0) {
            return `${minutes}m ${secs}s`;
        } else {
            return `${secs}s`;
        }
    }
};

// Validation helpers
const validators = {
    required(value) {
        return value !== null && value !== undefined && value !== '';
    },
    
    number(value) {
        return !isNaN(parseFloat(value)) && isFinite(value);
    },
    
    positive(value) {
        return this.number(value) && parseFloat(value) > 0;
    },
    
    range(value, min, max) {
        return this.number(value) && parseFloat(value) >= min && parseFloat(value) <= max;
    },
    
    email(value) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(value);
    }
};

// DOM helpers
const dom = {
    show(element) {
        if (typeof element === 'string') {
            element = document.getElementById(element);
        }
        if (element) {
            element.style.display = 'block';
        }
    },
    
    hide(element) {
        if (typeof element === 'string') {
            element = document.getElementById(element);
        }
        if (element) {
            element.style.display = 'none';
        }
    },
    
    toggle(element) {
        if (typeof element === 'string') {
            element = document.getElementById(element);
        }
        if (element) {
            element.style.display = element.style.display === 'none' ? 'block' : 'none';
        }
    },
    
    addClass(element, className) {
        if (typeof element === 'string') {
            element = document.getElementById(element);
        }
        if (element) {
            element.classList.add(className);
        }
    },
    
    removeClass(element, className) {
        if (typeof element === 'string') {
            element = document.getElementById(element);
        }
        if (element) {
            element.classList.remove(className);
        }
    },
    
    toggleClass(element, className) {
        if (typeof element === 'string') {
            element = document.getElementById(element);
        }
        if (element) {
            element.classList.toggle(className);
        }
    }
};

// Debounce function
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Throttle function
function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Loading state helpers
const loading = {
    show(button) {
        if (typeof button === 'string') {
            button = document.getElementById(button);
        }
        if (button) {
            button.disabled = true;
            button.classList.add('loading');
            button.dataset.originalText = button.textContent;
        }
    },
    
    hide(button) {
        if (typeof button === 'string') {
            button = document.getElementById(button);
        }
        if (button) {
            button.disabled = false;
            button.classList.remove('loading');
            if (button.dataset.originalText) {
                button.textContent = button.dataset.originalText;
                delete button.dataset.originalText;
            }
        }
    }
};

// Export utilities
window.notifications = notifications;
window.formatters = formatters;
window.validators = validators;
window.dom = dom;
window.debounce = debounce;
window.throttle = throttle;
window.loading = loading;
