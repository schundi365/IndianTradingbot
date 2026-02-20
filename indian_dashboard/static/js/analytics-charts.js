/**
 * Analytics Chart Components
 * Individual chart implementations using Chart.js
 */

// Binance color scheme
const COLORS = {
    green: '#0ECB81',
    red: '#F6465D',
    yellow: '#FCD535',
    blue: '#2196F3',
    purple: '#9C27B0',
    orange: '#FF9800',
    cyan: '#00BCD4',
    background: '#181A20',
    gridLines: '#2B3139',
    text: '#EAECEF'
};

// Chart.js default configuration
Chart.defaults.color = COLORS.text;
Chart.defaults.borderColor = COLORS.gridLines;
Chart.defaults.font.family = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif";
Chart.defaults.font.size = 12;

/**
 * Profit by Symbol Chart (Bar Chart)
 */
window.ProfitBySymbolChart = {
    chart: null,
    
    render(data) {
        const ctx = document.getElementById('profit-by-symbol-chart');
        if (!ctx) return;
        
        // Destroy existing chart
        if (this.chart) {
            this.chart.destroy();
        }
        
        // Prepare data
        const labels = data.map(d => d.symbol);
        const values = data.map(d => d.pnl);
        const colors = values.map(v => v >= 0 ? COLORS.green : COLORS.red);
        
        // Create chart
        this.chart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'P&L (₹)',
                    data: values,
                    backgroundColor: colors,
                    borderColor: colors,
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: '#1E2329',
                        titleColor: COLORS.text,
                        bodyColor: COLORS.text,
                        borderColor: COLORS.gridLines,
                        borderWidth: 1,
                        callbacks: {
                            label: (context) => {
                                const value = context.parsed.y;
                                const item = data[context.dataIndex];
                                return [
                                    `P&L: ₹${value.toLocaleString('en-IN', {minimumFractionDigits: 2})}`,
                                    `Trades: ${item.trades_count}`,
                                    `Win Rate: ${item.win_rate}%`
                                ];
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: COLORS.gridLines
                        },
                        ticks: {
                            callback: (value) => `₹${value.toLocaleString('en-IN')}`
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }
};

/**
 * Win/Loss by Symbol Chart (Stacked Bar Chart)
 */
window.WinLossChart = {
    chart: null,
    
    render(data) {
        const ctx = document.getElementById('win-loss-chart');
        if (!ctx) return;
        
        if (this.chart) {
            this.chart.destroy();
        }
        
        const labels = data.map(d => d.symbol);
        const wins = data.map(d => d.wins);
        const losses = data.map(d => d.losses);
        
        this.chart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Wins',
                        data: wins,
                        backgroundColor: COLORS.green,
                        borderColor: COLORS.green,
                        borderWidth: 1
                    },
                    {
                        label: 'Losses',
                        data: losses,
                        backgroundColor: COLORS.red,
                        borderColor: COLORS.red,
                        borderWidth: 1
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                        labels: {
                            color: COLORS.text,
                            usePointStyle: true,
                            padding: 15
                        }
                    },
                    tooltip: {
                        backgroundColor: '#1E2329',
                        titleColor: COLORS.text,
                        bodyColor: COLORS.text,
                        borderColor: COLORS.gridLines,
                        borderWidth: 1
                    }
                },
                scales: {
                    y: {
                        stacked: true,
                        beginAtZero: true,
                        grid: {
                            color: COLORS.gridLines
                        }
                    },
                    x: {
                        stacked: true,
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }
};

/**
 * Daily Profit Chart (Line Chart)
 */
window.DailyProfitChart = {
    chart: null,
    
    render(data) {
        const ctx = document.getElementById('daily-profit-chart');
        if (!ctx) return;
        
        if (this.chart) {
            this.chart.destroy();
        }
        
        const labels = data.map(d => d.date);
        const values = data.map(d => d.pnl);
        
        // Calculate cumulative P&L
        let cumulative = 0;
        const cumulativeValues = values.map(v => {
            cumulative += v;
            return cumulative;
        });
        
        this.chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Cumulative P&L (₹)',
                    data: cumulativeValues,
                    borderColor: COLORS.blue,
                    backgroundColor: 'rgba(33, 150, 243, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 3,
                    pointHoverRadius: 5,
                    pointBackgroundColor: COLORS.blue,
                    pointBorderColor: COLORS.background,
                    pointBorderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                        labels: {
                            color: COLORS.text,
                            usePointStyle: true,
                            padding: 15
                        }
                    },
                    tooltip: {
                        backgroundColor: '#1E2329',
                        titleColor: COLORS.text,
                        bodyColor: COLORS.text,
                        borderColor: COLORS.gridLines,
                        borderWidth: 1,
                        callbacks: {
                            label: (context) => {
                                const value = context.parsed.y;
                                const item = data[context.dataIndex];
                                return [
                                    `Cumulative: ₹${value.toLocaleString('en-IN', {minimumFractionDigits: 2})}`,
                                    `Daily: ₹${item.pnl.toLocaleString('en-IN', {minimumFractionDigits: 2})}`,
                                    `Trades: ${item.trades_count}`
                                ];
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        grid: {
                            color: COLORS.gridLines
                        },
                        ticks: {
                            callback: (value) => `₹${value.toLocaleString('en-IN')}`
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            maxRotation: 45,
                            minRotation: 45
                        }
                    }
                }
            }
        });
    }
};

