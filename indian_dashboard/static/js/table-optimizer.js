/**
 * Table Rendering Optimizer
 * Optimizes large table rendering with virtual scrolling and batched updates
 */

class TableOptimizer {
    constructor(options = {}) {
        this.tableBody = options.tableBody;
        this.rowHeight = options.rowHeight || 50;
        this.buffer = options.buffer || 10;
        this.data = [];
        this.visibleRange = { start: 0, end: 0 };
        this.renderFunction = options.renderFunction;
        this.container = options.container;
        this.lastScrollTop = 0;
        this.scrollThrottle = 16; // ~60fps
        
        this.init();
    }

    init() {
        if (this.container) {
            // Throttle scroll handler for performance
            const throttledScroll = throttleAdvanced(
                this.handleScroll.bind(this),
                this.scrollThrottle
            );
            
            this.container.addEventListener('scroll', throttledScroll);
        }
    }

    setData(data) {
        this.data = data;
        this.updateVisibleRange();
        this.render();
    }

    updateVisibleRange() {
        if (!this.container) {
            // No virtual scrolling, show all
            this.visibleRange = { start: 0, end: this.data.length };
            return;
        }

        const containerHeight = this.container.clientHeight;
        const scrollTop = this.container.scrollTop;

        const startIndex = Math.max(
            0,
            Math.floor(scrollTop / this.rowHeight) - this.buffer
        );
        
        const visibleCount = Math.ceil(containerHeight / this.rowHeight);
        const endIndex = Math.min(
            this.data.length,
            startIndex + visibleCount + this.buffer * 2
        );

        this.visibleRange = { start: startIndex, end: endIndex };
    }

    handleScroll() {
        const scrollTop = this.container.scrollTop;
        const scrollDelta = Math.abs(scrollTop - this.lastScrollTop);

        // Only update if scrolled more than one row
        if (scrollDelta > this.rowHeight) {
            this.lastScrollTop = scrollTop;
            this.updateVisibleRange();
            this.render();
        }
    }

    render() {
        if (!this.tableBody || !this.renderFunction) {
            return;
        }

        const startTime = performance.now();

        // Get visible data
        const visibleData = this.data.slice(
            this.visibleRange.start,
            this.visibleRange.end
        );

        // Use document fragment for batch DOM updates
        const fragment = document.createDocumentFragment();

        // Render visible rows
        visibleData.forEach((item, index) => {
            const actualIndex = this.visibleRange.start + index;
            const row = this.renderFunction(item, actualIndex);
            fragment.appendChild(row);
        });

        // Clear and append in one operation
        this.tableBody.innerHTML = '';
        this.tableBody.appendChild(fragment);

        // Add spacer rows for virtual scrolling
        if (this.container) {
            this.addSpacers();
        }

        const duration = performance.now() - startTime;
        performanceMonitor.recordRenderTime(duration);
    }

    addSpacers() {
        const topSpacer = this.visibleRange.start * this.rowHeight;
        const bottomSpacer = (this.data.length - this.visibleRange.end) * this.rowHeight;

        if (topSpacer > 0) {
            const spacerRow = document.createElement('tr');
            spacerRow.style.height = `${topSpacer}px`;
            spacerRow.className = 'spacer-row';
            this.tableBody.insertBefore(spacerRow, this.tableBody.firstChild);
        }

        if (bottomSpacer > 0) {
            const spacerRow = document.createElement('tr');
            spacerRow.style.height = `${bottomSpacer}px`;
            spacerRow.className = 'spacer-row';
            this.tableBody.appendChild(spacerRow);
        }
    }

    updateRow(index, newData) {
        // Update data
        if (index >= 0 && index < this.data.length) {
            this.data[index] = newData;
            
            // Only re-render if row is visible
            if (index >= this.visibleRange.start && index < this.visibleRange.end) {
                this.render();
            }
        }
    }

    refresh() {
        this.render();
    }

    destroy() {
        if (this.container) {
            this.container.removeEventListener('scroll', this.handleScroll);
        }
    }
}

/**
 * Incremental Table Renderer
 * Renders large tables incrementally to avoid blocking UI
 */
class IncrementalTableRenderer {
    constructor(options = {}) {
        this.tableBody = options.tableBody;
        this.data = [];
        this.renderFunction = options.renderFunction;
        this.batchSize = options.batchSize || 50;
        this.delay = options.delay || 0;
        this.currentIndex = 0;
        this.isRendering = false;
        this.onComplete = options.onComplete;
    }

    setData(data) {
        this.data = data;
        this.currentIndex = 0;
    }

