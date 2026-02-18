/**
 * Loading States Module for Indian Market Trading Dashboard
 * Provides comprehensive loading indicators, spinners, and skeleton screens
 */

class LoadingStates {
    constructor() {
        this.activeLoaders = new Map();
        this.init();
    }
    
    /**
     * Initialize loading states
     */
    init() {
        // Create global loading overlay if it doesn't exist
        this.createGlobalLoadingOverlay();
    }
    
    /**
     * Create global loading overlay
     */
    createGlobalLoadingOverlay() {
        if (!document.getElementById('global-loading-overlay')) {
            const overlay = document.createElement('div');
            overlay.id = 'global-loading-overlay';
            overlay.className = 'global-loading-overlay';
            overlay.style.display = 'none';
            overlay.innerHTML = `
                <div class="loading-content">
                    <div class="spinner-large"></div>
                    <p id="global-loading-message">Loading...</p>
                </div>
            `;
            document.body.appendChild(overlay);
        }
    }
    
    /**
     * Show global loading overlay
     */
    showGlobalLoading(message = 'Loading...') {
        const overlay = document.getElementById('global-loading-overlay');
        const messageEl = document.getElementById('global-loading-message');
        
        if (overlay) {
            if (messageEl) {
                messageEl.textContent = message;
            }
            overlay.style.display = 'flex';
        }
    }
    
    /**
     * Hide global loading overlay
     */
    hideGlobalLoading() {
        const overlay = document.getElementById('global-loading-overlay');
        if (overlay) {
            overlay.style.display = 'none';
        }
    }
    
    /**
     * Show button loading state
     */
    showButtonLoading(buttonId, loadingText = null) {
        const button = typeof buttonId === 'string' 
            ? document.getElementById(buttonId) 
            : buttonId;
        
        if (!button) return;
        
        // Store original state
        if (!this.activeLoaders.has(button)) {
            this.activeLoaders.set(button, {
                originalText: button.textContent,
                originalDisabled: button.disabled,
                originalHTML: button.innerHTML
            });
        }
        
        // Apply loading state
        button.disabled = true;
        button.classList.add('btn-loading');
        
        if (loadingText) {
            button.innerHTML = `
                <span class="btn-spinner"></span>
                <span>${loadingText}</span>
            `;
        } else {
            button.innerHTML = `<span class="btn-spinner"></span>`;
        }
    }
    
    /**
     * Hide button loading state
     */
    hideButtonLoading(buttonId) {
        const button = typeof buttonId === 'string' 
            ? document.getElementById(buttonId) 
            : buttonId;
        
        if (!button) return;
        
        // Restore original state
        const originalState = this.activeLoaders.get(button);
        if (originalState) {
            button.disabled = originalState.originalDisabled;
            button.classList.remove('btn-loading');
            button.innerHTML = originalState.originalHTML;
            this.activeLoaders.delete(button);
        }
    }
    
    /**
     * Show inline loading spinner
     */
    showInlineLoading(containerId, message = 'Loading...') {
        const container = typeof containerId === 'string' 
            ? document.getElementById(containerId) 
            : containerId;
        
        if (!container) return;
        
        // Store original content
        if (!this.activeLoaders.has(container)) {
            this.activeLoaders.set(container, {
                originalHTML: container.innerHTML
            });
        }
        
        container.innerHTML = `
            <div class="inline-loading">
                <div class="spinner"></div>
                <p>${message}</p>
            </div>
        `;
    }
    
    /**
     * Hide inline loading spinner
     */
    hideInlineLoading(containerId, newContent = null) {
        const container = typeof containerId === 'string' 
            ? document.getElementById(containerId) 
            : containerId;
        
        if (!container) return;
        
        if (newContent !== null) {
            container.innerHTML = newContent;
        } else {
            const originalState = this.activeLoaders.get(container);
            if (originalState) {
                container.innerHTML = originalState.originalHTML;
                this.activeLoaders.delete(container);
            }
        }
    }
    
    /**
     * Show skeleton screen
     */
    showSkeleton(containerId, type = 'default', count = 1) {
        const container = typeof containerId === 'string' 
            ? document.getElementById(containerId) 
            : containerId;
        
        if (!container) return;
        
        // Store original content
        if (!this.activeLoaders.has(container)) {
            this.activeLoaders.set(container, {
                originalHTML: container.innerHTML
            });
        }
        
        const skeletons = [];
        for (let i = 0; i < count; i++) {
            skeletons.push(this.getSkeletonHTML(type));
        }
        
        container.innerHTML = skeletons.join('');
    }
    
