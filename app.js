let currentFilter = 'all';

async function loadMatches() {
    try {
        const response = await fetch(`data/matches.json?v=${new Date().getTime()}`);
        if (!response.ok) throw new Error('Failed to load matches');
        allMatches = await response.json();
        renderMatches();
    } catch (err) {
        console.error('Error loading matches:', err);
    }
}

function filterLeague(league) {
    currentFilter = league;
    
    // Update tab styles
    document.querySelectorAll('[id^="tab-"]').forEach(tab => {
        tab.classList.remove('bg-primary', 'text-black', 'shadow-lg', 'shadow-primary/20');
        tab.classList.add('glass', 'text-slate-400');
    });
    
    const activeTab = document.getElementById('tab-' + (league === 'all' ? 'all' : 'nba'));
    if (activeTab) {
        activeTab.classList.remove('glass', 'text-slate-400');
        activeTab.classList.add('bg-primary', 'text-black', 'shadow-lg', 'shadow-primary/20');
    }
    
    renderMatches();
}

function renderMatches() {
    const list = document.getElementById('match-list');
    if (!list) return;
    
    // Keep the header
    const header = list.querySelector('h2');
    list.innerHTML = '';
    if (header) list.appendChild(header);

    const filtered = currentFilter === 'all' 
        ? allMatches 
        : allMatches.filter(m => m.away_team.includes(currentFilter) || m.home_team.includes(currentFilter) || (m.league && m.league === currentFilter) || currentFilter === 'NBA'); 
        // Note: Currently syncing mostly NBA, but added flexible filter logic

    if (filtered.length === 0) {
        list.innerHTML += '<div class="glass p-8 rounded-2xl text-center text-slate-500">Нет активных прогнозов</div>';
        return;
    }

    filtered.forEach(match => {
        const card = document.createElement('div');
        card.className = "glass-card rounded-2xl overflow-hidden group cursor-pointer active:scale-[0.98] transition-all mb-4";
        card.onclick = () => showMatchDetails(match.id);
        
        const edgeColor = match.edge > 12 ? 'text-primary' : (match.edge > 10 ? 'text-emerald-400' : 'text-slate-400');

        card.innerHTML = `
            <div class="p-5 space-y-4">
                <div class="flex justify-between items-start">
                    <h3 class="text-xl font-bold text-white group-hover:text-primary transition-colors">${match.away_team} @ ${match.home_team}</h3>
                    <div class="text-right">
                        <p class="text-[9px] text-slate-500 uppercase font-bold tracking-widest mb-1">Edge</p>
                        <p class="${edgeColor} text-lg font-bold">+${Math.round(match.edge * 10) / 10}%</p>
                    </div>
                </div>
                <div class="flex items-center justify-between py-3 border-y border-white/5">
                    <div class="space-y-1">
                        <p class="text-[9px] text-slate-500 uppercase font-bold text-left">Odd</p>
                        <p class="font-mono text-lg text-primary font-bold">${match.odds}</p>
                    </div>
                    <div class="space-y-1 text-right">
                        <p class="text-[9px] text-slate-500 uppercase font-bold">Start</p>
                        <p class="text-xs font-semibold text-slate-200">${match.commence_time_display || match.commence_time}</p>
                    </div>
                </div>
                <div class="flex items-center gap-2">
                     <span class="bg-primary/20 text-primary text-[9px] font-bold px-2 py-0.5 rounded uppercase">${match.bet_type}</span>
                     <span class="text-slate-500 text-[10px] font-medium">Pick: ${match.pick} ${match.line || ''}</span>
                </div>
            </div>
        `;
        list.appendChild(card);
    });
}

function showMatchDetails(matchId) {
    const match = allMatches.find(m => m.id === matchId);
    if (!match) return;

    document.getElementById('detail-edge').innerText = `+${Math.round(match.edge * 10) / 10}%`;
    document.getElementById('detail-odds').innerText = match.odds;
    const sign = (match.line && match.line > 0) ? '+' : '';
    const lineStr = match.line ? ` (${sign}${match.line})` : '';
    document.getElementById('detail-pick').innerText = `${match.pick}${lineStr}`;
    
    const desc = document.querySelector('#view-details p.text-slate-300');
    if (desc) desc.innerText = match.intel_summary || "Анализ матча сформирован автономными скрапперами на основе рыночных аномалий и инсайдерских потоков данных.";

    const title = document.querySelector('#view-details h1');
    if (title) title.innerHTML = `${match.away_team} <span class="text-slate-500 text-xl font-light">vs</span> ${match.home_team}`;

    const detailsView = document.getElementById('view-details');
    detailsView.classList.add('active');
    document.body.style.overflow = 'hidden'; 
}

function closeMatchDetails() {
    const detailsView = document.getElementById('view-details');
    detailsView.classList.remove('active');
    document.body.style.overflow = ''; 
}

async function loadStats() {
    try {
        const response = await fetch(`data/stats.json?v=${new Date().getTime()}`);
        if (!response.ok) throw new Error('Failed to load stats');
        const stats = await response.json();
        renderStats(stats);
    } catch (err) {
        console.error('Error loading stats:', err);
    }
}

