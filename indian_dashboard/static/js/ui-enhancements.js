/**
 * UI/UX Enhancements for Indian Market Trading Dashboard
 * Task 14.2: Keyboard Shortcuts, Accessibility, and Interactive Features
 */

// Keyboard Shortcuts Manager
const KeyboardShortcuts = {
    shortcuts: {
        // Tab navigation
        '1': { action: () => switchTab('broker'), description: 'Go to Broker tab' },
        '2': { action: () => switchTab('instruments'), description: 'Go to Instruments tab' },
        '3': { action: () => switchTab('configuration'), description: 'Go to Configuration tab' },
        '4': { action: () => switchTab('monitor'), description: 'Go to Monitor tab' },
        '5': { action: () => switchTab('trades'), description: 'Go to Trades tab' },
        
        // Actions
        's': { action: () => focusSearch(), description: 'Focus search input', ctrl: false },
        'r': { action: () => refreshCurrentTab(), description: 'Refresh current tab', ctrl: false },
        'h': { action: () => KeyboardShortcuts.showHelp(), description: 'Show keyboard shortcuts', shift: true },
        'Escape': { action: () => closeModals(), description: 'Close modals/dialogs' },
        
        // With modifiers
        's_ctrl': { action: () => saveConfiguration(), description: 'Save configuration', ctrl: true },
        'l_ctrl': { action: () => loadConfiguration(), description: 'Load configuration', ctrl: true },
        'e_ctrl': { action: () => exportConfiguration(), description: 'Export configuration', ctrl: true },
        'f_ctrl': { action: () => focusSearch(), description: 'Focus search', ctrl: true },
    },
    
    init() {
        document.addEventListener('keydown', (e) => this.handleKeyPress(e));
        this.addShortcutHints();
    },
    
    handleKeyPress(e) {
        // Don't trigger shortcuts when typing in inputs
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.tagName === 'SELECT') {
            // Allow Escape to blur inputs
            if (e.key === 'Escape') {
                e.target.blur();
                return;
            }
            // Allow Ctrl+S, Ctrl+L, Ctrl+E, Ctrl+F even in inputs
            if (!e.ctrlKey && !e.metaKey) {
                return;
            }
        }
        
        // Build shortcut key
        let shortcutKey = e.key.toLowerCase();
        if (e.ctrlKey || e.metaKey) {
            shortcutKey += '_ctrl';
        }
        if (e.shiftKey && !e.ctrlKey && !e.metaKey) {
            shortcutKey = e.key; // Keep original case for shift
        }
        
        const shortcut = this.shortcuts[shortcutKey];
        
        if (shortcut) {
            // Check if modifiers match
            const ctrlMatch = shortcut.ctrl === undefined || shortcut.ctrl === (e.ctrlKey || e.metaKey);
            const shiftMatch = shortcut.shift === undefined || shortcut.shift === e.shiftKey;
            
            if (ctrlMatch && shiftMatch) {
                e.preventDefault();
                shortcut.action();
            }
        }
    },
    
    addShortcutHints() {
        // Add hints to tab buttons
        const tabButtons = document.querySelectorAll('.tab-button');
        tabButtons.forEach((btn, index) => {
            const hint = document.createElement('span');
            hint.className = 'keyboard-shortcut-hint';
            hint.innerHTML = `<kbd>${index + 1}</kbd>`;
            hint.setAttribute('aria-label', `Keyboard shortcut: ${index + 1}`);
            btn.appendChild(hint);
        });
        
        // Add hint to search input
        const searchInput = document.getElementById('instrument-search');
        if (searchInput) {
            searchInput.placeholder = 'Search instruments... (Press S or Ctrl+F)';
        }
    },
    
    showHelp() {
        const overlay = document.createElement('div');
        overlay.className = 'keyboard-shortcuts-overlay';
        overlay.onclick = () => this.hideHelp();
        
        const modal = document.createElement('div');
        modal.className = 'keyboard-shortcuts-modal';
        modal.setAttribute('role', 'dialog');
        modal.setAttribute('aria-labelledby', 'shortcuts-title');
        modal.setAttribute('aria-modal', 'true');
        
        modal.innerHTML = `
            <h2 id="shortcuts-title">Keyboard Shortcuts</h2>
            <div class="shortcuts-list">
                <div class="shortcut-item">
                    <span class="shortcut-description">Go to Broker tab</span>
                    <div class="shortcut-keys"><kbd>1</kbd></div>
                </div>
                <div class="shortcut-item">
                    <span class="shortcut-description">Go to Instruments tab</span>
                    <div class="shortcut-keys"><kbd>2</kbd></div>
                </div>
                <div class="shortcut-item">
                    <span class="shortcut-description">Go to Configuration tab</span>
                    <div class="shortcut-keys"><kbd>3</kbd></div>
                </div>
                <div class="shortcut-item">
                    <span class="shortcut-description">Go to Monitor tab</span>
                    <div class="shortcut-keys"><kbd>4</kbd></div>
                </div>
                <div class="shortcut-item">
                    <span class="shortcut-description">Go to Trades tab</span>
                    <div class="shortcut-keys"><kbd>5</kbd></div>
                </div>
                <div class="shortcut-item">
                    <span class="shortcut-description">Focus search</span>
                    <div class="shortcut-keys"><kbd>S</kbd> or <kbd>Ctrl</kbd>+<kbd>F</kbd></div>
                </div>
                <div class="shortcut-item">
                    <span class="shortcut-description">Refresh current tab</span>
                    <div class="shortcut-keys"><kbd>R</kbd></div>
                </div>
                <div class="shortcut-item">
                    <span class="shortcut-description">Save configuration</span>
                    <div class="shortcut-keys"><kbd>Ctrl</kbd>+<kbd>S</kbd></div>
                </div>
                <div class="shortcut-item">
                    <span class="shortcut-description">Load configuration</span>
                    <div class="shortcut-keys"><kbd>Ctrl</kbd>+<kbd>L</kbd></div>
                </div>
                <div class="shortcut-item">
                    <span class="shortcut-description">Export configuration</span>
                    <div class="shortcut-keys"><kbd>Ctrl</kbd>+<kbd>E</kbd></div>
                </div>
                <div class="shortcut-item">
                    <span class="shortcut-description">Show this help</span>
                    <div class="shortcut-keys"><kbd>Shift</kbd>+<kbd>H</kbd></div>
                </div>
                <div class="shortcut-item">
                    <span class="shortcut-description">Close modals</span>
                    <div class="shortcut-keys"><kbd>Esc</kbd></div>
                </div>
            </div>
            <div style="margin-top: 1.5rem; text-align: center;">
                <button class="btn btn-primary" onclick="KeyboardShortcuts.hideHelp()">Close</button>
            </div>
        `;
        
        document.body.appendChild(overlay);
        document.body.appendChild(modal);
        
        // Focus the modal
        modal.focus();
        
        // Trap focus in modal
        this.trapFocus(modal);
    },
    
    hideHelp() {
        const overlay = document.querySelector('.keyboard-shortcuts-overlay');
        const modal = document.querySelector('.keyboard-shortcuts-modal');
        if (overlay) overlay.remove();
        if (modal) modal.remove();
    },
    
    trapFocus(element) {
        const focusableElements = element.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        const firstFocusable = focusableElements[0];
        const lastFocusable = focusableElements[focusableElements.length - 1];
        
        element.addEventListener('keydown', (e) => {
            if (e.key === 'Tab') {
                if (e.shiftKey) {
                    if (document.activeElement === firstFocusable) {
                        e.preventDefault();
                        lastFocusable.focus();
                    }
                } else {
                    if (document.activeElement === lastFocusable) {
                        e.preventDefault();
                        firstFocusable.focus();
                    }
                }
            }
        });
    }
};