    /**
     * Get skeleton HTML by type
     */
    getSkeletonHTML(type) {
        const skeletonTemplates = {
            'default': `
                <div class="skeleton-item">
                    <div class="skeleton-line"></div>
                    <div class="skeleton-line"></div>
                    <div class="skeleton-line short"></div>
                </div>
            `,
            'card': `
                <div class="skeleton-card">
                    <div class="skeleton-header"></div>
                    <div class="skeleton-line"></div>
                    <div class="skeleton-line"></div>
                    <div class="skeleton-line short"></div>
                </div>
            `,
            'table-row': `
                <tr class="skeleton-row">
                    <td><div class="skeleton-cell"></div></td>
                    <td><div class="skeleton-cell"></div></td>
                    <td><div class="skeleton-cell"></div></td>
                    <td><div class="skeleton-cell"></div></td>
                    <td><div class="skeleton-cell"></div></td>
                </tr>
            `,
            'list-item': `
                <div class="skeleton-list-item">
                    <div class="skeleton-avatar"></div>
                    <div class="skeleton-content">
                        <div class="skeleton-line"></div>
                        <div class="skeleton-line short"></div>
                    </div>
                </div>
            `,
            'broker-card': `
                <div class="skeleton-broker-card">
                    <div class="skeleton-logo"></div>
                    <div class="skeleton-line"></div>
                </div>
            `,
            'instrument-row': `
                <tr class="skeleton-row">
                    <td><div class="skeleton-checkbox"></div></td>
                    <td><div class="skeleton-cell"></div></td>
                    <td><div class="skeleton-cell long"></div></td>
                    <td><div class="skeleton-cell short"></div></td>
                    <td><div class="skeleton-cell short"></div></td>
                    <td><div class="skeleton-cell short"></div></td>
                </tr>
            `,
            'trade-row': `
                <tr class="skeleton-row">
                    <td><div class="skeleton-cell"></div></td>
                    <td><div class="skeleton-cell"></div></td>
                    <td><div class="skeleton-cell short"></div></td>
                    <td><div class="skeleton-cell short"></div></td>
                    <td><div class="skeleton-cell"></div></td>
                    <td><div class="skeleton-cell"></div></td>
                    <td><div class="skeleton-cell"></div></td>
                </tr>
            `,
            'position-row': `
                <tr class="skeleton-row">
                    <td><div class="skeleton-cell"></div></td>
                    <td><div class="skeleton-cell short"></div></td>
                    <td><div class="skeleton-cell"></div></td>
                    <td><div class="skeleton-cell"></div></td>
                    <td><div class="skeleton-cell"></div></td>
                    <td><div class="skeleton-cell short"></div></td>
                </tr>
            `
        };
        
        return skeletonTemplates[type] || skeletonTemplates['default'];
    }
    
    /**
     * Hide skeleton screen
     */
    hideSkeleton(containerId, newContent = null) {
        this.hideInlineLoading(containerId, newContent);
    }
    
    /**
     * Show table loading state
     */
    showTableLoading(tableBodyId, colspan = 5, message = 'Loading...') {
        const tbody = typeof tableBodyId === 'string' 
            ? document.getElementById(tableBodyId) 
            : tableBodyId;
        
        if (!tbody) return;
        
        // Store original content
        if (!this.activeLoaders.has(tbody)) {
            this.activeLoaders.set(tbody, {
                originalHTML: tbody.innerHTML
            });
        }
        
        tbody.innerHTML = `
            <tr>
                <td colspan="${colspan}" style="text-align: center; padding: 2rem;">
                    <div class="spinner"></div>
                    <p style="margin-top: 1rem; color: var(--text-muted);">${message}</p>
                </td>
            </tr>
        `;
    }
    
    /**
     * Hide table loading state
     */
    hideTableLoading(tableBodyId, newContent = null) {
        this.hideInlineLoading(tableBodyId, newContent);
    }
    