function renderStats(stats) {
    const profitEl = document.getElementById('stat-profit');
    const roiEl = document.getElementById('stat-roi');
    const winRateEl = document.getElementById('stat-winrate');
    const totalEl = document.getElementById('stat-total');
    const winsEl = document.getElementById('stat-wins');
    const lossesEl = document.getElementById('stat-losses');
    const streakEl = document.getElementById('stat-streak');
    const updateTimeEl = document.getElementById('last-update-time');

    if (profitEl) profitEl.innerText = stats.profit !== undefined ? stats.profit.toFixed(2) : "0.00";
    if (roiEl) roiEl.innerText = (stats.roi || 0) + "%";
    if (winRateEl) winRateEl.innerText = (stats.win_rate || 0) + "%";
    if (totalEl) totalEl.innerText = stats.total_bets || 0;
    if (winsEl) winsEl.innerText = stats.wins || 0;
    if (lossesEl) lossesEl.innerText = stats.losses || 0;
    if (updateTimeEl) updateTimeEl.innerText = "Обновлено: " + (stats.last_update || "--:--");

    const trendEl = document.getElementById('profit-trend');
    if (trendEl && stats.roi !== undefined) {
        trendEl.innerText = (stats.roi >= 0 ? "+" : "") + stats.roi + "%";
        trendEl.className = stats.roi >= 0 ? "text-sm font-bold text-emerald-400" : "text-sm font-bold text-rose-500";
    }

    if (streakEl && stats.streak) {
        streakEl.innerHTML = '';
        stats.streak.forEach(s => {
            const dot = document.createElement('div');
            dot.className = `size-2 rounded-full ${s === 'W' ? 'bg-emerald-400 scale-125' : 'bg-rose-500'} shadow-lg`;
            if (s === 'W') dot.classList.add('animate-pulse');
            streakEl.appendChild(dot);
        });
        // Fill remaining dots if less than 10
        for (let i = stats.streak.length; i < 10; i++) {
            const dot = document.createElement('div');
            dot.className = "size-2 rounded-full bg-white/10";
            streakEl.appendChild(dot);
        }
    }
}

async function loadHistory() {
    console.log('Fetching history...');
    try {
        const timestamp = new Date().getTime();
        const response = await fetch(`data/history.json?v=${timestamp}`);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        const history = await response.json();
        console.log('History loaded:', history.length, 'items');
        renderHistory(history);
    } catch (err) {
        console.error('CRITICAL: Error loading history:', err);
        const histList = document.getElementById('history-list');
        if (histList) {
            histList.innerHTML = `
                <div class="glass p-4 rounded-2xl text-center">
                    <p class="text-[10px] text-rose-500 font-bold mb-1">Ошибка загрузки</p>
                    <p class="text-[9px] text-slate-500">${err.message}</p>
                    <button onclick="loadHistory()" class="mt-2 text-[9px] text-primary underline">Повторить</button>
                </div>
            `;
        }
    }
}

function renderHistory(history) {
    const list = document.getElementById('history-list');
    if (!list) return;
    list.innerHTML = '';

    if (history.length === 0) {
        list.innerHTML = '<div class="glass p-4 rounded-2xl text-center text-[10px] text-slate-500">Нет завершенных матчей</div>';
        return;
    }

    history.forEach(match => {
        const item = document.createElement('div');
        const isWin = match.status === 'WIN';
        const statusColor = isWin ? 'text-emerald-400' : 'text-rose-500';
        const statusBg = isWin ? 'bg-emerald-500/10' : 'bg-rose-500/10';
        const statusIcon = isWin ? 'check_circle' : 'cancel';

        item.className = "glass p-4 rounded-2xl flex items-center justify-between border border-white/5";
        item.innerHTML = `
            <div class="space-y-1">
                <p class="text-xs font-bold text-white">${match.away_team} @ ${match.home_team}</p>
                <div class="flex items-center gap-2">
                    <p class="text-[9px] text-slate-500 uppercase font-bold tracking-widest">${match.commence_time_display || ''}</p>
                    <span class="text-[9px] px-1.5 py-0.5 bg-white/5 rounded text-primary font-mono font-bold">@ ${match.odds || '?.??'}</span>
                </div>
            </div>
            <div class="flex items-center gap-3">
                <div class="text-right">
                    <p class="text-[9px] text-slate-500 uppercase font-bold mb-0.5">Pick: ${match.pick}</p>
                    <p class="text-xs font-mono font-bold text-slate-200">${match.result_score || '--:--'}</p>
                </div>
                <div class="size-8 rounded-full ${statusBg} flex items-center justify-center ${statusColor}">
                    <span class="material-symbols-outlined text-lg">${statusIcon}</span>
                </div>
            </div>
        `;
        list.appendChild(item);
    });
}

function switchView(viewId) {
    document.querySelectorAll('.view').forEach(view => {
        view.classList.remove('active');
        if (view.id === 'view-' + viewId) {
            view.classList.add('active');
        }
    });

    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.remove('text-primary');
        btn.classList.add('text-slate-500');
        const icon = btn.querySelector('.material-symbols-outlined');
        if (icon) icon.style.fontVariationSettings = "'FILL' 0";
        
        if (btn.dataset.view === viewId) {
            btn.classList.add('text-primary');
            btn.classList.remove('text-slate-500');
            if (icon) icon.style.fontVariationSettings = "'FILL' 1";
        }
    });

    if (viewId === 'predictions') loadMatches();
    if (viewId === 'stats') {
        loadStats();
        loadHistory();
    }
    
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

loadMatches();

if (window.Telegram && window.Telegram.WebApp) {
    const webapp = window.Telegram.WebApp;
    webapp.expand();
    webapp.ready();
    webapp.headerColor = '#000000';
}

// Add haptic feedback simulation
document.querySelectorAll('button, a').forEach(el => {
    el.addEventListener('click', () => {
        if (window.Telegram && window.Telegram.WebApp && window.Telegram.WebApp.HapticFeedback) {
            window.Telegram.WebApp.HapticFeedback.impactOccurred('medium');
        }
    });
});
