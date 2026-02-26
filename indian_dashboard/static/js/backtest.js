/**
 * Time Machine — Backtest & Forward Test UI
 * ==========================================
 * Manages both the "Backtest (Past)" and "Forward Test (Future)" sub-tabs.
 *
 * Dependencies: Chart.js (already loaded in dashboard)
 */

const TimeMachine = (() => {
    'use strict';

    // ----------------------------------------------------------------
    // State
    // ----------------------------------------------------------------
    let activeMode = 'backtest';           // 'backtest' | 'forward'
    let pollingInterval = null;
    let equityChart = null;
    let currentRunId = null;

    // ----------------------------------------------------------------
    // Initialisation (called once when tab first opens)
    // ----------------------------------------------------------------
    function init() {
        _bindSubtabSwitcher();
        _bindRunButton();
        _bindSymbolInput();
        loadResultsList();
    }

    // ----------------------------------------------------------------
    // Sub-tab switching
    // ----------------------------------------------------------------
    function _bindSubtabSwitcher() {
        document.querySelectorAll('.tm-subtab').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.tm-subtab').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                activeMode = btn.dataset.mode;
                _toggleModeUI(activeMode);
                loadResultsList();
            });
        });
    }

    function _toggleModeUI(mode) {
        const fromDateGroup = document.getElementById('tm-from-date-group');
        const toDateGroup = document.getElementById('tm-to-date-group');
        const hint = document.getElementById('tm-mode-hint');

        if (mode === 'backtest') {
            fromDateGroup.style.display = '';
            toDateGroup.style.display = '';
            hint.textContent = '📅 Backtest runs on historical data. Kite connection required for real data; falls back to simulated data otherwise.';
        } else {
            fromDateGroup.style.display = 'none';
            toDateGroup.style.display = 'none';
            hint.textContent = '🔮 Forward Test monitors your strategy on live paper-trading from today onward. Results accumulate in real time.';
        }
    }

    // ----------------------------------------------------------------
    // Symbol tag input
    // ----------------------------------------------------------------
    function _bindSymbolInput() {
        const input = document.getElementById('tm-symbol-input');
        if (!input) return;
        input.addEventListener('keydown', e => {
            if (e.key === 'Enter' || e.key === ',') {
                e.preventDefault();
                const val = input.value.trim().toUpperCase().replace(/,/g, '');
                if (val) _addSymbolTag(val);
                input.value = '';
            }
        });
    }

    function _addSymbolTag(symbol) {
        const container = document.getElementById('tm-symbol-tags');
        if (!container) return;
        // Avoid duplicates
        const existing = [...container.querySelectorAll('.tm-tag')].map(t => t.dataset.symbol);
        if (existing.includes(symbol)) return;

        const tag = document.createElement('span');
        tag.className = 'tm-tag';
        tag.dataset.symbol = symbol;
        tag.innerHTML = `${symbol} <button onclick="this.parentElement.remove()" title="Remove">×</button>`;
        container.appendChild(tag);
    }

    function _getSelectedSymbols() {
        return [...document.querySelectorAll('.tm-tag')].map(t => t.dataset.symbol);
    }

    // ----------------------------------------------------------------
    // Run
    // ----------------------------------------------------------------
    function _bindRunButton() {
        const btn = document.getElementById('tm-run-btn');
        if (!btn) return;
        btn.addEventListener('click', startRun);
    }

    async function startRun() {
        const symbols = _getSelectedSymbols();
        if (!symbols.length) {
            _showAlert('Add at least one symbol (e.g. RELIANCE)', 'warning');
            return;
        }

        const name = document.getElementById('tm-run-name')?.value || '';
        const fromDate = document.getElementById('tm-from-date')?.value || '';
        const toDate = document.getElementById('tm-to-date')?.value || new Date().toISOString().split('T')[0];
        const capital = parseFloat(document.getElementById('tm-capital')?.value || '500000');
        const configJSON = document.getElementById('tm-config-override')?.value?.trim() || '{}';

        if (activeMode === 'backtest' && !fromDate) {
            _showAlert('Please select a From Date for backtesting.', 'warning');
            return;
        }

        let extraConfig = {};
        try { extraConfig = JSON.parse(configJSON); } catch { /* ignore bad JSON */ }

        // Gather current dashboard configuration
        let dashboardConfig = {};
        if (typeof StrategyParameters !== 'undefined') {
            const params = StrategyParameters.getParameters();
            dashboardConfig = Object.assign(dashboardConfig, params);
        }

        // Merge: Base Defaults < Dashboard UI < Config Override
        const config = Object.assign({
            strategy: 'trend_following',
            timeframe: '15min'
        }, dashboardConfig, extraConfig);

        _setRunning(true);
        _showProgress(5, 'Submitting…');

        try {
            const body = { name, symbols, config, from_date: fromDate, to_date: toDate, initial_capital: capital, mode: activeMode };
            const res = await fetch('/api/backtest/run', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
            const json = await res.json();

            if (!json.success) throw new Error(json.error || 'Failed to start run');

            currentRunId = json.run_id;
            _showAlert(`Run started: ${json.name}`, 'info');
            _startPolling(json.run_id);
        } catch (err) {
            _showAlert('Error: ' + err.message, 'danger');
            _setRunning(false);
            _showProgress(0);
        }
    }

    // ----------------------------------------------------------------
    // Progress polling
    // ----------------------------------------------------------------
    function _startPolling(runId) {
        if (pollingInterval) clearInterval(pollingInterval);
        pollingInterval = setInterval(async () => {
            try {
                const res = await fetch(`/api/backtest/status/${runId}`);
                const json = await res.json();
                if (!json.success) return;

                const pct = json.pct || 0;
                _showProgress(pct, pct < 100 ? `Running… ${pct}%` : 'Done!');

                if (json.status === 'completed') {
                    clearInterval(pollingInterval);
                    _setRunning(false);
                    _showProgress(100, 'Completed ✓');
                    loadResultsList();
                    loadRunDetail(runId);
                } else if (json.status === 'failed') {
                    clearInterval(pollingInterval);
                    _setRunning(false);
                    _showProgress(0);
                    _showAlert('Run failed: ' + (json.error || 'Unknown error'), 'danger');
                    loadResultsList();
                }
            } catch { /* network hiccup — keep polling */ }
        }, 1500);
    }

    // ----------------------------------------------------------------
    // Results list
    // ----------------------------------------------------------------
    async function loadResultsList() {
        const tbody = document.getElementById('tm-results-tbody');
        if (!tbody) return;

        try {
            const res = await fetch(`/api/backtest/results?mode=${activeMode}`);
            const json = await res.json();
            if (!json.success) return;

            if (!json.runs.length) {
                tbody.innerHTML = `<tr><td colspan="8" class="text-center text-muted py-3">No ${activeMode === 'backtest' ? 'backtests' : 'forward tests'} yet.</td></tr>`;
                return;
            }

            tbody.innerHTML = json.runs.map(r => {
                const ret = r.total_return_pct != null ? r.total_return_pct.toFixed(2) : '—';
                const dd = r.max_drawdown_pct != null ? r.max_drawdown_pct.toFixed(2) : '—';
                const wr = r.win_rate != null ? r.win_rate.toFixed(1) : '—';
                const sh = r.sharpe_ratio != null ? r.sharpe_ratio.toFixed(2) : '—';
                const sym = Array.isArray(r.symbols) ? r.symbols.join(', ') : r.symbols;
                const statusBadge = _statusBadge(r.status);
                const retColor = parseFloat(ret) >= 0 ? 'text-success' : 'text-danger';
                return `
                <tr class="tm-result-row" onclick="TimeMachine.loadRunDetail('${r.id}')">
                    <td><small class="text-muted">${(r.created_at || '').slice(0, 16)}</small></td>
                    <td><strong>${_esc(r.name)}</strong></td>
                    <td><small>${_esc(sym)}</small></td>
                    <td class="${retColor} fw-bold">${ret}%</td>
                    <td class="text-warning fw-bold">-${dd}%</td>
                    <td>${wr}%</td>
                    <td>${sh}</td>
                    <td>${statusBadge}</td>
                    <td>
                        <button class="btn btn-xs btn-outline-primary" onclick="event.stopPropagation(); TimeMachine.exportRun('${r.id}','csv')">CSV</button>
                        <button class="btn btn-xs btn-outline-secondary" onclick="event.stopPropagation(); TimeMachine.exportRun('${r.id}','json')">JSON</button>
                        <button class="btn btn-xs btn-outline-danger" onclick="event.stopPropagation(); TimeMachine.deleteRun('${r.id}')">🗑</button>
                    </td>
                </tr>`;
            }).join('');
        } catch (err) {
            tbody.innerHTML = `<tr><td colspan="8" class="text-danger">Error loading results: ${err.message}</td></tr>`;
        }
    }

    // ----------------------------------------------------------------
    // Run detail — equity chart + trades + metrics
    // ----------------------------------------------------------------
    async function loadRunDetail(runId) {
        const panel = document.getElementById('tm-detail-panel');
        if (!panel) return;
        panel.style.display = '';
        panel.innerHTML = '<div class="text-center py-4"><div class="spinner-border text-primary"></div></div>';

        try {
            const res = await fetch(`/api/backtest/results/${runId}`);
            const json = await res.json();
            if (!json.success) throw new Error(json.error || 'Load failed');

            const r = json.result;
            panel.innerHTML = _buildDetailHTML(r);
            _renderEquityChart(r.equity_curve || []);
        } catch (err) {
            panel.innerHTML = `<div class="alert alert-danger">Error: ${err.message}</div>`;
        }
    }

    function _buildDetailHTML(r) {
        const retColor = r.total_return_pct >= 0 ? 'text-success' : 'text-danger';
        const symbols = Array.isArray(r.symbols) ? r.symbols.join(', ') : r.symbols;
        const period = r.mode === 'backtest' ? `${r.from_date} → ${r.to_date}` : `Forward from ${r.from_date}`;
        const capital = `₹${(r.initial_capital || 0).toLocaleString('en-IN')}`;
        const finalCap = `₹${(r.final_capital || 0).toLocaleString('en-IN')}`;

        const tradesHTML = (r.trades || []).slice(0, 100).map(t => {
            const pnlColor = t.pnl >= 0 ? 'text-success' : 'text-danger';
            return `
            <tr>
                <td>${_esc(t.symbol)}</td>
                <td><span class="badge ${t.direction === 'buy' ? 'bg-success' : 'bg-danger'}">${t.direction.toUpperCase()}</span></td>
                <td><small>${(t.entry_time || '').slice(0, 16)}</small></td>
                <td>₹${(t.entry_price || 0).toFixed(2)}</td>
                <td><small>${(t.exit_time || '').slice(0, 16)}</small></td>
                <td>₹${(t.exit_price || 0).toFixed(2)}</td>
                <td class="${pnlColor} fw-bold">₹${(t.pnl || 0).toFixed(2)}</td>
                <td><span class="badge bg-secondary">${t.exit_reason || ''}</span></td>
            </tr>`;
        }).join('') || '<tr><td colspan="8" class="text-muted text-center">No trades</td></tr>';

        const metricsHTML = (r.symbol_metrics || []).map(m => `
            <tr>
                <td><strong>${_esc(m.symbol)}</strong></td>
                <td>${m.total_trades || 0}</td>
                <td class="${m.win_rate >= 50 ? 'text-success' : 'text-warning'}">${(m.win_rate || 0).toFixed(1)}%</td>
                <td class="${m.total_pnl >= 0 ? 'text-success' : 'text-danger'}">₹${(m.total_pnl || 0).toFixed(2)}</td>
                <td>${(m.profit_factor || 0).toFixed(2)}</td>
                <td class="text-warning">-${(m.max_drawdown_pct || 0).toFixed(2)}%</td>
                <td>${(m.sharpe_ratio || 0).toFixed(2)}</td>
                <td>${(m.avg_bars_held || 0).toFixed(1)}</td>
            </tr>`).join('') || '<tr><td colspan="8" class="text-muted text-center">No data</td></tr>';

        return `
        <div class="tm-detail-header d-flex justify-content-between align-items-start mb-3">
            <div>
                <h5 class="mb-1">${_esc(r.name)}</h5>
                <small class="text-muted">${symbols} &bull; ${period} &bull; Capital: ${capital}</small>
            </div>
            <div class="d-flex gap-2">
                <button class="btn btn-sm btn-outline-primary" onclick="TimeMachine.exportRun('${r.run_id}','csv')">⬇ CSV</button>
                <button class="btn btn-sm btn-outline-secondary" onclick="TimeMachine.exportRun('${r.run_id}','json')">⬇ JSON</button>
            </div>
        </div>

        <!-- KPI Cards -->
        <div class="row g-2 mb-3">
            ${_kpiCard('Total Return', (r.total_return_pct || 0).toFixed(2) + '%', retColor)}
            ${_kpiCard('Final Capital', finalCap, '')}
            ${_kpiCard('Max Drawdown', '-' + (r.max_drawdown_pct || 0).toFixed(2) + '%', 'text-warning')}
            ${_kpiCard('Sharpe Ratio', (r.sharpe_ratio || 0).toFixed(2), '')}
            ${_kpiCard('Win Rate', (r.win_rate || 0).toFixed(1) + '%', (r.win_rate || 0) >= 50 ? 'text-success' : 'text-warning')}
            ${_kpiCard('Total Trades', r.total_trades || 0, '')}
            ${_kpiCard('Profit Factor', (r.profit_factor || 0).toFixed(2), '')}
            ${_kpiCard('Duration', (r.duration_seconds || 0).toFixed(1) + 's', 'text-muted')}
        </div>

        <!-- Equity Curve -->
        <div class="tm-card mb-3">
            <h6 class="mb-2">📈 Equity Curve</h6>
            <canvas id="tm-equity-chart" height="90"></canvas>
        </div>

        <!-- Per-symbol metrics -->
        <div class="tm-card mb-3">
            <h6 class="mb-2">📊 Per-Symbol Metrics</h6>
            <div class="table-responsive">
                <table class="table table-sm table-hover mb-0">
                    <thead class="table-dark"><tr>
                        <th>Symbol</th><th>Trades</th><th>Win%</th>
                        <th>Net P&L</th><th>Profit Factor</th>
                        <th>Max DD</th><th>Sharpe</th><th>Avg Bars</th>
                    </tr></thead>
                    <tbody>${metricsHTML}</tbody>
                </table>
            </div>
        </div>

        <!-- Trades list -->
        <div class="tm-card">
            <h6 class="mb-2">📋 Trade History ${(r.trades || []).length > 100 ? '(showing first 100)' : ''}</h6>
            <div class="table-responsive" style="max-height:350px;overflow-y:auto">
                <table class="table table-sm table-hover mb-0">
                    <thead class="table-dark sticky-top"><tr>
                        <th>Symbol</th><th>Dir</th><th>Entry Time</th><th>Entry ₹</th>
                        <th>Exit Time</th><th>Exit ₹</th><th>P&L</th><th>Reason</th>
                    </tr></thead>
                    <tbody>${tradesHTML}</tbody>
                </table>
            </div>
        </div>`;
    }

    function _kpiCard(label, value, colorClass) {
        return `<div class="col-6 col-md-3 col-xl-auto flex-fill">
            <div class="tm-kpi-card">
                <div class="tm-kpi-value ${colorClass}">${value}</div>
                <div class="tm-kpi-label">${label}</div>
            </div>
        </div>`;
    }

    function _renderEquityChart(equityCurve) {
        const canvas = document.getElementById('tm-equity-chart');
        if (!canvas || !equityCurve.length) return;

        if (equityChart) equityChart.destroy();

        const labels = equityCurve.map(e => String(e.time).slice(0, 16));
        const data = equityCurve.map(e => e.equity);
        const isPos = data[data.length - 1] >= data[0];

        equityChart = new Chart(canvas, {
            type: 'line',
            data: {
                labels,
                datasets: [{
                    label: 'Portfolio Equity (₹)',
                    data,
                    borderColor: isPos ? '#22c55e' : '#ef4444',
                    backgroundColor: isPos ? 'rgba(34,197,94,0.08)' : 'rgba(239,68,68,0.08)',
                    borderWidth: 1.5,
                    pointRadius: 0,
                    fill: true,
                    tension: 0.2,
                }],
            },
            options: {
                responsive: true,
                interaction: { mode: 'index', intersect: false },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: ctx => `₹ ${ctx.raw.toLocaleString('en-IN', { maximumFractionDigits: 0 })}`,
                        },
                    },
                },
                scales: {
                    x: { ticks: { maxTicksLimit: 8, font: { size: 10 } }, grid: { display: false } },
                    y: { ticks: { callback: v => '₹' + (v / 1000).toFixed(0) + 'k', font: { size: 10 } } },
                },
            },
        });
    }

    // ----------------------------------------------------------------
    // Export / Delete
    // ----------------------------------------------------------------
    function exportRun(runId, fmt) {
        window.open(`/api/backtest/export/${runId}?format=${fmt}`, '_blank');
    }

    async function deleteRun(runId) {
        if (!confirm('Delete this run? This cannot be undone.')) return;
        try {
            const res = await fetch(`/api/backtest/results/${runId}`, { method: 'DELETE' });
            const json = await res.json();
            if (json.success) {
                loadResultsList();
                if (currentRunId === runId) {
                    document.getElementById('tm-detail-panel').style.display = 'none';
                    currentRunId = null;
                }
            }
        } catch (err) {
            _showAlert('Delete failed: ' + err.message, 'danger');
        }
    }

    // ----------------------------------------------------------------
    // UI helpers
    // ----------------------------------------------------------------
    function _setRunning(running) {
        const btn = document.getElementById('tm-run-btn');
        if (!btn) return;
        btn.disabled = running;
        btn.innerHTML = running ? '<span class="spinner-border spinner-border-sm me-1"></span>Running…' : '▶ Run';
    }

    function _showProgress(pct, label = '') {
        const bar = document.getElementById('tm-progress-bar');
        const wrap = document.getElementById('tm-progress-wrap');
        if (!bar || !wrap) return;
        wrap.style.display = pct > 0 ? '' : 'none';
        bar.style.width = pct + '%';
        bar.textContent = label || pct + '%';
    }

    function _showAlert(msg, type = 'info') {
        const el = document.getElementById('tm-alert');
        if (!el) return;
        el.className = `alert alert-${type} py-2 px-3`;
        el.textContent = msg;
        el.style.display = '';
        setTimeout(() => { el.style.display = 'none'; }, 6000);
    }

    function _statusBadge(status) {
        const map = { completed: 'bg-success', running: 'bg-primary', failed: 'bg-danger', pending: 'bg-secondary' };
        return `<span class="badge ${map[status] || 'bg-secondary'}">${status}</span>`;
    }

    function _esc(str) {
        const d = document.createElement('div');
        d.textContent = str || '';
        return d.innerHTML;
    }

    // ----------------------------------------------------------------
    // Public API
    // ----------------------------------------------------------------
    return { init, loadRunDetail, loadResultsList, exportRun, deleteRun };
})();
