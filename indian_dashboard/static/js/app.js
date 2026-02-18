/**
 * Main Application Logic for Indian Market Trading Dashboard
 */

// Tab management
function initTabs() {
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabName = button.dataset.tab;
            
            // Update buttons
            tabButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            
            // Update content
            tabContents.forEach(content => content.classList.remove('active'));
            document.getElementById(`${tabName}-tab`).classList.add('active');
            
            // Load tab data
            loadTabData(tabName);
        });
    });
}

function loadTabData(tabName) {
    switch (tabName) {
        case 'broker':
            loadBrokers();
            // Stop auto-refresh when leaving monitor tab
            AutoRefresh.stop();
            break;
        case 'instruments':
            loadInstruments();
            // Stop auto-refresh when leaving monitor tab
            AutoRefresh.stop();
            break;
        case 'configuration':
            loadPresets();
            // Refresh selected instruments display when switching to configuration tab
            if (typeof ConfigForm !== 'undefined' && ConfigForm.refreshSelectedInstruments) {
                ConfigForm.refreshSelectedInstruments();
            }
            // Stop auto-refresh when leaving monitor tab
            AutoRefresh.stop();
            break;
        case 'monitor':
            loadMonitorData();
            // Start auto-refresh when entering monitor tab
            AutoRefresh.start();
            break;
        case 'trades':
            loadTrades();
            // Stop auto-refresh when leaving monitor tab
            AutoRefresh.stop();
            break;
    }
}

// Broker tab
async function loadBrokers() {
    try {
        const response = await api.getBrokers();
        const brokerList = document.getElementById('broker-list');
        const currentStatus = await api.getBrokerStatus();
        const connectedBroker = currentStatus.status.connected ? currentStatus.status.broker : null;
        
        brokerList.innerHTML = '';
        
        response.brokers.forEach(broker => {
            const isConnected = broker.id === connectedBroker;
            const card = document.createElement('div');
            card.className = 'broker-card';
            if (isConnected) {
                card.classList.add('connected');
            }
            card.dataset.broker = broker.id;
            
            // Create broker logo (placeholder if image doesn't exist)
            const logoHtml = `<div class="broker-logo" style="display: flex; align-items: center; justify-content: center; font-size: 2rem; font-weight: bold; color: var(--primary-color);">
                ${broker.name.substring(0, 2).toUpperCase()}
            </div>`;
            
            card.innerHTML = `
                <div class="broker-status-indicator ${isConnected ? 'connected' : ''}"></div>
                ${logoHtml}
                <div class="broker-name">${broker.name}</div>
                ${broker.oauth_enabled ? '<span class="broker-oauth-badge">OAuth</span>' : ''}
            `;
            
            // Disable selection if already connected to a different broker
            if (connectedBroker && !isConnected) {
                card.classList.add('disabled');
                card.title = 'Disconnect from current broker to select this one';
            } else {
                card.addEventListener('click', () => selectBroker(broker));
            }
            
            brokerList.appendChild(card);
        });
        
        // Show/hide change broker button based on connection status
        if (connectedBroker) {
            dom.show('change-broker-section');
            dom.show('connection-status');
        } else {
            dom.hide('change-broker-section');
            dom.hide('connection-status');
        }
        
        // Check current status
        updateBrokerStatus();
    } catch (error) {
        notifications.error('Failed to load brokers: ' + error.message);
    }
}

async function selectBroker(broker) {
    try {
        // Check if already connected to a different broker
        const currentStatus = await api.getBrokerStatus();
        if (currentStatus.status.connected && currentStatus.status.broker !== broker.id) {
            notifications.error('Please disconnect from current broker first');
            return;
        }
        
        // Highlight selected
        document.querySelectorAll('.broker-card').forEach(card => {
            card.classList.remove('selected');
        });
        const selectedCard = document.querySelector(`[data-broker="${broker.id}"]`);
        if (selectedCard) {
            selectedCard.classList.add('selected');
        }
        
        // Load credentials form using the new CredentialsForm module
        const response = await api.getCredentialsForm(broker.id);
        const formContainer = document.getElementById('credentials-form');
        
        // Generate dynamic form with validation and tooltips
        CredentialsForm.generate(broker.id, response.fields, formContainer);
        
        dom.show('credentials-section');
        
        // Setup connect button with validation
        document.getElementById('connect-btn').onclick = () => connectBroker();
    } catch (error) {
        notifications.error('Failed to load credentials form: ' + error.message);
    }
}

async function connectBroker() {
    const formContainer = document.getElementById('credentials-form');
    const broker = formContainer.dataset.broker;
    
    // Validate form before submitting
    if (!CredentialsForm.validateForm(formContainer)) {
        notifications.error('Please fix the errors in the form');
        return;
    }
    
    // Collect form data
    const credentials = CredentialsForm.getFormData(formContainer);
    
    try {
        // Show connection progress
        loading.show('connect-btn');
        notifications.info('Connecting to ' + broker + '...');
        
        const response = await api.connectBroker(broker, credentials);
        
        // Display success with user info
        if (response.user_info && response.user_info.user_id) {
            notifications.success(`Connected to ${broker} as ${response.user_info.user_id}`);
        } else {
            notifications.success('Connected to ' + broker);
        }
        
        appState.setBrokerConnected(true, broker, response.user_info);
        
        dom.hide('credentials-section');
        dom.show('connection-status');
        dom.show('change-broker-section');
        
        // Clear form
        CredentialsForm.clear(formContainer);
        
        // Reload brokers to update UI
        await loadBrokers();
        await updateBrokerStatus();
        
        // Display user info in connection status
        displayUserInfo(response.user_info);
        
    } catch (error) {
        // Handle connection errors with detailed messages
        const errorMsg = error.message || error.error || 'Unknown error';
        let errorMessage = 'Connection failed: ' + errorMsg;
        
        // Provide helpful error messages based on error type
        if (errorMsg.includes('credentials')) {
            errorMessage = 'Invalid credentials. Please check your API key and secret.';
        } else if (errorMsg.includes('network') || errorMsg.includes('timeout')) {
            errorMessage = 'Network error. Please check your internet connection.';
        } else if (errorMsg.includes('token')) {
            errorMessage = 'Authentication token error. Please try logging in again.';
        }
        
        notifications.error(errorMessage);
        console.error('Connection error details:', error);
    } finally {
        loading.hide('connect-btn');
    }
}

