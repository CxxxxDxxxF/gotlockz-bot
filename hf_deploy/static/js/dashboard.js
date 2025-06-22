// Dashboard JavaScript for real-time updates

let performanceChart;
let currentChartPeriod = '30d';

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    loadBotStatus();
    loadStats();
    loadRecentPicks();
    loadPickTypes();
    loadPerformanceChart();
    
    // Auto-refresh every 30 seconds
    setInterval(loadBotStatus, 30000);
    setInterval(loadStats, 30000);
    setInterval(loadRecentPicks, 30000);
});

async function loadBotStatus() {
    try {
        const response = await fetch('/api/bot-status');
        const data = await response.json();
        
        const statusBadge = document.getElementById('botStatus');
        const statusDetails = document.getElementById('botStatusDetails');
        const cpuUsage = document.getElementById('cpuUsage');
        const memoryUsage = document.getElementById('memoryUsage');
        
        if (data.bot_running) {
            statusBadge.className = 'badge bg-success ms-2';
            statusBadge.textContent = 'Online';
            statusDetails.textContent = 'Bot is running and connected to Discord';
        } else {
            statusBadge.className = 'badge bg-danger ms-2';
            statusBadge.textContent = 'Offline';
            statusDetails.textContent = 'Bot is not running';
        }
        
        if (data.system) {
            cpuUsage.textContent = data.system.cpu_percent.toFixed(1);
            memoryUsage.textContent = data.system.memory_percent.toFixed(1);
        }
        
    } catch (error) {
        console.error('Error loading bot status:', error);
        document.getElementById('botStatus').className = 'badge bg-warning ms-2';
        document.getElementById('botStatus').textContent = 'Error';
        document.getElementById('botStatusDetails').textContent = 'Unable to check bot status';
    }
}