// Helper functions for keyboard shortcuts
function switchTab(tabName) {
    const tabButton = document.querySelector(`[data-tab="${tabName}"]`);
    if (tabButton) {
        tabButton.click();
    }
}

function focusSearch() {
    const searchInput = document.getElementById('instrument-search');
    if (searchInput && searchInput.offsetParent !== null) {
        searchInput.focus();
        searchInput.select();
    }
}

function refreshCurrentTab() {
    const activeTab = document.querySelector('.tab-button.active');
    if (activeTab) {
        const tabName = activeTab.dataset.tab;
        if (typeof loadTabData === 'function') {
            loadTabData(tabName);
        }
    }
}

function saveConfiguration() {
    const saveBtn = document.getElementById('save-config-btn');
    if (saveBtn && saveBtn.offsetParent !== null) {
        saveBtn.click();
    }
}

function loadConfiguration() {
    const loadBtn = document.getElementById('load-config-btn');
    if (loadBtn && loadBtn.offsetParent !== null) {
        loadBtn.click();
    }
}

function exportConfiguration() {
    const exportBtn = document.getElementById('export-config-btn');
    if (exportBtn && exportBtn.offsetParent !== null) {
        exportBtn.click();
    }
}

function closeModals() {
    // Close keyboard shortcuts modal
    KeyboardShortcuts.hideHelp();
    
    // Close any other modals
    const overlays = document.querySelectorAll('.modal-overlay, .keyboard-shortcuts-overlay');
    overlays.forEach(overlay => overlay.remove());
    
    const modals = document.querySelectorAll('.modal, .keyboard-shortcuts-modal');
    modals.forEach(modal => modal.remove());
}