async function testConnection() {
    try {
        // Show test progress
        loading.show('test-connection-btn');
        notifications.info('Testing connection...');
        
        const response = await api.testConnection();
        
        if (response.success) {
            notifications.success('Connection test successful: ' + response.message);
            
            // Refresh status to show latest info
            await updateBrokerStatus();
        } else {
            notifications.error('Connection test failed: ' + response.message);
        }
        
    } catch (error) {
        notifications.error('Connection test failed: ' + error.message);
        console.error('Test connection error:', error);
    } finally {
        loading.hide('test-connection-btn');
    }
}

function displayUserInfo(userInfo) {
    // After connection, update the full broker status display
    updateBrokerStatus();
}

async function disconnectBroker() {
    try {
        await api.disconnectBroker();
        notifications.success('Disconnected from broker');
        appState.setBrokerConnected(false);
        
        dom.hide('connection-status');
        dom.hide('change-broker-section');
        dom.show('credentials-section');
        
        // Reload brokers to update UI
        await loadBrokers();
        updateBrokerStatus();
    } catch (error) {
        notifications.error('Disconnect failed: ' + error.message);
    }
}

function changeBroker() {
    // Show confirmation dialog
    if (confirm('Are you sure you want to change broker? This will disconnect your current broker.')) {
        disconnectBroker();
    }
}

async function updateBrokerStatus() {
    try {
        const response = await api.getBrokerStatus();
        const statusBadge = document.getElementById('broker-status');
        
        if (response.status.connected) {
            statusBadge.textContent = `Connected: ${response.status.broker}`;
            statusBadge.className = 'status-badge connected';
            
            // Display comprehensive broker status
            displayBrokerStatus(response.status);
            
            dom.show('connection-status');
            
            // Show test connection button in the connection status card
            const testBtn = document.getElementById('test-connection-btn');
            if (testBtn) {
                testBtn.style.display = 'inline-block';
            }
        } else {
            statusBadge.textContent = 'Not Connected';
            statusBadge.className = 'status-badge';
            
            // Hide test connection button when not connected
            const testBtn = document.getElementById('test-connection-btn');
            if (testBtn) {
                testBtn.style.display = 'none';
            }
        }
    } catch (error) {
        console.error('Failed to update broker status:', error);
    }
}

function displayBrokerStatus(status) {
    const info = document.getElementById('connection-info');
    
    // Get broker display name
    const brokerNames = {
        'kite': 'Zerodha Kite',
        'alice_blue': 'Alice Blue',
        'angel_one': 'Angel One',
        'upstox': 'Upstox',
        'paper': 'Paper Trading'
    };
    const brokerDisplayName = brokerNames[status.broker] || status.broker.toUpperCase();
    
    // Get user display name
    const userInfo = status.user_info || {};
    const userName = userInfo.user_name || userInfo.user_id || 'N/A';
    const userId = userInfo.user_id || 'N/A';
    
    // Format connection time
    const connectionTime = status.connection_time 
        ? formatters.datetime(status.connection_time)
        : 'Unknown';
    
    // Calculate connection duration
    let connectionDuration = '';
    if (status.connection_time) {
        const connectedAt = new Date(status.connection_time);
        const now = new Date();
        const durationMs = now - connectedAt;
        const hours = Math.floor(durationMs / (1000 * 60 * 60));
        const minutes = Math.floor((durationMs % (1000 * 60 * 60)) / (1000 * 60));
        
        if (hours > 0) {
            connectionDuration = `${hours}h ${minutes}m`;
        } else {
            connectionDuration = `${minutes}m`;
        }
    }
    
    // Build status display HTML
    let statusHTML = `
        <div class="status-header">
            <div class="status-icon">✓</div>
            <div class="status-title">
                <h4>Connected to ${brokerDisplayName}</h4>
                <p><span class="connection-indicator">Active Connection</span></p>
            </div>
        </div>
        
        <div class="status-grid">
            <div class="status-item">
                <div class="status-item-label">Broker</div>
                <div class="status-item-value broker-name">${brokerDisplayName}</div>
            </div>
            
            <div class="status-item">
                <div class="status-item-label">User ID</div>
                <div class="status-item-value">${userId}</div>
            </div>
    `;
    
    // Add user name if different from user ID
    if (userName !== userId && userName !== 'N/A') {
        statusHTML += `
            <div class="status-item">
                <div class="status-item-label">User Name</div>
                <div class="status-item-value">${userName}</div>
            </div>
        `;
    }
    
    statusHTML += `
            <div class="status-item">
                <div class="status-item-label">Connected At</div>
                <div class="status-item-value">${connectionTime}</div>
            </div>
    `;
    
    // Add connection duration
    if (connectionDuration) {
        statusHTML += `
            <div class="status-item">
                <div class="status-item-label">Duration</div>
                <div class="status-item-value">${connectionDuration}</div>
            </div>
        `;
    }
    
    // Add email if available
    if (userInfo.email) {
        statusHTML += `
            <div class="status-item">
                <div class="status-item-label">Email</div>
                <div class="status-item-value">${userInfo.email}</div>
            </div>
        `;
    }
    
    // Show token expiry if available (for OAuth connections)
    if (status.token_expiry) {
        const expiryDate = new Date(status.token_expiry);
        const now = new Date();
        const hoursUntilExpiry = (expiryDate - now) / (1000 * 60 * 60);
        
        let expiryClass = '';
        let expiryStatus = '';
        if (hoursUntilExpiry < 0) {
            expiryClass = 'expired';
            expiryStatus = ' (EXPIRED)';
        } else if (hoursUntilExpiry < 1) {
            expiryClass = 'warning';
            expiryStatus = ' (Expiring soon!)';
        } else if (hoursUntilExpiry < 6) {
            expiryClass = 'warning';
            expiryStatus = ' (Expires soon)';
        }
        
        statusHTML += `
            <div class="status-item">
                <div class="status-item-label">Token Expiry</div>
                <div class="status-item-value">
                    <div class="token-expiry ${expiryClass}">
                        ${formatters.datetime(status.token_expiry)}${expiryStatus}
                    </div>
                </div>
            </div>
        `;
    }
    
    statusHTML += `
        </div>
    `;
    
    info.innerHTML = statusHTML;
}

// Instruments tab
async function loadInstruments() {
    if (!appState.get('broker.connected')) {
        notifications.error('Please connect to a broker first');
        return;
    }
    
    try {
        // Show loading indicator
        showInstrumentsLoading(true);
        
        const filters = appState.get('instruments.filters');
        const response = await api.getInstruments(filters);
        
        appState.setAllInstruments(response.instruments);
        renderInstruments();
        
        // Update cache timestamp display
        if (response.cache_info) {
            updateCacheTimestamp(response.cache_info);
        }
    } catch (error) {
        notifications.error('Failed to load instruments: ' + error.message);
    } finally {
        // Hide loading indicator
        showInstrumentsLoading(false);
    }
}

