/**
 * Configuration Manager Module
 * Handles save/load/delete configuration dialogs and operations
 */

const ConfigManager = {
    /**
     * Initialize configuration manager
     */
    init() {
        this.setupEventListeners();
        this.createDialogs();
    },

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Save button
        const saveBtn = document.getElementById('save-config-btn');
        if (saveBtn) {
            saveBtn.addEventListener('click', () => this.showSaveDialog());
        }

        // Load button
        const loadBtn = document.getElementById('load-config-btn');
        if (loadBtn) {
            loadBtn.addEventListener('click', () => this.showLoadDialog());
        }
    },

    /**
     * Create dialog elements
     */
    createDialogs() {
        // Create save dialog
        this.createSaveDialog();
        
        // Create load dialog
        this.createLoadDialog();
    },

    /**
     * Create save configuration dialog
     */
    createSaveDialog() {
        const dialog = document.createElement('div');
        dialog.id = 'save-config-dialog';
        dialog.className = 'modal-overlay';
        dialog.style.display = 'none';
        dialog.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Save Configuration</h3>
                    <button class="modal-close" onclick="ConfigManager.closeSaveDialog()">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="form-group">
                        <label for="config-name-input">Configuration Name</label>
                        <input type="text" id="config-name-input" class="form-control" 
                               placeholder="e.g., NIFTY Intraday Strategy" required>
                        <small class="form-help">Enter a descriptive name for this configuration</small>
                    </div>
                    <div class="form-group">
                        <label for="config-description-input">Description (Optional)</label>
                        <textarea id="config-description-input" class="form-control" rows="3"
                                  placeholder="Brief description of this configuration"></textarea>
                    </div>
                    <div id="save-config-error" class="error-message" style="display: none;"></div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" onclick="ConfigManager.closeSaveDialog()">Cancel</button>
                    <button class="btn btn-primary" onclick="ConfigManager.saveConfiguration()">Save</button>
                </div>
            </div>
        `;
        document.body.appendChild(dialog);
    },

    /**
     * Create load configuration dialog
     */
    createLoadDialog() {
        const dialog = document.createElement('div');
        dialog.id = 'load-config-dialog';
        dialog.className = 'modal-overlay';
        dialog.style.display = 'none';
        dialog.innerHTML = `
            <div class="modal-content modal-large">
                <div class="modal-header">
                    <h3>Load Configuration</h3>
                    <button class="modal-close" onclick="ConfigManager.closeLoadDialog()">&times;</button>
                </div>
                <div class="modal-body">
                    <div id="load-config-loading" class="loading-indicator" style="display: none;">
                        <div class="spinner"></div>
                        <p>Loading configurations...</p>
                    </div>
                    <div id="config-list-container">
                        <!-- Configuration list will be loaded here -->
                    </div>
                    <div id="load-config-error" class="error-message" style="display: none;"></div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" onclick="ConfigManager.closeLoadDialog()">Close</button>
                </div>
            </div>
        `;
        document.body.appendChild(dialog);
    },

    /**
     * Show save configuration dialog
     */
    showSaveDialog() {
        // Validate before showing dialog
        if (typeof Validation !== 'undefined') {
            if (!Validation.validateBeforeSave()) {
                showNotification('Please fix validation errors before saving', 'error');
                return;
            }
        }

        const dialog = document.getElementById('save-config-dialog');
        const nameInput = document.getElementById('config-name-input');
        const descInput = document.getElementById('config-description-input');
        const errorDiv = document.getElementById('save-config-error');
        
        // Clear previous values
        nameInput.value = '';
        descInput.value = '';
        errorDiv.style.display = 'none';
        
        // Show dialog
        dialog.style.display = 'flex';
        nameInput.focus();
    },

    /**
     * Close save configuration dialog
     */
    closeSaveDialog() {
        const dialog = document.getElementById('save-config-dialog');
        dialog.style.display = 'none';
    },

    /**
     * Save configuration
     */
    async saveConfiguration() {
        const nameInput = document.getElementById('config-name-input');
        const descInput = document.getElementById('config-description-input');
        const errorDiv = document.getElementById('save-config-error');
        
        const name = nameInput.value.trim();
        
        // Validate name
        if (!name) {
            errorDiv.textContent = 'Configuration name is required';
            errorDiv.style.display = 'block';
            return;
        }

        // Validate name format (alphanumeric, spaces, hyphens, underscores)
        if (!/^[a-zA-Z0-9\s\-_]+$/.test(name)) {
            errorDiv.textContent = 'Name can only contain letters, numbers, spaces, hyphens, and underscores';
            errorDiv.style.display = 'block';
            return;
        }

        try {
            // Get form data
            const config = ConfigForm.getFormData();
            if (!config) {
                throw new Error('Failed to get configuration data');
            }

            // Add description if provided
            if (descInput.value.trim()) {
                config.description = descInput.value.trim();
            }

            // Save configuration
            const response = await api.saveConfig(config, name);
            
            if (response.success) {
                showNotification(`Configuration "${name}" saved successfully`, 'success');
                this.closeSaveDialog();
                
                // Update app state
                AppState.config.current = config;
                AppState.config.isDirty = false;
            } else {
                throw new Error(response.error || 'Failed to save configuration');
            }
        } catch (error) {
            console.error('Save configuration error:', error);
            errorDiv.textContent = 'Error: ' + error.message;
            errorDiv.style.display = 'block';
        }
    },

    /**
     * Show load configuration dialog
     */
    async showLoadDialog() {
        const dialog = document.getElementById('load-config-dialog');
        const loadingDiv = document.getElementById('load-config-loading');
        const containerDiv = document.getElementById('config-list-container');
        const errorDiv = document.getElementById('load-config-error');
        
        // Show dialog
        dialog.style.display = 'flex';
        
        // Show loading
        loadingDiv.style.display = 'flex';
        containerDiv.innerHTML = '';
        errorDiv.style.display = 'none';
        
        try {
            // Fetch configurations
            const response = await api.listConfigs();
            
            loadingDiv.style.display = 'none';
            
            if (response.success) {
                this.renderConfigList(response.configs);
            } else {
                throw new Error(response.error || 'Failed to load configurations');
            }
        } catch (error) {
            console.error('Load configurations error:', error);
            loadingDiv.style.display = 'none';
            errorDiv.textContent = 'Error: ' + error.message;
            errorDiv.style.display = 'block';
        }
    },

    /**
     * Close load configuration dialog
     */
    closeLoadDialog() {
        const dialog = document.getElementById('load-config-dialog');
        dialog.style.display = 'none';
    },

    /**
     * Render configuration list
     */
    renderConfigList(configs) {
        const container = document.getElementById('config-list-container');
        
        if (!configs || configs.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <p>No saved configurations found</p>
                    <small>Save your first configuration to see it here</small>
                </div>
            `;
            return;
        }

        // Sort by name
        configs.sort((a, b) => a.name.localeCompare(b.name));

        // Render configuration cards
        container.innerHTML = `
            <div class="config-list">
                ${configs.map(config => this.renderConfigCard(config)).join('')}
            </div>
        `;
    },

    /**
     * Render single configuration card
     */
    renderConfigCard(config) {
        return `
            <div class="config-card" data-config-name="${config.name}">
                <div class="config-card-header">
                    <h4 class="config-card-title">${this.escapeHtml(config.name)}</h4>
                    <div class="config-card-actions">
                        <button class="btn btn-sm btn-primary" 
                                onclick="ConfigManager.loadConfiguration('${this.escapeHtml(config.name)}')">
                            Load
                        </button>
                        <button class="btn btn-sm btn-danger" 
                                onclick="ConfigManager.confirmDelete('${this.escapeHtml(config.name)}')">
                            Delete
                        </button>
                    </div>
                </div>
                <div class="config-card-body">
                    ${config.description ? `<p class="config-description">${this.escapeHtml(config.description)}</p>` : ''}
                    <div class="config-meta">
                        ${config.broker ? `<span class="config-badge">Broker: ${this.escapeHtml(config.broker)}</span>` : ''}
                        ${config.strategy ? `<span class="config-badge">Strategy: ${this.escapeHtml(config.strategy)}</span>` : ''}
                        ${config.instruments_count ? `<span class="config-badge">${config.instruments_count} Instruments</span>` : ''}
                    </div>
                </div>
            </div>
        `;
    },

    /**
     * Load configuration
     */
    async loadConfiguration(name) {
        try {
            showNotification(`Loading configuration "${name}"...`, 'info');
            
            const response = await api.getConfig(name);
            
            if (response.success && response.config) {
                // Set form data
                if (typeof ConfigForm !== 'undefined') {
                    ConfigForm.setFormData(response.config);
                }
                
                // Update app state
                AppState.config.current = response.config;
                AppState.config.isDirty = false;
                
                showNotification(`Configuration "${name}" loaded successfully`, 'success');
                this.closeLoadDialog();
                
                // Switch to configuration tab if not already there
                const configTab = document.querySelector('[data-tab="configuration"]');
                if (configTab && !configTab.classList.contains('active')) {
                    configTab.click();
                }
            } else {
                throw new Error(response.error || 'Failed to load configuration');
            }
        } catch (error) {
            console.error('Load configuration error:', error);
            showNotification('Error loading configuration: ' + error.message, 'error');
        }
    },

    /**
     * Confirm delete configuration
     */
    confirmDelete(name) {
        if (confirm(`Are you sure you want to delete the configuration "${name}"?\n\nThis action cannot be undone.`)) {
            this.deleteConfiguration(name);
        }
    },

    /**
     * Delete configuration
     */
    async deleteConfiguration(name) {
        try {
            showNotification(`Deleting configuration "${name}"...`, 'info');
            
            const response = await api.deleteConfig(name);
            
            if (response.success) {
                showNotification(`Configuration "${name}" deleted successfully`, 'success');
                
                // Remove card from UI
                const card = document.querySelector(`[data-config-name="${name}"]`);
                if (card) {
                    card.remove();
                }
                
                // Check if list is now empty
                const container = document.getElementById('config-list-container');
                const configList = container.querySelector('.config-list');
                if (configList && configList.children.length === 0) {
                    this.renderConfigList([]);
                }
            } else {
                throw new Error(response.error || 'Failed to delete configuration');
            }
        } catch (error) {
            console.error('Delete configuration error:', error);
            showNotification('Error deleting configuration: ' + error.message, 'error');
        }
    },

    /**
     * Escape HTML to prevent XSS
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
};

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => ConfigManager.init());
} else {
    ConfigManager.init();
}