// Accessibility Enhancements
const AccessibilityEnhancements = {
    init() {
        this.addSkipLink();
        this.enhanceFormLabels();
        this.addAriaLabels();
        this.improveTableAccessibility();
        this.enhanceNotifications();
        this.addLiveRegions();
    },
    
    addSkipLink() {
        const skipLink = document.createElement('a');
        skipLink.href = '#main-content';
        skipLink.className = 'skip-to-main';
        skipLink.textContent = 'Skip to main content';
        document.body.insertBefore(skipLink, document.body.firstChild);
        
        // Add id to main content
        const mainContent = document.querySelector('.dashboard-content');
        if (mainContent) {
            mainContent.id = 'main-content';
            mainContent.setAttribute('role', 'main');
        }
    },
    
    enhanceFormLabels() {
        // Ensure all form inputs have associated labels
        const inputs = document.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            if (!input.id) {
                input.id = 'input-' + Math.random().toString(36).substr(2, 9);
            }
            
            // Find or create label
            let label = document.querySelector(`label[for="${input.id}"]`);
            if (!label) {
                label = input.closest('.form-group')?.querySelector('label');
                if (label) {
                    label.setAttribute('for', input.id);
                }
            }
            
            // Add aria-required for required fields
            if (input.required) {
                input.setAttribute('aria-required', 'true');
            }
            
            // Add aria-invalid for invalid fields
            if (input.classList.contains('invalid')) {
                input.setAttribute('aria-invalid', 'true');
            }
        });
    },
    
    addAriaLabels() {
        // Add aria-labels to buttons without text
        const buttons = document.querySelectorAll('button:not([aria-label])');
        buttons.forEach(button => {
            if (!button.textContent.trim() && button.querySelector('.btn-icon')) {
                const icon = button.querySelector('.btn-icon').textContent;
                button.setAttribute('aria-label', this.getButtonLabel(icon, button));
            }
        });
        
        // Add aria-labels to tab buttons
        const tabButtons = document.querySelectorAll('.tab-button');
        tabButtons.forEach(button => {
            const tabName = button.dataset.tab;
            button.setAttribute('aria-label', `${tabName} tab`);
            button.setAttribute('role', 'tab');
            button.setAttribute('aria-selected', button.classList.contains('active') ? 'true' : 'false');
        });
        
        // Add role to tab navigation
        const tabNav = document.querySelector('.tab-navigation');
        if (tabNav) {
            tabNav.setAttribute('role', 'tablist');
        }
        
        // Add role to tab content
        const tabContents = document.querySelectorAll('.tab-content');
        tabContents.forEach(content => {
            content.setAttribute('role', 'tabpanel');
        });
    },
    
    getButtonLabel(icon, button) {
        const labels = {
            '🔄': 'Refresh',
            '💾': 'Save',
            '📂': 'Load',
            '📤': 'Export',
            '📥': 'Import',
            '📋': 'Copy',
            '▶️': 'Start',
            '⏹️': 'Stop',
            '🔧': 'Settings'
        };
        return labels[icon] || button.textContent.trim() || 'Button';
    },
    
    improveTableAccessibility() {
        const tables = document.querySelectorAll('.data-table');
        tables.forEach(table => {
            // Add caption if missing
            if (!table.querySelector('caption')) {
                const caption = document.createElement('caption');
                caption.className = 'sr-only';
                caption.textContent = 'Data table';
                table.insertBefore(caption, table.firstChild);
            }
            
            // Add scope to headers
            const headers = table.querySelectorAll('th');
            headers.forEach(header => {
                if (!header.hasAttribute('scope')) {
                    header.setAttribute('scope', 'col');
                }
            });
            
            // Add aria-sort to sortable headers
            const sortableHeaders = table.querySelectorAll('th.sortable');
            sortableHeaders.forEach(header => {
                header.setAttribute('aria-sort', 'none');
                header.setAttribute('role', 'button');
                header.setAttribute('tabindex', '0');
                
                // Add keyboard support for sorting
                header.addEventListener('keydown', (e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        header.click();
                    }
                });
            });
        });
    },
    
    enhanceNotifications() {
        // Observe notification container for new notifications
        const container = document.getElementById('notification-container');
        if (container) {
            const observer = new MutationObserver((mutations) => {
                mutations.forEach((mutation) => {
                    mutation.addedNodes.forEach((node) => {
                        if (node.classList && node.classList.contains('notification')) {
                            node.setAttribute('role', 'alert');
                            node.setAttribute('aria-live', 'assertive');
                            node.setAttribute('aria-atomic', 'true');
                        }
                    });
                });
            });
            
            observer.observe(container, { childList: true });
        }
    },
    
    addLiveRegions() {
        // Add live region for status updates
        const statusRegion = document.createElement('div');
        statusRegion.id = 'status-live-region';
        statusRegion.className = 'sr-only';
        statusRegion.setAttribute('role', 'status');
        statusRegion.setAttribute('aria-live', 'polite');
        statusRegion.setAttribute('aria-atomic', 'true');
        document.body.appendChild(statusRegion);
        
        // Add live region for alerts
        const alertRegion = document.createElement('div');
        alertRegion.id = 'alert-live-region';
        alertRegion.className = 'sr-only';
        alertRegion.setAttribute('role', 'alert');
        alertRegion.setAttribute('aria-live', 'assertive');
        alertRegion.setAttribute('aria-atomic', 'true');
        document.body.appendChild(alertRegion);
    },
    
    announceStatus(message) {
        const region = document.getElementById('status-live-region');
        if (region) {
            region.textContent = message;
            setTimeout(() => {
                region.textContent = '';
            }, 1000);
        }
    },
    
    announceAlert(message) {
        const region = document.getElementById('alert-live-region');
        if (region) {
            region.textContent = message;
            setTimeout(() => {
                region.textContent = '';
            }, 1000);
        }
    }
};