function updateCacheTimestamp(cacheInfo) {
    // Find or create cache timestamp display
    let timestampDisplay = document.getElementById('cache-timestamp-display');
    
    if (!timestampDisplay) {
        // Create timestamp display element
        const toolbar = document.querySelector('.instruments-toolbar');
        if (toolbar) {
            timestampDisplay = document.createElement('div');
            timestampDisplay.id = 'cache-timestamp-display';
            timestampDisplay.className = 'cache-timestamp';
            toolbar.appendChild(timestampDisplay);
        }
    }
    
    if (timestampDisplay && cacheInfo) {
        if (cacheInfo.exists && cacheInfo.timestamp) {
            const timestamp = formatters.datetime(cacheInfo.timestamp);
            const ageMinutes = Math.floor(cacheInfo.age_seconds / 60);
            const ageHours = Math.floor(ageMinutes / 60);
            
            let ageText = '';
            if (ageHours > 0) {
                ageText = `${ageHours}h ago`;
            } else if (ageMinutes > 0) {
                ageText = `${ageMinutes}m ago`;
            } else {
                ageText = 'just now';
            }
            
            const validClass = cacheInfo.valid ? 'valid' : 'expired';
            timestampDisplay.innerHTML = `
                <span class="cache-status ${validClass}">
                    <span class="cache-icon">🕐</span>
                    Last updated: ${ageText}
                    <span class="cache-tooltip">${timestamp}</span>
                </span>
            `;
            timestampDisplay.style.display = 'block';
        } else {
            timestampDisplay.style.display = 'none';
        }
    }
}

// Search functionality with debouncing
let searchDebounceTimer = null;

function initInstrumentSearch() {
    const searchInput = document.getElementById('instrument-search');
    
    searchInput.addEventListener('input', (e) => {
        const searchTerm = e.target.value.trim();
        
        // Clear previous timer
        if (searchDebounceTimer) {
            clearTimeout(searchDebounceTimer);
        }
        
        // Debounce search - wait 300ms after user stops typing
        searchDebounceTimer = setTimeout(() => {
            performSearch(searchTerm);
        }, 300);
    });
    
    // Clear search on escape key
    searchInput.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            searchInput.value = '';
            performSearch('');
        }
    });
}

// Filter functionality
function initInstrumentFilters() {
    // Exchange filters
    const exchangeFilters = document.querySelectorAll('input[name="exchange"]');
    exchangeFilters.forEach(checkbox => {
        checkbox.addEventListener('change', () => {
            applyFilters();
        });
    });
    
    // Type filters
    const typeFilters = document.querySelectorAll('input[name="type"]');
    typeFilters.forEach(checkbox => {
        checkbox.addEventListener('change', () => {
            applyFilters();
        });
    });
    
    // Clear filters button
    const clearFiltersBtn = document.getElementById('clear-filters-btn');
    if (clearFiltersBtn) {
        clearFiltersBtn.addEventListener('click', clearFilters);
    }
}

function applyFilters() {
    // Get selected exchanges
    const exchangeCheckboxes = document.querySelectorAll('input[name="exchange"]:checked');
    const selectedExchanges = Array.from(exchangeCheckboxes).map(cb => cb.value);
    
    // Get selected types
    const typeCheckboxes = document.querySelectorAll('input[name="type"]:checked');
    const selectedTypes = Array.from(typeCheckboxes).map(cb => cb.value);
    
    // Update state
    const filters = appState.get('instruments.filters') || {};
    filters.exchange = selectedExchanges;
    filters.type = selectedTypes;
    appState.set('instruments.filters', filters);
    
    // Apply filters to instruments
    filterInstruments();
    
    // Update active filters display
    updateActiveFiltersDisplay();
    
    // Reset to first page
    const pagination = appState.get('instruments.pagination');
    pagination.page = 1;
    appState.set('instruments.pagination', pagination);
    
    // Re-render table
    renderInstruments();
}

function filterInstruments() {
    const allInstruments = appState.get('instruments.all') || [];
    const filters = appState.get('instruments.filters') || {};
    
    let filtered = allInstruments;
    
    // Apply exchange filter
    if (filters.exchange && filters.exchange.length > 0) {
        filtered = filtered.filter(inst => 
            filters.exchange.includes(inst.exchange)
        );
    }
    
    // Apply type filter
    if (filters.type && filters.type.length > 0) {
        filtered = filtered.filter(inst => 
            filters.type.includes(inst.instrument_type)
        );
    }
    
    // Apply search filter
    if (filters.search) {
        const searchLower = filters.search.toLowerCase();
        filtered = filtered.filter(inst => {
            const symbol = (inst.symbol || '').toLowerCase();
            const name = (inst.name || '').toLowerCase();
            return symbol.includes(searchLower) || name.includes(searchLower);
        });
    }
    
    appState.setInstruments(filtered);
}

function clearFilters() {
    // Uncheck all filter checkboxes
    const allCheckboxes = document.querySelectorAll('input[name="exchange"], input[name="type"]');
    allCheckboxes.forEach(cb => cb.checked = false);
    
    // Clear search input
    const searchInput = document.getElementById('instrument-search');
    if (searchInput) {
        searchInput.value = '';
    }
    
    // Reset filters in state
    const filters = {
        search: '',
        exchange: [],
        type: []
    };
    appState.set('instruments.filters', filters);
    
    // Reset instruments to show all
    const allInstruments = appState.get('instruments.all') || [];
    appState.setInstruments(allInstruments);
    
    // Update active filters display
    updateActiveFiltersDisplay();
    
    // Reset to first page
    const pagination = appState.get('instruments.pagination');
    pagination.page = 1;
    appState.set('instruments.pagination', pagination);
    
    // Re-render table
    renderInstruments();
}