function changeChartPeriod(period) {
    currentChartPeriod = period;
    
    // Update button states
    document.querySelectorAll('.btn-group .btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    loadPerformanceChart();
}

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
        
        if (data.recent_picks.length === 0) {
            picksContainer.innerHTML = '<div class="text-center text-muted">No picks yet</div>';
            return;
        }
        
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
        const response = await fetch(`/api/performance/daily?period=${currentChartPeriod}`);
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

// Quick Action Functions
function refreshAll() {
    loadBotStatus();
    loadStats();
    loadRecentPicks();
    loadPickTypes();
    loadPerformanceChart();
    
    // Show feedback
    const btn = event.target;
    const originalText = btn.innerHTML;
    btn.innerHTML = '<i class="fas fa-check"></i> Refreshed!';
    btn.classList.remove('btn-outline-success');
    btn.classList.add('btn-success');
    
    setTimeout(() => {
        btn.innerHTML = originalText;
        btn.classList.remove('btn-success');
        btn.classList.add('btn-outline-success');
    }, 2000);
}

function showAddPickModal() {
    const modal = new bootstrap.Modal(document.getElementById('addPickModal'));
    modal.show();
    
    // Setup confidence score display
    const confidenceSlider = document.querySelector('input[name="confidence_score"]');
    const confidenceValue = document.getElementById('confidenceValue');
    
    confidenceSlider.addEventListener('input', function() {
        confidenceValue.textContent = this.value;
    });
}

function submitPick() {
    const form = document.getElementById('addPickForm');
    const formData = new FormData(form);
    
    const pickData = {
        pick_type: formData.get('pick_type'),
        pick_number: parseInt(formData.get('pick_number')),
        bet_details: formData.get('bet_details'),
        odds: formData.get('odds'),
        analysis: formData.get('analysis'),
        confidence_score: parseInt(formData.get('confidence_score')),
        edge_percentage: parseFloat(formData.get('edge_percentage')) || 0
    };
    
    fetch('/api/picks/add', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(pickData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Close modal and refresh data
            bootstrap.Modal.getInstance(document.getElementById('addPickModal')).hide();
            form.reset();
            refreshAll();
            
            // Show success message
            showNotification('Pick added successfully!', 'success');
        } else {
            showNotification('Error adding pick: ' + data.error, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Error adding pick', 'error');
    });
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

function exportData() {
    // Create a CSV export of all picks
    fetch('/api/stats')
        .then(response => response.json())
        .then(data => {
            const csvContent = "data:text/csv;charset=utf-8," 
                + "Type,Bet,Odds,Result,Profit/Loss\n"
                + data.recent_picks.map(pick => 
                    `${pick.type},${pick.bet},${pick.odds},${pick.result},${pick.profit_loss}`
                ).join("\n");
            
            const encodedUri = encodeURI(csvContent);
            const link = document.createElement("a");
            link.setAttribute("href", encodedUri);
            link.setAttribute("download", `gotlockz_picks_${new Date().toISOString().split('T')[0]}.csv`);
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            showNotification('Data exported successfully!', 'success');
        })
        .catch(error => {
            console.error('Error exporting data:', error);
            showNotification('Error exporting data', 'error');
        });
}

function showAnalytics() {
    const modal = new bootstrap.Modal(document.getElementById('analyticsModal'));
    modal.show();
    loadAnalytics();
}

function loadAnalytics() {
    fetch('/api/analytics')
        .then(response => response.json())
        .then(data => {
            // Load overall stats
            const overall = data.overall;
            const winRate = overall.total_picks > 0 ? (overall.wins / overall.total_picks * 100).toFixed(1) : 0;
            
            document.getElementById('overallStats').innerHTML = `
                <div class="row text-center">
                    <div class="col-6">
                        <h4 class="text-primary">${overall.total_picks}</h4>
                        <small>Total Picks</small>
                    </div>
                    <div class="col-6">
                        <h4 class="text-success">${winRate}%</h4>
                        <small>Win Rate</small>
                    </div>
                </div>
                <div class="row text-center mt-3">
                    <div class="col-6">
                        <h4 class="text-${overall.total_profit >= 0 ? 'success' : 'danger'}">$${overall.total_profit.toFixed(2)}</h4>
                        <small>Total Profit</small>
                    </div>
                    <div class="col-6">
                        <h4 class="text-info">${overall.avg_confidence.toFixed(1)}</h4>
                        <small>Avg Confidence</small>
                    </div>
                </div>
            `;
            
            // Load type stats
            let typeStatsHtml = '';
            data.by_type.forEach(type => {
                const typeWinRate = type.total > 0 ? (type.wins / type.total * 100).toFixed(1) : 0;
                typeStatsHtml += `
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <div>
                            <strong>${type.type.toUpperCase()}</strong>
                            <br><small>${type.wins}/${type.total} wins</small>
                        </div>
                        <div class="text-end">
                            <div class="text-${type.profit >= 0 ? 'success' : 'danger'}">$${type.profit.toFixed(2)}</div>
                            <small>${typeWinRate}%</small>
                        </div>
                    </div>
                `;
            });
            document.getElementById('typeStats').innerHTML = typeStatsHtml;
            
            // Load monthly chart
            loadMonthlyChart(data.monthly);
        })
        .catch(error => {
            console.error('Error loading analytics:', error);
            document.getElementById('overallStats').innerHTML = '<div class="text-danger">Error loading analytics</div>';
        });
}

function loadMonthlyChart(monthlyData) {
    const ctx = document.getElementById('monthlyChart').getContext('2d');
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: monthlyData.map(d => d.month),
            datasets: [{
                label: 'Monthly Profit',
                data: monthlyData.map(d => d.profit),
                backgroundColor: monthlyData.map(d => d.profit >= 0 ? 'rgba(40, 167, 69, 0.8)' : 'rgba(220, 53, 69, 0.8)'),
                borderColor: monthlyData.map(d => d.profit >= 0 ? '#28a745' : '#dc3545'),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Profit ($)'
                    }
                }
            }
        }
    });
}

function showPickHistory() {
    const modal = new bootstrap.Modal(document.getElementById('historyModal'));
    modal.show();
    loadHistory();
}