// Mobile Enhancements
const MobileEnhancements = {
    init() {
        this.detectTouchDevice();
        this.addSwipeGestures();
        this.improveScrolling();
        this.handleOrientationChange();
    },
    
    detectTouchDevice() {
        if ('ontouchstart' in window || navigator.maxTouchPoints > 0) {
            document.body.classList.add('touch-device');
        }
    },
    
    addSwipeGestures() {
        let touchStartX = 0;
        let touchEndX = 0;
        
        const tabContent = document.querySelector('.dashboard-content');
        if (!tabContent) return;
        
        tabContent.addEventListener('touchstart', (e) => {
            touchStartX = e.changedTouches[0].screenX;
        }, { passive: true });
        
        tabContent.addEventListener('touchend', (e) => {
            touchEndX = e.changedTouches[0].screenX;
            this.handleSwipe(touchStartX, touchEndX);
        }, { passive: true });
    },
    
    handleSwipe(startX, endX) {
        const threshold = 100;
        const diff = startX - endX;
        
        if (Math.abs(diff) < threshold) return;
        
        const tabs = ['broker', 'instruments', 'configuration', 'monitor', 'trades'];
        const activeTab = document.querySelector('.tab-button.active');
        if (!activeTab) return;
        
        const currentIndex = tabs.indexOf(activeTab.dataset.tab);
        
        if (diff > 0 && currentIndex < tabs.length - 1) {
            // Swipe left - next tab
            switchTab(tabs[currentIndex + 1]);
        } else if (diff < 0 && currentIndex > 0) {
            // Swipe right - previous tab
            switchTab(tabs[currentIndex - 1]);
        }
    },
    
    improveScrolling() {
        // Add smooth scrolling
        document.documentElement.style.scrollBehavior = 'smooth';
        
        // Prevent overscroll on iOS
        document.body.addEventListener('touchmove', (e) => {
            if (e.target.closest('.tab-navigation .container') || 
                e.target.closest('.config-tabs')) {
                // Allow horizontal scrolling for these elements
                return;
            }
        }, { passive: true });
    },
    
    handleOrientationChange() {
        window.addEventListener('orientationchange', () => {
            // Refresh layout after orientation change
            setTimeout(() => {
                window.scrollTo(0, 0);
            }, 100);
        });
    }
};