function updateActiveFiltersDisplay() {
    const filters = appState.get('instruments.filters') || {};
    const activeFiltersContainer = document.getElementById('active-filters');
    
    if (!activeFiltersContainer) {
        return;
    }
    
    // Count active filters
    const activeCount = (filters.exchange?.length || 0) + (filters.type?.length || 0);
    
    // Clear container
    activeFiltersContainer.innerHTML = '';
    
    if (activeCount === 0 && !filters.search) {
        activeFiltersContainer.style.display = 'none';
        return;
    }
    
    activeFiltersContainer.style.display = 'flex';
    
    // Add label
    const label = document.createElement('span');
    label.className = 'active-filters-label';
    label.textContent = 'Active Filters:';
    activeFiltersContainer.appendChild(label);
    
    // Add exchange filters
    if (filters.exchange && filters.exchange.length > 0) {
        filters.exchange.forEach(exchange => {
            const tag = createFilterTag('Exchange', exchange, () => {
                removeFilter('exchange', exchange);
            });
            activeFiltersContainer.appendChild(tag);
        });
    }
    
    // Add type filters
    if (filters.type && filters.type.length > 0) {
        filters.type.forEach(type => {
            const typeLabel = getTypeLabel(type);
            const tag = createFilterTag('Type', typeLabel, () => {
                removeFilter('type', type);
            });
            activeFiltersContainer.appendChild(tag);
        });
    }
    
    // Add search filter
    if (filters.search) {
        const tag = createFilterTag('Search', filters.search, () => {
            const searchInput = document.getElementById('instrument-search');
            if (searchInput) {
                searchInput.value = '';
            }
            performSearch('');
        });
        activeFiltersContainer.appendChild(tag);
    }
}

function createFilterTag(category, value, onRemove) {
    const tag = document.createElement('div');
    tag.className = 'filter-tag';
    tag.innerHTML = `
        <span class="filter-tag-category">${category}:</span>
        <span class="filter-tag-value">${value}</span>
        <button class="filter-tag-remove" aria-label="Remove filter">&times;</button>
    `;
    
    tag.querySelector('.filter-tag-remove').addEventListener('click', onRemove);
    
    return tag;
}

function removeFilter(filterType, value) {
    const filters = appState.get('instruments.filters') || {};
    
    if (filterType === 'exchange') {
        filters.exchange = filters.exchange.filter(e => e !== value);
        // Uncheck the checkbox
        const checkbox = document.querySelector(`input[name="exchange"][value="${value}"]`);
        if (checkbox) checkbox.checked = false;
    } else if (filterType === 'type') {
        filters.type = filters.type.filter(t => t !== value);
        // Uncheck the checkbox
        const checkbox = document.querySelector(`input[name="type"][value="${value}"]`);
        if (checkbox) checkbox.checked = false;
    }
    
    appState.set('instruments.filters', filters);
    filterInstruments();
    updateActiveFiltersDisplay();
    renderInstruments();
}

function getTypeLabel(type) {
    const labels = {
        'EQ': 'Equity',
        'FUT': 'Futures',
        'CE': 'Call',
        'PE': 'Put'
    };
    return labels[type] || type;
}

function performSearch(searchTerm) {
    // Update state with search term
    const filters = appState.get('instruments.filters') || {};
    filters.search = searchTerm;
    appState.set('instruments.filters', filters);
    
    // Apply all filters (including search)
    filterInstruments();
    
    // Update active filters display
    updateActiveFiltersDisplay();
    
    // Reset to first page when searching
    const pagination = appState.get('instruments.pagination');
    pagination.page = 1;
    appState.set('instruments.pagination', pagination);
    
    // Re-render table
    renderInstruments();
}

function highlightSearchMatch(text, searchTerm) {
    if (!searchTerm || !text) {
        return text || '';
    }
    
    // Escape special regex characters in search term
    const escapedTerm = searchTerm.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    
    // Create case-insensitive regex
    const regex = new RegExp(`(${escapedTerm})`, 'gi');
    
    // Replace matches with highlighted span
    return text.replace(regex, '<mark class="search-highlight">$1</mark>');
}

function showInstrumentsLoading(show) {
    const loadingIndicator = document.getElementById('instruments-loading');
    const table = document.getElementById('instruments-table');
    
    if (show) {
        loadingIndicator.style.display = 'flex';
        table.style.opacity = '0.3';
    } else {
        loadingIndicator.style.display = 'none';
        table.style.opacity = '1';
    }
}

function renderInstruments() {
    const instruments = appState.get('instruments.list');
    const tbody = document.getElementById('instruments-tbody');
    const pagination = appState.get('instruments.pagination');
    const searchTerm = appState.get('instruments.filters')?.search || '';
    
    const start = (pagination.page - 1) * pagination.perPage;
    const end = start + pagination.perPage;
    const pageInstruments = instruments.slice(start, end);
    
    tbody.innerHTML = '';
    
    if (pageInstruments.length === 0) {
        const noResultsMessage = searchTerm 
            ? `No instruments found matching "${searchTerm}"`
            : 'No instruments found';
        tbody.innerHTML = `<tr><td colspan="6" style="text-align: center; padding: 2rem; color: var(--text-muted);">${noResultsMessage}</td></tr>`;
        return;
    }
    
    pageInstruments.forEach(inst => {
        const row = document.createElement('tr');
        const isSelected = appState.get('instruments.selected').some(i => i.token === inst.token);
        
        // Add selected class to row
        if (isSelected) {
            row.classList.add('selected-row');
        }
        
        // Format price
        const priceDisplay = inst.last_price 
            ? formatters.currency(inst.last_price) 
            : '--';
        
        // Highlight search matches in symbol and name
        const highlightedSymbol = highlightSearchMatch(inst.symbol || '--', searchTerm);
        const highlightedName = highlightSearchMatch(inst.name || '--', searchTerm);
        
        row.innerHTML = `
            <td><input type="checkbox" ${isSelected ? 'checked' : ''} data-token="${inst.token}"></td>
            <td>${highlightedSymbol}</td>
            <td>${highlightedName}</td>
            <td>${inst.exchange || '--'}</td>
            <td>${inst.instrument_type || '--'}</td>
            <td>${priceDisplay}</td>
        `;
        
        row.querySelector('input').addEventListener('change', (e) => {
            if (e.target.checked) {
                appState.addSelectedInstrument(inst);
            } else {
                appState.removeSelectedInstrument(inst.token);
            }
            updateSelectedInstruments();
        });
        
        tbody.appendChild(row);
    });
    
    updatePaginationInfo();
}

function updatePaginationInfo() {
    const instruments = appState.get('instruments.list');
    const pagination = appState.get('instruments.pagination');
    const totalPages = Math.ceil(instruments.length / pagination.perPage);
    
    document.getElementById('page-info').textContent = 
        `Page ${pagination.page} of ${totalPages || 1}`;
    
    // Enable/disable pagination buttons
    const prevBtn = document.getElementById('prev-page');
    const nextBtn = document.getElementById('next-page');
    
    prevBtn.disabled = pagination.page <= 1;
    nextBtn.disabled = pagination.page >= totalPages;
}