    /**
     * Show progress bar
     */
    showProgress(containerId, progress = 0, message = '') {
        const container = typeof containerId === 'string' 
            ? document.getElementById(containerId) 
            : containerId;
        
        if (!container) return;
        
        // Create or update progress bar
        let progressBar = container.querySelector('.progress-bar-container');
        if (!progressBar) {
            // Store original content
            if (!this.activeLoaders.has(container)) {
                this.activeLoaders.set(container, {
                    originalHTML: container.innerHTML
                });
            }
            
            container.innerHTML = `
                <div class="progress-bar-container">
                    <div class="progress-bar">
                        <div class="progress-bar-fill" style="width: ${progress}%"></div>
                    </div>
                    <p class="progress-message">${message}</p>
                </div>
            `;
        } else {
            const fill = progressBar.querySelector('.progress-bar-fill');
            const messageEl = progressBar.querySelector('.progress-message');
            
            if (fill) fill.style.width = `${progress}%`;
            if (messageEl) messageEl.textContent = message;
        }
    }
    
    /**
     * Hide progress bar
     */
    hideProgress(containerId) {
        this.hideInlineLoading(containerId);
    }
    
    /**
     * Show loading dots animation
     */
    showLoadingDots(containerId, message = 'Loading') {
        const container = typeof containerId === 'string' 
            ? document.getElementById(containerId) 
            : containerId;
        
        if (!container) return;
        
        // Store original content
        if (!this.activeLoaders.has(container)) {
            this.activeLoaders.set(container, {
                originalHTML: container.innerHTML
            });
        }
        
        container.innerHTML = `
            <div class="loading-dots">
                <span>${message}</span>
                <span class="dot">.</span>
                <span class="dot">.</span>
                <span class="dot">.</span>
            </div>
        `;
    }
    
    /**
     * Disable element during operation
     */
    disableElement(elementId) {
        const element = typeof elementId === 'string' 
            ? document.getElementById(elementId) 
            : elementId;
        
        if (!element) return;
        
        // Store original state
        if (!this.activeLoaders.has(element)) {
            this.activeLoaders.set(element, {
                originalDisabled: element.disabled,
                originalPointerEvents: element.style.pointerEvents,
                originalOpacity: element.style.opacity
            });
        }
        
        element.disabled = true;
        element.style.pointerEvents = 'none';
        element.style.opacity = '0.6';
        element.classList.add('disabled-loading');
    }
    
    /**
     * Enable element after operation
     */
    enableElement(elementId) {
        const element = typeof elementId === 'string' 
            ? document.getElementById(elementId) 
            : elementId;
        
        if (!element) return;
        
        const originalState = this.activeLoaders.get(element);
        if (originalState) {
            element.disabled = originalState.originalDisabled;
            element.style.pointerEvents = originalState.originalPointerEvents;
            element.style.opacity = originalState.originalOpacity;
            element.classList.remove('disabled-loading');
            this.activeLoaders.delete(element);
        }
    }
    
    /**
     * Show loading state for multiple elements
     */
    showMultipleLoading(elementIds, type = 'button') {
        elementIds.forEach(id => {
            if (type === 'button') {
                this.showButtonLoading(id);
            } else if (type === 'inline') {
                this.showInlineLoading(id);
            } else if (type === 'disable') {
                this.disableElement(id);
            }
        });
    }
    
    /**
     * Hide loading state for multiple elements
     */
    hideMultipleLoading(elementIds, type = 'button') {
        elementIds.forEach(id => {
            if (type === 'button') {
                this.hideButtonLoading(id);
            } else if (type === 'inline') {
                this.hideInlineLoading(id);
            } else if (type === 'disable') {
                this.enableElement(id);
            }
        });
    }
    
    /**
     * Clear all active loaders
     */
    clearAllLoaders() {
        this.activeLoaders.forEach((state, element) => {
            if (element.tagName === 'BUTTON') {
                this.hideButtonLoading(element);
            } else {
                this.hideInlineLoading(element);
            }
        });
        this.activeLoaders.clear();
        this.hideGlobalLoading();
    }
    
    /**
     * Get active loaders count
     */
    getActiveLoadersCount() {
        return this.activeLoaders.size;
    }
}

// Create global instance
const loadingStates = new LoadingStates();

// Export for use in other modules
window.loadingStates = loadingStates;

// Backward compatibility with existing loading helper
if (!window.loading) {
    window.loading = {
        show: (buttonId, text) => loadingStates.showButtonLoading(buttonId, text),
        hide: (buttonId) => loadingStates.hideButtonLoading(buttonId)
    };
}