// Animation Enhancements
const AnimationEnhancements = {
    init() {
        this.addPageTransitions();
        this.addScrollAnimations();
        this.enhanceNotificationAnimations();
    },
    
    addPageTransitions() {
        // Add fade-in animation to cards when they appear
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '0';
                    entry.target.style.transform = 'translateY(20px)';
                    
                    setTimeout(() => {
                        entry.target.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
                        entry.target.style.opacity = '1';
                        entry.target.style.transform = 'translateY(0)';
                    }, 50);
                    
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });
        
        // Observe all cards
        document.querySelectorAll('.card').forEach(card => {
            observer.observe(card);
        });
    },
    
    addScrollAnimations() {
        // Add scroll-based animations for elements
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                }
            });
        }, { threshold: 0.1 });
        
        // Observe elements with data-animate attribute
        document.querySelectorAll('[data-animate]').forEach(element => {
            observer.observe(element);
        });
    },
    
    enhanceNotificationAnimations() {
        // Auto-remove notifications with animation
        const container = document.getElementById('notification-container');
        if (!container) return;
        
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.classList && node.classList.contains('notification')) {
                        // Auto-remove after 5 seconds
                        setTimeout(() => {
                            node.classList.add('removing');
                            setTimeout(() => {
                                node.remove();
                            }, 300);
                        }, 5000);
                    }
                });
            });
        });
        
        observer.observe(container, { childList: true });
    }
};

// Initialize all enhancements when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initUIEnhancements);
} else {
    initUIEnhancements();
}

function initUIEnhancements() {
    KeyboardShortcuts.init();
    AccessibilityEnhancements.init();
    MobileEnhancements.init();
    AnimationEnhancements.init();
    
    console.log('UI/UX enhancements initialized');
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        KeyboardShortcuts,
        AccessibilityEnhancements,
        MobileEnhancements,
        AnimationEnhancements
    };
}