function updateSelectAllCheckbox() {
    const selectAllCheckbox = document.getElementById('select-all');
    const instruments = appState.get('instruments.list');
    const pagination = appState.get('instruments.pagination');
    const start = (pagination.page - 1) * pagination.perPage;
    const end = start + pagination.perPage;
    const pageInstruments = instruments.slice(start, end);
    const selected = appState.get('instruments.selected');
    
    if (pageInstruments.length === 0) {
        selectAllCheckbox.checked = false;
        selectAllCheckbox.indeterminate = false;
        return;
    }
    
    // Check how many instruments on current page are selected
    const selectedOnPage = pageInstruments.filter(inst => 
        selected.some(s => s.token === inst.token)
    ).length;
    
    if (selectedOnPage === 0) {
        selectAllCheckbox.checked = false;
        selectAllCheckbox.indeterminate = false;
    } else if (selectedOnPage === pageInstruments.length) {
        selectAllCheckbox.checked = true;
        selectAllCheckbox.indeterminate = false;
    } else {
        selectAllCheckbox.checked = false;
        selectAllCheckbox.indeterminate = true;
    }
}

function initInstrumentSorting() {
    const sortableHeaders = document.querySelectorAll('#instruments-table th.sortable');
    
    sortableHeaders.forEach(header => {
        header.addEventListener('click', () => {
            const sortField = header.dataset.sort;
            const currentSort = appState.get('instruments.sort');
            
            // Toggle sort direction
            let sortDirection = 'asc';
            if (currentSort.field === sortField && currentSort.direction === 'asc') {
                sortDirection = 'desc';
            }
            
            // Update sort state
            appState.set('instruments.sort', { field: sortField, direction: sortDirection });
            
            // Update UI
            sortableHeaders.forEach(h => {
                h.classList.remove('sort-asc', 'sort-desc');
            });
            header.classList.add(`sort-${sortDirection}`);
            
            // Sort instruments
            sortInstruments(sortField, sortDirection);
            
            // Re-render
            renderInstruments();
        });
    });
}

function sortInstruments(field, direction) {
    const instruments = appState.get('instruments.list');
    
    instruments.sort((a, b) => {
        let aVal = a[field];
        let bVal = b[field];
        
        // Handle null/undefined values
        if (aVal === null || aVal === undefined) aVal = '';
        if (bVal === null || bVal === undefined) bVal = '';
        
        // Convert to lowercase for string comparison
        if (typeof aVal === 'string') aVal = aVal.toLowerCase();
        if (typeof bVal === 'string') bVal = bVal.toLowerCase();
        
        // Compare
        if (aVal < bVal) return direction === 'asc' ? -1 : 1;
        if (aVal > bVal) return direction === 'asc' ? 1 : -1;
        return 0;
    });
    
    appState.setInstruments(instruments);
}

function updateSelectedInstruments() {
    const selected = appState.get('instruments.selected');
    const container = document.getElementById('selected-instruments');
    const clearAllBtn = document.getElementById('clear-all-selections-btn');
    const continueBtn = document.getElementById('continue-to-config-btn');
    
    // Update count
    document.getElementById('selected-count').textContent = selected.length;
    
    // Clear container
    container.innerHTML = '';
    
    if (selected.length === 0) {
        // Show empty state
        container.innerHTML = '<p style="color: var(--text-muted); text-align: center; padding: 1rem;">No instruments selected</p>';
        clearAllBtn.style.display = 'none';
        continueBtn.disabled = true;
    } else {
        // Show selected instruments
        selected.forEach(inst => {
            const tag = document.createElement('div');
            tag.className = 'selected-instrument-tag';
            tag.innerHTML = `
                <div class="instrument-info">
                    <span class="instrument-symbol">${inst.symbol}</span>
                    <span class="instrument-exchange">${inst.exchange}</span>
                </div>
                <button class="remove-instrument" data-token="${inst.token}" aria-label="Remove ${inst.symbol}">&times;</button>
            `;
            
            tag.querySelector('.remove-instrument').addEventListener('click', () => {
                appState.removeSelectedInstrument(inst.token);
                updateSelectedInstruments();
                renderInstruments();
            });
            
            container.appendChild(tag);
        });
        
        clearAllBtn.style.display = 'inline-block';
        continueBtn.disabled = false;
    }
    
    // Update select-all checkbox state
    updateSelectAllCheckbox();
}

// Configuration tab
async function loadPresets() {
    try {
        const response = await api.getPresets();
        const selector = document.getElementById('preset-selector');
        
        selector.innerHTML = '<option value="">-- Select Preset --</option>';
        response.presets.forEach(preset => {
            const option = document.createElement('option');
            option.value = preset.id;
            option.textContent = preset.name;
            selector.appendChild(option);
        });
        
        selector.addEventListener('change', (e) => {
            if (e.target.value) {
                loadPreset(e.target.value, response.presets);
            }
        });
    } catch (error) {
        notifications.error('Failed to load presets: ' + error.message);
    }
}

function loadPreset(presetId, presets) {
    const preset = presets.find(p => p.id === presetId);
    if (preset) {
        const form = document.getElementById('config-form');
        form.querySelector('[name="strategy"]').value = preset.config.strategy;
        form.querySelector('[name="timeframe"]').value = preset.config.timeframe;
        form.querySelector('[name="risk_per_trade"]').value = preset.config.risk_per_trade;
        form.querySelector('[name="max_positions"]').value = preset.config.max_positions;
        form.querySelector('[name="max_daily_loss"]').value = preset.config.max_daily_loss;
        
        notifications.info(`Loaded preset: ${preset.name}`);
    }
}

// Monitor tab
async function loadMonitorData() {
    await updateBotStatus();
    await updateAccountInfo();
    await updatePositions();
}