    async render() {
        if (this.isRendering) {
            return;
        }

        this.isRendering = true;
        this.currentIndex = 0;

        // Clear table
        this.tableBody.innerHTML = '';

        // Create fragment for batch updates
        let fragment = document.createDocumentFragment();
        let batchCount = 0;

        while (this.currentIndex < this.data.length) {
            const item = this.data[this.currentIndex];
            const row = this.renderFunction(item, this.currentIndex);
            fragment.appendChild(row);
            
            batchCount++;
            this.currentIndex++;

            // Append batch and yield to browser
            if (batchCount >= this.batchSize) {
                this.tableBody.appendChild(fragment);
                fragment = document.createDocumentFragment();
                batchCount = 0;

                // Yield to browser to keep UI responsive
                if (this.delay > 0) {
                    await new Promise(resolve => setTimeout(resolve, this.delay));
                } else {
                    await new Promise(resolve => requestAnimationFrame(resolve));
                }
            }
        }

        // Append remaining items
        if (batchCount > 0) {
            this.tableBody.appendChild(fragment);
        }

        this.isRendering = false;

        if (this.onComplete) {
            this.onComplete();
        }
    }

    cancel() {
        this.isRendering = false;
    }
}

/**
 * Smart Table Updater
 * Updates only changed rows instead of re-rendering entire table
 */
class SmartTableUpdater {
    constructor(options = {}) {
        this.tableBody = options.tableBody;
        this.renderFunction = options.renderFunction;
        this.keyFunction = options.keyFunction || ((item) => item.id);
        this.currentData = new Map();
    }

    update(newData) {
        const startTime = performance.now();
        
        const newDataMap = new Map();
        newData.forEach((item, index) => {
            const key = this.keyFunction(item);
            newDataMap.set(key, { item, index });
        });

        const rows = Array.from(this.tableBody.querySelectorAll('tr:not(.spacer-row)'));
        const updates = [];

        // Find rows to update or remove
        this.currentData.forEach((value, key) => {
            if (!newDataMap.has(key)) {
                // Row removed
                const row = rows[value.index];
                if (row) {
                    updates.push({ type: 'remove', row });
                }
            } else {
                const newValue = newDataMap.get(key);
                if (JSON.stringify(value.item) !== JSON.stringify(newValue.item)) {
                    // Row changed
                    const row = rows[value.index];
                    if (row) {
                        updates.push({ 
                            type: 'update', 
                            row, 
                            newItem: newValue.item,
                            index: newValue.index
                        });
                    }
                }
            }
        });

        // Find rows to add
        newDataMap.forEach((value, key) => {
            if (!this.currentData.has(key)) {
                updates.push({ 
                    type: 'add', 
                    item: value.item,
                    index: value.index
                });
            }
        });

        // Apply updates in batch
        domBatcher.add(() => {
            updates.forEach(update => {
                if (update.type === 'remove') {
                    update.row.remove();
                } else if (update.type === 'update') {
                    const newRow = this.renderFunction(update.newItem, update.index);
                    update.row.replaceWith(newRow);
                } else if (update.type === 'add') {
                    const newRow = this.renderFunction(update.item, update.index);
                    
                    // Insert at correct position
                    if (update.index < this.tableBody.children.length) {
                        this.tableBody.insertBefore(newRow, this.tableBody.children[update.index]);
                    } else {
                        this.tableBody.appendChild(newRow);
                    }
                }
            });
        });

        this.currentData = newDataMap;

        const duration = performance.now() - startTime;
        performanceMonitor.recordRenderTime(duration);
    }

    clear() {
        this.currentData.clear();
        this.tableBody.innerHTML = '';
    }
}

/**
 * Table Search Optimizer
 * Optimizes search with indexing and caching
 */
class TableSearchOptimizer {
    constructor(options = {}) {
        this.data = [];
        this.searchFields = options.searchFields || [];
        this.index = new Map();
        this.caseInsensitive = options.caseInsensitive !== false;
    }

    setData(data) {
        this.data = data;
        this.buildIndex();
    }

    buildIndex() {
        this.index.clear();

        this.data.forEach((item, idx) => {
            this.searchFields.forEach(field => {
                const value = item[field];
                if (value) {
                    const searchValue = this.caseInsensitive 
                        ? String(value).toLowerCase() 
                        : String(value);
                    
                    if (!this.index.has(searchValue)) {
                        this.index.set(searchValue, []);
                    }
                    this.index.get(searchValue).push(idx);
                }
            });
        });
    }

    search(query) {
        if (!query) {
            return this.data;
        }

        const searchQuery = this.caseInsensitive ? query.toLowerCase() : query;
        const matchedIndices = new Set();

        // Search in index
        this.index.forEach((indices, value) => {
            if (value.includes(searchQuery)) {
                indices.forEach(idx => matchedIndices.add(idx));
            }
        });

        // Return matched items
        return Array.from(matchedIndices)
            .sort((a, b) => a - b)
            .map(idx => this.data[idx]);
    }
}

// Export classes
window.TableOptimizer = TableOptimizer;
window.IncrementalTableRenderer = IncrementalTableRenderer;
window.SmartTableUpdater = SmartTableUpdater;
window.TableSearchOptimizer = TableSearchOptimizer;
