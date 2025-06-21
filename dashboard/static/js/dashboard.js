// Dashboard JavaScript for real-time updates

let performanceChart;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    loadStats();
    loadRecentPicks();
    loadPickTypes();
    loadPerformanceChart();
    
    // Auto-refresh every 30 seconds
    setInterval(loadStats, 30000);
    setInterval(loadRecentPicks, 30000);
});

async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();
        
        document.getElementById('totalPicks').textContent = data.total_picks;
        document.getElementById('winRate').textContent = data.win_rate.toFixed(1) + '%';
        document.getElementById('totalProfit').textContent = '$' + data.total_profit.toFixed(2);
        document.getElementById('roi').textContent = data.roi_percentage.toFixed(1) + '%';
        
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

async function loadRecentPicks() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();
        
        const picksContainer = document.getElementById('recentPicks');
        picksContainer.innerHTML = '';
        
        data.recent_picks.forEach(pick => {
            const pickCard = document.createElement('div');
            pickCard.className = `card pick-card ${pick.result}`;
            
            const profitClass = pick.profit_loss >= 0 ? 'text-success' : 'text-danger';
            const profitIcon = pick.profit_loss >= 0 ? 'fa-arrow-up' : 'fa-arrow-down';
            
            pickCard.innerHTML = `
                <div class="card-body p-2">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <small class="text-muted">${pick.type.toUpperCase()}</small>
                            <div class="fw-bold">${pick.bet}</div>
                            <small>${pick.odds}</small>
                        </div>
                        <div class="text-end">
                            <div class="badge bg-${pick.result === 'win' ? 'success' : pick.result === 'loss' ? 'danger' : 'warning'}">
                                ${pick.result.toUpperCase()}
                            </div>
                            <div class="${profitClass}">
                                <i class="fas ${profitIcon}"></i> $${pick.profit_loss.toFixed(2)}
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            picksContainer.appendChild(pickCard);
        });
        
    } catch (error) {
        console.error('Error loading recent picks:', error);
    }
}

async function loadPickTypes() {
    const types = ['vip', 'lotto', 'free'];
    
    for (const type of types) {
        try {
            const response = await fetch(`/api/picks/${type}`);
            const picks = await response.json();
            
            const container = document.getElementById(`${type}Picks`);
            container.innerHTML = '';
            
            if (picks.length === 0) {
                container.innerHTML = '<div class="text-muted">No picks yet</div>';
                continue;
            }
            
            const wins = picks.filter(p => p.result === 'win').length;
            const total = picks.length;
            const winRate = total > 0 ? (wins / total * 100).toFixed(1) : 0;
            const totalProfit = picks.reduce((sum, p) => sum + p.profit_loss, 0);
            
            container.innerHTML = `
                <div class="text-center">
                    <h3 class="text-${totalProfit >= 0 ? 'success' : 'danger'}">$${totalProfit.toFixed(2)}</h3>
                    <p class="mb-1">${wins}/${total} Wins</p>
                    <p class="text-muted">${winRate}% Win Rate</p>
                </div>
            `;
            
        } catch (error) {
            console.error(`Error loading ${type} picks:`, error);
        }
    }
}

async function loadPerformanceChart() {
    try {
        const response = await fetch('/api/performance/daily');
        const data = await response.json();
        
        const ctx = document.getElementById('performanceChart').getContext('2d');
        
        if (performanceChart) {
            performanceChart.destroy();
        }
        
        performanceChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.map(d => d.date),
                datasets: [{
                    label: 'Daily Profit',
                    data: data.map(d => d.profit),
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    tension: 0.4,
                    fill: true
                }, {
                    label: 'Win Rate %',
                    data: data.map(d => d.win_rate),
                    borderColor: '#764ba2',
                    backgroundColor: 'rgba(118, 75, 162, 0.1)',
                    tension: 0.4,
                    yAxisID: 'y1'
                }]
            },
            options: {
                responsive: true,
                interaction: {
                    mode: 'index',
                    intersect: false,
                },
                scales: {
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        title: {
                            display: true,
                            text: 'Profit ($)'
                        }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: {
                            display: true,
                            text: 'Win Rate (%)'
                        },
                        grid: {
                            drawOnChartArea: false,
                        },
                    }
                }
            }
        });
        
    } catch (error) {
        console.error('Error loading performance chart:', error);
    }
}