async function updateBotStatus() {
    try {
        const response = await api.getBotStatus();
        const statusBadge = document.getElementById('bot-status');
        const statusIndicator = document.getElementById('bot-status-indicator');
        const statusText = document.getElementById('bot-running-status');
        const uptimeText = document.getElementById('bot-uptime');
        const brokerStatusText = document.getElementById('bot-broker-status');
        const positionsCountText = document.getElementById('bot-positions-count');
        
        // Get broker status
        const brokerStatus = await api.getBrokerStatus();
        const brokerConnected = brokerStatus.status.connected;
        const brokerName = brokerStatus.status.broker || 'None';
        
        // Update bot running status
        if (response.status.running) {
            // Header badge
            statusBadge.textContent = 'Running';
            statusBadge.className = 'status-badge running';
            
            // Status indicator
            statusIndicator.className = 'bot-status-indicator running';
            statusIndicator.querySelector('.status-text').textContent = 'Running';
            
            // Status text
            statusText.textContent = 'Running';
            statusText.className = 'status-item-value running';
            
            // Uptime
            const uptimeSeconds = response.status.uptime_seconds || 0;
            uptimeText.textContent = formatters.uptime(uptimeSeconds);
            
            // Show/hide buttons
            dom.hide('start-bot-btn');
            dom.show('stop-bot-btn');
            dom.show('restart-bot-btn');
        } else {
            // Header badge
            statusBadge.textContent = 'Stopped';
            statusBadge.className = 'status-badge stopped';
            
            // Status indicator
            statusIndicator.className = 'bot-status-indicator';
            statusIndicator.querySelector('.status-text').textContent = 'Stopped';
            
            // Status text
            statusText.textContent = 'Stopped';
            statusText.className = 'status-item-value stopped';
            
            // Uptime
            uptimeText.textContent = '--';
            
            // Show/hide buttons
            dom.show('start-bot-btn');
            dom.hide('stop-bot-btn');
            dom.hide('restart-bot-btn');
        }
        
        // Update broker connection status
        if (brokerConnected) {
            brokerStatusText.textContent = `Connected (${brokerName})`;
            brokerStatusText.className = 'status-item-value connected';
        } else {
            brokerStatusText.textContent = 'Not Connected';
            brokerStatusText.className = 'status-item-value disconnected';
        }
        
        // Update positions count
        try {
            const positionsResponse = await api.getPositions();
            const positionsCount = positionsResponse.positions ? positionsResponse.positions.length : 0;
            positionsCountText.textContent = positionsCount;
        } catch (error) {
            positionsCountText.textContent = '0';
        }
        
        appState.setBotRunning(response.status.running);
    } catch (error) {
        console.error('Failed to update bot status:', error);
    }
}

async function updateAccountInfo() {
    try {
        const response = await api.getAccountInfo();
        const statusMessage = document.getElementById('account-status-message');
        
        if (response.success && response.account) {
            const account = response.account;
            
            // Update balance
            const balanceEl = document.getElementById('account-balance');
            balanceEl.textContent = formatters.currency(account.balance || 0);
            
            // Update equity
            const equityEl = document.getElementById('account-equity');
            equityEl.textContent = formatters.currency(account.equity || 0);
            
            // Update available margin
            const marginAvailableEl = document.getElementById('account-margin-available');
            marginAvailableEl.textContent = formatters.currency(account.margin_available || 0);
            
            // Update used margin
            const marginUsedEl = document.getElementById('account-margin-used');
            marginUsedEl.textContent = formatters.currency(account.margin_used || 0);
            
            // Update today's P&L
            const pnlTodayEl = document.getElementById('account-pnl-today');
            const pnlToday = account.pnl_today || 0;
            pnlTodayEl.textContent = formatters.currency(pnlToday);
            
            // Add positive/negative class for P&L
            pnlTodayEl.classList.remove('positive', 'negative');
            if (pnlToday > 0) {
                pnlTodayEl.classList.add('positive');
            } else if (pnlToday < 0) {
                pnlTodayEl.classList.add('negative');
            }
            
            // Update status message
            statusMessage.className = 'account-status-message success';
            statusMessage.innerHTML = `
                <span class="status-icon">✅</span>
                <span class="status-text">Account data updated successfully</span>
            `;
        } else {
            // No account data available
            resetAccountInfo();
            
            // Check if broker is connected
            const brokerStatus = await api.getBrokerStatus();
            if (!brokerStatus.status.connected) {
                statusMessage.className = 'account-status-message warning';
                statusMessage.innerHTML = `
                    <span class="status-icon">⚠️</span>
                    <span class="status-text">Connect to broker to view account information</span>
                `;
            } else {
                statusMessage.className = 'account-status-message error';
                statusMessage.innerHTML = `
                    <span class="status-icon">❌</span>
                    <span class="status-text">Account information not available</span>
                `;
            }
        }
    } catch (error) {
        console.error('Failed to update account info:', error);
        resetAccountInfo();
        
        const statusMessage = document.getElementById('account-status-message');
        statusMessage.className = 'account-status-message error';
        statusMessage.innerHTML = `
            <span class="status-icon">❌</span>
            <span class="status-text">Failed to fetch account information</span>
        `;
    }
}

function resetAccountInfo() {
    // Reset all account values to default
    document.getElementById('account-balance').textContent = '--';
    document.getElementById('account-equity').textContent = '--';
    document.getElementById('account-margin-available').textContent = '--';
    document.getElementById('account-margin-used').textContent = '--';
    
    const pnlTodayEl = document.getElementById('account-pnl-today');
    pnlTodayEl.textContent = '--';
    pnlTodayEl.classList.remove('positive', 'negative');
}

async function updatePositions() {
    try {
        const response = await api.getPositions();
        const tbody = document.getElementById('positions-tbody');
        
        tbody.innerHTML = '';
        
        // Check if there are positions
        if (!response.positions || response.positions.length === 0) {
            // Show empty state
            tbody.innerHTML = `
                <tr>
                    <td colspan="6" style="text-align: center; padding: 2rem; color: var(--text-muted);">
                        <div style="font-size: 3rem; margin-bottom: 1rem;">📊</div>
                        <div style="font-size: 1.1rem; margin-bottom: 0.5rem;">No Open Positions</div>
                        <div style="font-size: 0.9rem;">Positions will appear here when the bot opens trades</div>
                    </td>
                </tr>
            `;
            return;
        }
        
        // Calculate total P&L
        let totalPnL = 0;
        
        // Render each position
        response.positions.forEach(pos => {
            const row = document.createElement('tr');
            
            // Calculate P&L if not provided
            let pnl = pos.pnl || 0;
            if (pnl === 0 && pos.entry_price && pos.current_price && pos.quantity) {
                // Calculate P&L: (current_price - entry_price) * quantity
                pnl = (pos.current_price - pos.entry_price) * pos.quantity;
            }
            
            totalPnL += pnl;
            
            // Determine P&L class for styling
            const pnlClass = pnl >= 0 ? 'positive' : 'negative';
            
            // Format quantity with sign for long/short indication
            const quantityDisplay = pos.quantity > 0 ? `+${pos.quantity}` : pos.quantity;
            
            row.innerHTML = `
                <td><strong>${pos.symbol || '--'}</strong></td>
                <td>${quantityDisplay || '--'}</td>
                <td>${formatters.currency(pos.entry_price || 0)}</td>
                <td>${formatters.currency(pos.current_price || 0)}</td>
                <td class="${pnlClass}">${formatters.currency(pnl)}</td>
                <td>
                    <button class="btn btn-sm btn-danger" onclick="closePosition('${pos.symbol}')">
                        Close
                    </button>
                </td>
            `;
            
            tbody.appendChild(row);
        });
        
        // Add total P&L row
        const totalRow = document.createElement('tr');
        totalRow.className = 'total-row';
        const totalPnLClass = totalPnL >= 0 ? 'positive' : 'negative';
        
        totalRow.innerHTML = `
            <td colspan="4" style="text-align: right; font-weight: bold;">Total P&L:</td>
            <td class="${totalPnLClass}" style="font-weight: bold; font-size: 1.1rem;">
                ${formatters.currency(totalPnL)}
            </td>
            <td></td>
        `;
        
        tbody.appendChild(totalRow);
        
    } catch (error) {
        console.error('Failed to update positions:', error);
        
        // Show error state
        const tbody = document.getElementById('positions-tbody');
        tbody.innerHTML = `
            <tr>
                <td colspan="6" style="text-align: center; padding: 2rem; color: var(--error-color);">
                    <div style="font-size: 2rem; margin-bottom: 1rem;">⚠️</div>
                    <div>Failed to load positions</div>
                    <div style="font-size: 0.9rem; margin-top: 0.5rem;">${error.message}</div>
                </td>
            </tr>
        `;
    }
}