/**
 * Hourly Performance Chart (Bar Chart)
 */
window.HourlyPerformanceChart = {
    chart: null,
    
    render(data) {
        const ctx = document.getElementById('hourly-performance-chart');
        if (!ctx) return;
        
        if (this.chart) {
            this.chart.destroy();
        }
        
        const labels = data.map(d => d.hour);
        const values = data.map(d => d.pnl);
        const colors = values.map(v => v >= 0 ? COLORS.green : COLORS.red);
        
        this.chart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'P&L (₹)',
                    data: values,
                    backgroundColor: colors,
                    borderColor: colors,
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: '#1E2329',
                        titleColor: COLORS.text,
                        bodyColor: COLORS.text,
                        borderColor: COLORS.gridLines,
                        borderWidth: 1,
                        callbacks: {
                            label: (context) => {
                                const value = context.parsed.y;
                                const item = data[context.dataIndex];
                                return [
                                    `P&L: ₹${value.toLocaleString('en-IN', {minimumFractionDigits: 2})}`,
                                    `Trades: ${item.trades_count}`
                                ];
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: COLORS.gridLines
                        },
                        ticks: {
                            callback: (value) => `₹${value.toLocaleString('en-IN')}`
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }
};

/**
 * Trade Distribution Chart (Doughnut Chart)
 */
window.TradeDistributionChart = {
    chart: null,
    
    render(data) {
        const ctx = document.getElementById('trade-distribution-chart');
        if (!ctx) return;
        
        if (this.chart) {
            this.chart.destroy();
        }
        
        const labels = data.map(d => d.symbol);
        const values = data.map(d => d.count);
        
        // Generate colors
        const colorPalette = [
            COLORS.blue, COLORS.green, COLORS.yellow, COLORS.purple,
            COLORS.orange, COLORS.cyan, COLORS.red
        ];
        const backgroundColors = labels.map((_, i) => colorPalette[i % colorPalette.length]);
        
        this.chart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: values,
                    backgroundColor: backgroundColors,
                    borderColor: COLORS.background,
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'right',
                        labels: {
                            color: COLORS.text,
                            usePointStyle: true,
                            padding: 15,
                            generateLabels: (chart) => {
                                const datasets = chart.data.datasets;
                                return chart.data.labels.map((label, i) => {
                                    const value = datasets[0].data[i];
                                    const item = data[i];
                                    return {
                                        text: `${label} (${item.percentage}%)`,
                                        fillStyle: datasets[0].backgroundColor[i],
                                        hidden: false,
                                        index: i
                                    };
                                });
                            }
                        }
                    },
                    tooltip: {
                        backgroundColor: '#1E2329',
                        titleColor: COLORS.text,
                        bodyColor: COLORS.text,
                        borderColor: COLORS.gridLines,
                        borderWidth: 1,
                        callbacks: {
                            label: (context) => {
                                const item = data[context.dataIndex];
                                return [
                                    `${item.symbol}: ${item.count} trades`,
                                    `${item.percentage}% of total`
                                ];
                            }
                        }
                    }
                }
            }
        });
    }
};