function loadHistory(page = 1) {
    const typeFilter = document.getElementById('historyTypeFilter').value;
    const resultFilter = document.getElementById('historyResultFilter').value;
    
    const params = new URLSearchParams({
        page: page,
        limit: 10
    });
    
    if (typeFilter) params.append('type', typeFilter);
    if (resultFilter) params.append('result', resultFilter);
    
    fetch(`/api/history?${params}`)
        .then(response => response.json())
        .then(data => {
            let historyHtml = '';
            
            if (data.picks.length === 0) {
                historyHtml = '<div class="text-center text-muted">No picks found</div>';
            } else {
                data.picks.forEach(pick => {
                    const profitClass = pick.profit_loss >= 0 ? 'text-success' : 'text-danger';
                    const resultBadge = pick.result ? 
                        `<span class="badge bg-${pick.result === 'win' ? 'success' : pick.result === 'loss' ? 'danger' : 'warning'}">${pick.result.toUpperCase()}</span>` : 
                        '<span class="badge bg-secondary">PENDING</span>';
                    
                    historyHtml += `
                        <div class="card mb-2">
                            <div class="card-body p-3">
                                <div class="d-flex justify-content-between align-items-start">
                                    <div>
                                        <div class="fw-bold">${pick.pick_type.toUpperCase()} #${pick.pick_number}</div>
                                        <div>${pick.bet_details}</div>
                                        <small class="text-muted">${pick.odds} • Posted: ${new Date(pick.posted_at).toLocaleDateString()}</small>
                                        ${pick.analysis ? `<div class="mt-1"><small>${pick.analysis}</small></div>` : ''}
                                    </div>
                                    <div class="text-end">
                                        ${resultBadge}
                                        <div class="${profitClass} fw-bold">$${pick.profit_loss.toFixed(2)}</div>
                                        <small>Confidence: ${pick.confidence_score}/10</small>
                                    </div>
                                </div>
                            </div>
                        </div>
                    `;
                });
            }
            
            document.getElementById('historyContent').innerHTML = historyHtml;
            
            // Add pagination
            if (data.pagination.pages > 1) {
                let paginationHtml = `
                    <div>
                        Page ${data.pagination.page} of ${data.pagination.pages} 
                        (${data.pagination.total} total picks)
                    </div>
                    <div>
                `;
                
                if (data.pagination.page > 1) {
                    paginationHtml += `<button class="btn btn-sm btn-outline-primary me-2" onclick="loadHistory(${data.pagination.page - 1})">Previous</button>`;
                }
                
                if (data.pagination.page < data.pagination.pages) {
                    paginationHtml += `<button class="btn btn-sm btn-outline-primary" onclick="loadHistory(${data.pagination.page + 1})">Next</button>`;
                }
                
                paginationHtml += '</div>';
                document.getElementById('historyPagination').innerHTML = paginationHtml;
            } else {
                document.getElementById('historyPagination').innerHTML = '';
            }
        })
        .catch(error => {
            console.error('Error loading history:', error);
            document.getElementById('historyContent').innerHTML = '<div class="text-danger">Error loading history</div>';
        });
}

function exportHistory() {
    const typeFilter = document.getElementById('historyTypeFilter').value;
    const resultFilter = document.getElementById('historyResultFilter').value;
    
    fetch('/api/history?limit=1000' + (typeFilter ? `&type=${typeFilter}` : '') + (resultFilter ? `&result=${resultFilter}` : ''))
        .then(response => response.json())
        .then(data => {
            const csvContent = "data:text/csv;charset=utf-8," 
                + "Type,Pick Number,Bet Details,Odds,Result,Profit/Loss,Confidence,Edge %,Posted Date,Analysis\n"
                + data.picks.map(pick => 
                    `${pick.pick_type},${pick.pick_number},"${pick.bet_details}",${pick.odds},${pick.result || 'pending'},${pick.profit_loss},${pick.confidence_score},${pick.edge_percentage},${pick.posted_at},"${pick.analysis}"`
                ).join("\n");
            
            const encodedUri = encodeURI(csvContent);
            const link = document.createElement("a");
            link.setAttribute("href", encodedUri);
            link.setAttribute("download", `gotlockz_history_${new Date().toISOString().split('T')[0]}.csv`);
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            showNotification('History exported successfully!', 'success');
        })
        .catch(error => {
            console.error('Error exporting history:', error);
            showNotification('Error exporting history', 'error');
        });
}

function showNotifications() {
    const modal = new bootstrap.Modal(document.getElementById('notificationsModal'));
    modal.show();
    loadNotifications();
}

