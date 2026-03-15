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
        
        const edgeColor = match.edge > 0.12 ? 'text-primary' : (match.edge > 0.1 ? 'text-emerald-400' : 'text-slate-400');

        card.innerHTML = `
            <div class="p-5 space-y-4">
                <div class="flex justify-between items-start">
                    <h3 class="text-xl font-bold text-white group-hover:text-primary transition-colors">${match.away_team} @ ${match.home_team}</h3>
                    <div class="text-right">
                        <p class="text-[9px] text-slate-500 uppercase font-bold tracking-widest mb-1">Edge</p>
                        <p class="${edgeColor} text-lg font-bold">+${Math.round(match.edge * 1000) / 10}%</p>
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

    document.getElementById('detail-edge').innerText = `+${Math.round(match.edge * 1000) / 10}%`;
    document.getElementById('detail-odds').innerText = match.odds;
    const sign = (match.line && match.line > 0) ? '+' : '';
    const lineStr = match.line ? ` (${sign}${match.line})` : '';
    document.getElementById('detail-pick').innerText = `${match.pick}${lineStr}`;
    
    const desc = document.querySelector('#view-details p.text-slate-300');
    if (desc) desc.innerText = match.intel_summary || "Анализ матча формируется на основе нейросетевых данных NotebookLM и рыночных аномалий.";

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

    if (viewId === 'predictions') renderMatches();
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

loadMatches();

if (window.Telegram && window.Telegram.WebApp) {
    const webapp = window.Telegram.WebApp;
    webapp.expand();
    webapp.ready();
    webapp.headerColor = '#000000';

    const user = webapp.initDataUnsafe.user;
    if (user) {
        const nameEl = document.getElementById('user-name');
        if (nameEl) {
            // Priority: Username -> First+Last Name -> First Name
            nameEl.innerText = user.username ? ('@' + user.username) : (user.first_name + (user.last_name ? ' ' + user.last_name : ''));
        }
        if (user.photo_url) {
            const avatarDiv = document.querySelector('#view-profile .bg-cover');
            if (avatarDiv) {
                avatarDiv.style.backgroundImage = `url('${user.photo_url}')`;
            }
        }
    }
}

// Add haptic feedback simulation
document.querySelectorAll('button, a').forEach(el => {
    el.addEventListener('click', () => {
        if (window.Telegram && window.Telegram.WebApp && window.Telegram.WebApp.HapticFeedback) {
            window.Telegram.WebApp.HapticFeedback.impactOccurred('medium');
        }
    });
});