// Close position function
async function closePosition(symbol) {
    // Confirm before closing
    if (!confirm(`Are you sure you want to close the position for ${symbol}?`)) {
        return;
    }
    
    try {
        notifications.info(`Closing position for ${symbol}...`);
        
        const response = await api.closePosition(symbol);
        
        if (response.success) {
            notifications.success(response.message || `Position closed for ${symbol}`);
            
            // Refresh positions and account info
            await updatePositions();
            await updateAccountInfo();
            await updateBotStatus();
        } else {
            notifications.error(response.error || `Failed to close position for ${symbol}`);
        }
    } catch (error) {
        notifications.error(`Failed to close position: ${error.message}`);
        console.error('Close position error:', error);
    }
}

// Trades tab
async function loadTrades() {
    // Initialize TradeHistory module if not already done
    if (typeof TradeHistory !== 'undefined' && !TradeHistory._initialized) {
        TradeHistory.init();
        TradeHistory._initialized = true;
    }
    
    // Load trades using the TradeHistory module
    if (typeof TradeHistory !== 'undefined') {
        await TradeHistory.loadTrades();
    }
}

// Event handlers
document.addEventListener('DOMContentLoaded', () => {
    initTabs();
    loadBrokers();
    
    // Broker tab events
    document.getElementById('disconnect-btn').addEventListener('click', disconnectBroker);
    document.getElementById('change-broker-btn').addEventListener('click', changeBroker);
    
    // Test connection button
    const testConnectionBtn = document.getElementById('test-connection-btn');
    if (testConnectionBtn) {
        testConnectionBtn.addEventListener('click', testConnection);
    }
    
    // Instruments tab events
    document.getElementById('refresh-instruments-btn').addEventListener('click', async () => {
        try {
            // Show loading state
            loading.show('refresh-instruments-btn');
            showInstrumentsLoading(true);
            notifications.info('Refreshing instruments from broker...');
            
            // Refresh instruments
            const response = await api.refreshInstruments();
            
            // Reload instruments
            await loadInstruments();
            
            // Get updated cache info
            const cacheInfo = await api.getCacheInfo();
            
            // Show success with count and timestamp
            const timestamp = cacheInfo.cache_info?.timestamp 
                ? formatters.datetime(cacheInfo.cache_info.timestamp)
                : 'just now';
            notifications.success(`Refreshed ${response.count} instruments (updated: ${timestamp})`);
            
            // Update cache timestamp display
            updateCacheTimestamp(cacheInfo.cache_info);
            
        } catch (error) {
            notifications.error('Refresh failed: ' + error.message);
        } finally {
            loading.hide('refresh-instruments-btn');
            showInstrumentsLoading(false);
        }
    });
    
    document.getElementById('continue-to-config-btn').addEventListener('click', () => {
        // Switch to configuration tab
        document.querySelector('[data-tab="configuration"]').click();
        
        // Refresh selected instruments display
        if (typeof ConfigForm !== 'undefined' && ConfigForm.refreshSelectedInstruments) {
            ConfigForm.refreshSelectedInstruments();
        }
        
        // Show notification
        const selectedCount = appState.get('instruments.selected').length;
        notifications.success(`Switched to configuration with ${selectedCount} selected instruments`);
    });
    
    // Clear all selections button
    document.getElementById('clear-all-selections-btn').addEventListener('click', () => {
        const selected = appState.get('instruments.selected');
        const count = selected.length;
        
        if (confirm(`Are you sure you want to clear all ${count} selected instruments?`)) {
            appState.clearSelectedInstruments();
            updateSelectedInstruments();
            renderInstruments();
            notifications.success(`Cleared ${count} selected instruments`);
        }
    });
    
    // Pagination buttons
    document.getElementById('prev-page').addEventListener('click', () => {
        const pagination = appState.get('instruments.pagination');
        if (pagination.page > 1) {
            pagination.page--;
            appState.set('instruments.pagination', pagination);
            renderInstruments();
        }
    });
    
    document.getElementById('next-page').addEventListener('click', () => {
        const pagination = appState.get('instruments.pagination');
        const instruments = appState.get('instruments.list');
        const totalPages = Math.ceil(instruments.length / pagination.perPage);
        
        if (pagination.page < totalPages) {
            pagination.page++;
            appState.set('instruments.pagination', pagination);
            renderInstruments();
        }
    });
    
    // Select all checkbox
    document.getElementById('select-all').addEventListener('change', (e) => {
        const instruments = appState.get('instruments.list');
        const pagination = appState.get('instruments.pagination');
        const start = (pagination.page - 1) * pagination.perPage;
        const end = start + pagination.perPage;
        const pageInstruments = instruments.slice(start, end);
        
        if (e.target.checked) {
            // Select all on current page
            pageInstruments.forEach(inst => {
                appState.addSelectedInstrument(inst);
            });
            notifications.info(`Selected ${pageInstruments.length} instruments on this page`);
        } else {
            // Deselect all on current page
            pageInstruments.forEach(inst => {
                appState.removeSelectedInstrument(inst.token);
            });
            notifications.info('Cleared selections on this page');
        }
        
        updateSelectedInstruments();
        renderInstruments();
    });
    
    // Initialize sorting
    initInstrumentSorting();
    
    // Initialize search
    initInstrumentSearch();
    
    // Initialize filters
    initInstrumentFilters();
    
    // Configuration tab events
    document.getElementById('save-config-btn').addEventListener('click', async () => {
        const form = document.getElementById('config-form');
        const formData = new FormData(form);
        const config = Object.fromEntries(formData);
        config.instruments = appState.get('instruments.selected');
        
        try {
            await api.saveConfig(config);
            notifications.success('Configuration saved');
        } catch (error) {
            notifications.error('Save failed: ' + error.message);
        }
    });
    
    // Monitor tab events
    document.getElementById('start-bot-btn').addEventListener('click', async () => {
        const config = appState.get('config.current');
        if (!config || !config.instruments || config.instruments.length === 0) {
            notifications.error('Please configure the bot and select instruments first');
            return;
        }
        
        // Check if broker is connected
        const brokerStatus = await api.getBrokerStatus();
        if (!brokerStatus.status.connected) {
            notifications.error('Please connect to a broker first');
            return;
        }
        
        try {
            loading.show('start-bot-btn');
            notifications.info('Starting bot...');
            await api.startBot(config);
            notifications.success('Bot started successfully');
            await updateBotStatus();
        } catch (error) {
            notifications.error('Start failed: ' + error.message);
        } finally {
            loading.hide('start-bot-btn');
        }
    });
    
    document.getElementById('stop-bot-btn').addEventListener('click', async () => {
        if (!confirm('Are you sure you want to stop the bot?')) {
            return;
        }
        
        try {
            loading.show('stop-bot-btn');
            notifications.info('Stopping bot...');
            await api.stopBot();
            notifications.success('Bot stopped successfully');
            await updateBotStatus();
        } catch (error) {
            notifications.error('Stop failed: ' + error.message);
        } finally {
            loading.hide('stop-bot-btn');
        }
    });
    
    document.getElementById('restart-bot-btn').addEventListener('click', async () => {
        if (!confirm('Are you sure you want to restart the bot?')) {
            return;
        }
        
        try {
            loading.show('restart-bot-btn');
            notifications.info('Restarting bot...');
            await api.restartBot();
            notifications.success('Bot restarted successfully');
            await updateBotStatus();
        } catch (error) {
            notifications.error('Restart failed: ' + error.message);
        } finally {
            loading.hide('restart-bot-btn');
        }
    });
    
    // Manual refresh button
    document.getElementById('manual-refresh-btn').addEventListener('click', async () => {
        try {
            loading.show('manual-refresh-btn');
            notifications.info('Refreshing monitor data...');
            
            // Perform manual refresh
            await AutoRefresh.refresh();
            
            notifications.success('Monitor data refreshed');
        } catch (error) {
            notifications.error('Refresh failed: ' + error.message);
        } finally {
            loading.hide('manual-refresh-btn');
        }
    });
    
    // Trades tab events
    document.getElementById('filter-trades-btn').addEventListener('click', loadTrades);
});