function loadNotifications() {
    fetch('/api/notifications')
        .then(response => response.json())
        .then(data => {
            // Set checkbox states
            document.getElementById('emailNotif').checked = data.settings.email_notifications;
            document.getElementById('discordNotif').checked = data.settings.discord_notifications;
            document.getElementById('newPickNotif').checked = data.settings.new_pick_alerts;
            document.getElementById('resultNotif').checked = data.settings.result_alerts;
            
            // Load recent notifications
            let notificationsHtml = '';
            data.recent_notifications.forEach(notif => {
                const timeAgo = getTimeAgo(new Date(notif.timestamp));
                notificationsHtml += `
                    <div class="d-flex align-items-start mb-2 ${!notif.read ? 'fw-bold' : ''}">
                        <div class="flex-grow-1">
                            <div class="small">${notif.message}</div>
                            <small class="text-muted">${timeAgo}</small>
                        </div>
                        ${!notif.read ? '<span class="badge bg-primary ms-2">New</span>' : ''}
                    </div>
                `;
            });
            
            if (data.recent_notifications.length === 0) {
                notificationsHtml = '<div class="text-muted">No recent notifications</div>';
            }
            
            document.getElementById('recentNotifications').innerHTML = notificationsHtml;
        })
        .catch(error => {
            console.error('Error loading notifications:', error);
            document.getElementById('recentNotifications').innerHTML = '<div class="text-danger">Error loading notifications</div>';
        });
}

function saveNotificationSettings() {
    const settings = {
        email_notifications: document.getElementById('emailNotif').checked,
        discord_notifications: document.getElementById('discordNotif').checked,
        new_pick_alerts: document.getElementById('newPickNotif').checked,
        result_alerts: document.getElementById('resultNotif').checked
    };
    
    // In a real app, you'd save this to the backend
    showNotification('Notification settings saved!', 'success');
}

function showSettings() {
    const modal = new bootstrap.Modal(document.getElementById('settingsModal'));
    modal.show();
    loadSettings();
}

function loadSettings() {
    fetch('/api/settings')
        .then(response => response.json())
        .then(data => {
            document.getElementById('autoRefresh').checked = data.dashboard.auto_refresh;
            document.getElementById('refreshInterval').value = data.dashboard.refresh_interval;
            document.getElementById('themeSelect').value = data.dashboard.theme;
            document.getElementById('showConfidence').checked = data.display.show_confidence;
            document.getElementById('showEdge').checked = data.display.show_edge;
            document.getElementById('showAnalysis').checked = data.display.show_analysis;
        })
        .catch(error => {
            console.error('Error loading settings:', error);
        });
}

function saveSettings() {
    const settings = {
        dashboard: {
            auto_refresh: document.getElementById('autoRefresh').checked,
            refresh_interval: parseInt(document.getElementById('refreshInterval').value),
            theme: document.getElementById('themeSelect').value,
            chart_type: 'line'
        },
        display: {
            show_confidence: document.getElementById('showConfidence').checked,
            show_edge: document.getElementById('showEdge').checked,
            show_analysis: document.getElementById('showAnalysis').checked
        }
    };
    
    // In a real app, you'd save this to the backend
    showNotification('Settings saved successfully!', 'success');
    
    // Apply theme change
    if (settings.dashboard.theme === 'light') {
        document.body.style.background = 'linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)';
    } else {
        document.body.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
    }
}

function showHelp() {
    const modal = new bootstrap.Modal(document.getElementById('helpModal'));
    modal.show();
    loadHelp();
}

function loadHelp() {
    fetch('/api/help')
        .then(response => response.json())
        .then(data => {
            let helpHtml = '';
            
            // Add sections
            data.sections.forEach(section => {
                helpHtml += `
                    <div class="mb-4">
                        <h5><i class="fas fa-info-circle text-primary"></i> ${section.title}</h5>
                        <p class="text-muted">${section.content}</p>
                        <ul class="list-unstyled">
                            ${section.items.map(item => `<li><i class="fas fa-check text-success me-2"></i>${item}</li>`).join('')}
                        </ul>
                    </div>
                `;
            });
            
            // Add FAQ
            helpHtml += '<h5 class="mt-4"><i class="fas fa-question-circle text-primary"></i> Frequently Asked Questions</h5>';
            data.faq.forEach(faq => {
                helpHtml += `
                    <div class="mb-3">
                        <strong>Q: ${faq.question}</strong>
                        <br><span class="text-muted">A: ${faq.answer}</span>
                    </div>
                `;
            });
            
            document.getElementById('helpContent').innerHTML = helpHtml;
        })
        .catch(error => {
            console.error('Error loading help:', error);
            document.getElementById('helpContent').innerHTML = '<div class="text-danger">Error loading help content</div>';
        });
}

function getTimeAgo(date) {
    const now = new Date();
    const diffInSeconds = Math.floor((now - date) / 1000);
    
    if (diffInSeconds < 60) return 'Just now';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
    return `${Math.floor(diffInSeconds / 86400)}d ago`;
}
