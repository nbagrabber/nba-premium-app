function switchView(viewId) {
    // Update Views
    document.querySelectorAll('.view').forEach(view => {
        view.classList.remove('active');
        if (view.id === 'view-' + viewId) {
            view.classList.add('active');
        }
    });

    // Update Nav Buttons
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.remove('text-primary');
        btn.classList.add('text-slate-500');
        btn.querySelector('.material-symbols-outlined').style.fontVariationSettings = "'FILL' 0";
        
        if (btn.dataset.view === viewId) {
            btn.classList.add('text-primary');
            btn.classList.remove('text-slate-500');
            btn.querySelector('.material-symbols-outlined').style.fontVariationSettings = "'FILL' 1";
        }
    });

    // Reset scroll
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function showMatchDetails(matchId) {
    const detailsView = document.getElementById('view-details');
    detailsView.classList.add('active');
    document.body.style.overflow = 'hidden'; // Prevent background scroll
}

function closeMatchDetails() {
    const detailsView = document.getElementById('view-details');
    detailsView.classList.remove('active');
    document.body.style.overflow = ''; // Restore scroll
}

// Telegram Mini App Initialization (Global placeholder)
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