// Auto-refresh functionality for Monitor tab
const AutoRefresh = {
    intervalId: null,
    refreshInterval: 5000, // 5 seconds
    isPaused: false,
    lastUpdated: null,
    
    start() {
        if (this.intervalId) {
            return; // Already running
        }
        
        this.isPaused = false;
        this.updateRefreshIndicator();
        
        this.intervalId = setInterval(() => {
            const activeTab = document.querySelector('.tab-content.active');
            
            // Only refresh if monitor tab is active and not paused
            if (activeTab && activeTab.id === 'monitor-tab' && !this.isPaused) {
                // Check if tab is visible (not minimized or in background)
                if (!document.hidden) {
                    this.refresh();
                }
            }
        }, this.refreshInterval);
    },
    
    stop() {
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
        this.updateRefreshIndicator();
    },
    
    pause() {
        this.isPaused = true;
        this.updateRefreshIndicator();
    },
    
    resume() {
        this.isPaused = false;
        this.updateRefreshIndicator();
    },
    
    async refresh() {
        try {
            // Update last updated timestamp
            this.lastUpdated = new Date();
            this.updateLastUpdatedDisplay();
            
            // Refresh monitor data
            await loadMonitorData();
            
        } catch (error) {
            console.error('Auto-refresh error:', error);
        }
    },
    
    updateRefreshIndicator() {
        const indicator = document.getElementById('account-refresh-indicator');
        if (!indicator) return;
        
        const refreshIcon = indicator.querySelector('.refresh-icon');
        const refreshText = indicator.querySelector('.refresh-text');
        
        if (this.isPaused) {
            indicator.className = 'account-refresh-indicator paused';
            refreshIcon.textContent = '⏸️';
            refreshText.textContent = 'Auto-refresh: Paused';
        } else if (this.intervalId) {
            indicator.className = 'account-refresh-indicator active';
            refreshIcon.textContent = '🔄';
            refreshText.textContent = `Auto-refresh: ${this.refreshInterval / 1000}s`;
        } else {
            indicator.className = 'account-refresh-indicator';
            refreshIcon.textContent = '⏹️';
            refreshText.textContent = 'Auto-refresh: Off';
        }
    },
    
    updateLastUpdatedDisplay() {
        const display = document.getElementById('last-updated-display');
        if (!display || !this.lastUpdated) return;
        
        const timeAgo = this.getTimeAgo(this.lastUpdated);
        display.textContent = `Last updated: ${timeAgo}`;
    },
    
    getTimeAgo(date) {
        const seconds = Math.floor((new Date() - date) / 1000);
        
        if (seconds < 10) return 'just now';
        if (seconds < 60) return `${seconds}s ago`;
        
        const minutes = Math.floor(seconds / 60);
        if (minutes < 60) return `${minutes}m ago`;
        
        const hours = Math.floor(minutes / 60);
        return `${hours}h ago`;
    }
};

// Update last updated display every second
setInterval(() => {
    if (AutoRefresh.lastUpdated) {
        AutoRefresh.updateLastUpdatedDisplay();
    }
}, 1000);

// Pause auto-refresh when tab becomes hidden
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        AutoRefresh.pause();
    } else {
        // Resume if monitor tab is active
        const activeTab = document.querySelector('.tab-content.active');
        if (activeTab && activeTab.id === 'monitor-tab') {
            AutoRefresh.resume();
        }
    }
});

// Start auto-refresh when page loads
AutoRefresh.start();
