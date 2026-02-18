/**
 * Export/Import Module
 * Handles configuration export and import functionality
 */

const ExportImport = {
    /**
     * Initialize export/import functionality
     */
    init() {
        this.setupEventListeners();
        this.createImportDialog();
    },

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Export button
        const exportBtn = document.getElementById('export-config-btn');
        if (exportBtn) {
            exportBtn.addEventListener('click', () => this.exportConfiguration());
        }

        // Import button
        const importBtn = document.getElementById('import-config-btn');
        if (importBtn) {
            importBtn.addEventListener('click', () => this.showImportDialog());
        }

        // Copy to clipboard button
        const copyBtn = document.getElementById('copy-config-btn');
        if (copyBtn) {
            copyBtn.addEventListener('click', () => this.copyToClipboard());
        }
    },

    /**
     * Create import dialog
     */
    createImportDialog() {
        const dialog = document.createElement('div');
        dialog.id = 'import-config-dialog';
        dialog.className = 'modal-overlay';
        dialog.style.display = 'none';
        dialog.innerHTML = `
            <div class="modal-content modal-large">
                <div class="modal-header">
                    <h3>Import Configuration</h3>
                    <button class="modal-close" onclick="ExportImport.closeImportDialog()">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="form-group">
                        <label>Import Method</label>
                        <div class="import-method-tabs">
                            <button class="import-method-tab active" data-method="file">
                                <span class="tab-icon">📁</span> From File
                            </button>
                            <button class="import-method-tab" data-method="paste">
                                <span class="tab-icon">📋</span> Paste JSON
                            </button>
                        </div>
                    </div>

                    <!-- File Import -->
                    <div class="import-method-content active" data-method-content="file">
                        <div class="form-group">
                            <label for="config-file-input">Select Configuration File</label>
                            <input type="file" id="config-file-input" class="form-control" 
                                   accept=".json,application/json">
                            <small class="form-help">Select a JSON configuration file to import</small>
                        </div>
                    </div>

                    <!-- Paste Import -->
                    <div class="import-method-content" data-method-content="paste">
                        <div class="form-group">
                            <label for="config-json-input">Paste Configuration JSON</label>
                            <textarea id="config-json-input" class="form-control" rows="10"
                                      placeholder='{"broker": "kite", "strategy": "trend_following", ...}'></textarea>
                            <small class="form-help">Paste the JSON configuration text here</small>
                        </div>
                    </div>

                    <!-- Validation Results -->
                    <div id="import-validation-results" style="display: none;">
                        <h4>Validation Results</h4>
                        <div id="import-validation-content"></div>
                    </div>

                    <div id="import-config-error" class="error-message" style="display: none;"></div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" onclick="ExportImport.closeImportDialog()">Cancel</button>
                    <button class="btn btn-primary" onclick="ExportImport.importConfiguration()">Import</button>
                </div>
            </div>
        `;
        document.body.appendChild(dialog);

        // Setup import method tabs
        this.setupImportMethodTabs();
    },

    /**
     * Setup import method tabs
     */
    setupImportMethodTabs() {
        const tabs = document.querySelectorAll('.import-method-tab');
        const contents = document.querySelectorAll('.import-method-content');

        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                const method = tab.getAttribute('data-method');
                
                // Remove active class from all tabs and contents
                tabs.forEach(t => t.classList.remove('active'));
                contents.forEach(c => c.classList.remove('active'));
                
                // Add active class to clicked tab and corresponding content
                tab.classList.add('active');
                const targetContent = document.querySelector(`[data-method-content="${method}"]`);
                if (targetContent) {
                    targetContent.classList.add('active');
                }
            });
        });
    },

    /**
     * Export configuration to JSON file
     */
    async exportConfiguration() {
        try {
            // Validate before export
            if (typeof Validation !== 'undefined') {
                if (!Validation.validateBeforeSave()) {
                    showNotification('Please fix validation errors before exporting', 'error');
                    return;
                }
            }

            // Get form data
            const config = ConfigForm.getFormData();
            if (!config) {
                throw new Error('Failed to get configuration data');
            }

            // Add metadata
            const exportData = {
                ...config,
                exported_at: new Date().toISOString(),
                exported_by: 'Indian Market Trading Dashboard',
                version: '1.0'
            };

            // Convert to JSON
            const jsonString = JSON.stringify(exportData, null, 2);

            // Create blob and download
            const blob = new Blob([jsonString], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            
            // Create download link
            const link = document.createElement('a');
            link.href = url;
            link.download = `config_${this.generateFilename()}.json`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            // Clean up
            URL.revokeObjectURL(url);

            showNotification('Configuration exported successfully', 'success');
        } catch (error) {
            console.error('Export configuration error:', error);
            showNotification('Error exporting configuration: ' + error.message, 'error');
        }
    },

    /**
     * Copy configuration to clipboard
     */
    async copyToClipboard() {
        try {
            // Validate before copy
            if (typeof Validation !== 'undefined') {
                if (!Validation.validateBeforeSave()) {
                    showNotification('Please fix validation errors before copying', 'error');
                    return;
                }
            }

            // Get form data
            const config = ConfigForm.getFormData();
            if (!config) {
                throw new Error('Failed to get configuration data');
            }

            // Convert to JSON
            const jsonString = JSON.stringify(config, null, 2);

            // Copy to clipboard
            await navigator.clipboard.writeText(jsonString);

            showNotification('Configuration copied to clipboard', 'success');
        } catch (error) {
            console.error('Copy to clipboard error:', error);
            showNotification('Error copying to clipboard: ' + error.message, 'error');
        }
    },

    /**
     * Show import dialog
     */
    showImportDialog() {
        const dialog = document.getElementById('import-config-dialog');
        const fileInput = document.getElementById('config-file-input');
        const jsonInput = document.getElementById('config-json-input');
        const errorDiv = document.getElementById('import-config-error');
        const validationResults = document.getElementById('import-validation-results');
        
        // Clear previous values
        fileInput.value = '';
        jsonInput.value = '';
        errorDiv.style.display = 'none';
        validationResults.style.display = 'none';
        
        // Show dialog
        dialog.style.display = 'flex';
    },

    /**
     * Close import dialog
     */
    closeImportDialog() {
        const dialog = document.getElementById('import-config-dialog');
        dialog.style.display = 'none';
    },

    /**
     * Import configuration
     */
    async importConfiguration() {
        const errorDiv = document.getElementById('import-config-error');
        const validationResults = document.getElementById('import-validation-results');
        const validationContent = document.getElementById('import-validation-content');
        
        try {
            errorDiv.style.display = 'none';
            validationResults.style.display = 'none';

            // Get active import method
            const activeTab = document.querySelector('.import-method-tab.active');
            const method = activeTab.getAttribute('data-method');

            let configData = null;

            if (method === 'file') {
                // Import from file
                const fileInput = document.getElementById('config-file-input');
                const file = fileInput.files[0];
                
                if (!file) {
                    throw new Error('Please select a file to import');
                }

                // Read file
                const text = await this.readFileAsText(file);
                configData = JSON.parse(text);
            } else if (method === 'paste') {
                // Import from pasted JSON
                const jsonInput = document.getElementById('config-json-input');
                const jsonText = jsonInput.value.trim();
                
                if (!jsonText) {
                    throw new Error('Please paste configuration JSON');
                }

                configData = JSON.parse(jsonText);
            }

            if (!configData) {
                throw new Error('No configuration data to import');
            }

            // Validate imported configuration
            const validation = await this.validateImportedConfig(configData);
            
            if (!validation.valid) {
                // Show validation errors
                validationContent.innerHTML = `
                    <div class="validation-errors">
                        <h5>Validation Errors:</h5>
                        <ul>
                            ${validation.errors.map(err => `<li class="error">${err}</li>`).join('')}
                        </ul>
                    </div>
                `;
                validationResults.style.display = 'block';
                throw new Error('Configuration validation failed. Please fix the errors and try again.');
            }

            // Show validation warnings if any
            if (validation.warnings && validation.warnings.length > 0) {
                validationContent.innerHTML = `
                    <div class="validation-warnings">
                        <h5>Validation Warnings:</h5>
                        <ul>
                            ${validation.warnings.map(warn => `<li class="warning">${warn}</li>`).join('')}
                        </ul>
                        <p>Do you want to continue importing?</p>
                    </div>
                `;
                validationResults.style.display = 'block';
                
                // Ask for confirmation
                if (!confirm('Configuration has warnings. Do you want to continue importing?')) {
                    return;
                }
            }

            // Set form data
            if (typeof ConfigForm !== 'undefined') {
                ConfigForm.setFormData(configData);
            }

            // Update app state
            AppState.config.current = configData;
            AppState.config.isDirty = true;

            showNotification('Configuration imported successfully', 'success');
            this.closeImportDialog();

            // Switch to configuration tab if not already there
            const configTab = document.querySelector('[data-tab="configuration"]');
            if (configTab && !configTab.classList.contains('active')) {
                configTab.click();
            }
        } catch (error) {
            console.error('Import configuration error:', error);
            errorDiv.textContent = 'Error: ' + error.message;
            errorDiv.style.display = 'block';
        }
    },

    /**
     * Validate imported configuration
     */
    async validateImportedConfig(config) {
        try {
            // Use API validation endpoint
            const response = await api.validateConfig(config);
            
            if (response.success) {
                return {
                    valid: response.valid,
                    errors: response.errors || [],
                    warnings: response.warnings || []
                };
            } else {
                throw new Error(response.error || 'Validation failed');
            }
        } catch (error) {
            console.error('Validation error:', error);
            // Return basic validation if API fails
            return this.basicValidation(config);
        }
    },

    /**
     * Basic client-side validation
     */
    basicValidation(config) {
        const errors = [];
        const warnings = [];

        // Check required fields
        const requiredFields = ['broker', 'strategy', 'timeframe'];
        requiredFields.forEach(field => {
            if (!config[field]) {
                errors.push(`Missing required field: ${field}`);
            }
        });

        // Check instruments
        if (!config.instruments || !Array.isArray(config.instruments) || config.instruments.length === 0) {
            errors.push('At least one instrument is required');
        }

        // Check risk parameters
        if (config.risk_per_trade !== undefined) {
            const risk = parseFloat(config.risk_per_trade);
            if (isNaN(risk) || risk <= 0 || risk > 100) {
                errors.push('Risk per trade must be between 0 and 100');
            } else if (risk > 5) {
                warnings.push('Risk per trade above 5% is considered high');
            }
        }

        if (config.max_positions !== undefined) {
            const maxPos = parseInt(config.max_positions);
            if (isNaN(maxPos) || maxPos <= 0) {
                errors.push('Max positions must be a positive integer');
            } else if (maxPos > 10) {
                warnings.push('More than 10 positions may be difficult to manage');
            }
        }

        return {
            valid: errors.length === 0,
            errors,
            warnings
        };
    },

    /**
     * Read file as text
     */
    readFileAsText(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            
            reader.onload = (e) => {
                resolve(e.target.result);
            };
            
            reader.onerror = (e) => {
                reject(new Error('Failed to read file'));
            };
            
            reader.readAsText(file);
        });
    },

    /**
     * Generate filename for export
     */
    generateFilename() {
        const now = new Date();
        const year = now.getFullYear();
        const month = String(now.getMonth() + 1).padStart(2, '0');
        const day = String(now.getDate()).padStart(2, '0');
        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');
        const seconds = String(now.getSeconds()).padStart(2, '0');
        
        return `${year}${month}${day}_${hours}${minutes}${seconds}`;
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
    document.addEventListener('DOMContentLoaded', () => ExportImport.init());
} else {
    ExportImport.init();
}
