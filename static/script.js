(function() {
    'use strict';

    // ─── API BASE URL ──────────────────────────────────────────────────────
    // In production, set to your Render URL
    const API_BASE = window.location.origin;

    // ─── DOM REFS ──────────────────────────────────────────────────────────
    const $ = (sel) => document.querySelector(sel);
    const $$ = (sel) => document.querySelectorAll(sel);

    const statUsers = $('#statUsers');
    const statHosted = $('#statHosted');
    const statRunning = $('#statRunning');
    const statUptime = $('#statUptime');
    const accountList = $('#accountList');
    const accountCount = $('#accountCount');
    const quickCommands = $('#quickCommands');
    const apiStatus = $('#apiStatus');
    const toastContainer = $('#toastContainer');
    const loadingOverlay = $('#loadingOverlay');
    const hostModal = $('#hostModal');
    const phoneInput = $('#phoneInput');
    const nameInput = $('#nameInput');

    // ─── STATE ─────────────────────────────────────────────────────────────
    let state = {
        stats: { totalUsers: 0, hostedCount: 0, runningCount: 0, uptime: '0s' },
        accounts: [],
        quickCommands: [
            '.alive', '.ping', '.attack', '.roast', '.nuke',
            '.spray', '.stopspray', '.reply', '.rr', '.flag',
            '.antidel', '.fastgc', '.copy', '.normal', '.tts',
            '.qr', '.setname', '.setbio', '.ban', '.mute'
        ]
    };

    // ─── TOAST SYSTEM ─────────────────────────────────────────────────────
    function showToast(message, type = 'info', duration = 4000) {
        const icons = {
            success: 'fa-check-circle',
            error: 'fa-exclamation-circle',
            info: 'fa-info-circle'
        };
        const toast = document.createElement('div');
        toast.className = `toast toast--${type}`;
        toast.innerHTML = `<i class="fas ${icons[type] || icons.info}"></i> ${message}`;
        toastContainer.appendChild(toast);
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateY(20px) scale(0.95)';
            toast.style.transition = '0.3s ease';
            setTimeout(() => toast.remove(), 350);
        }, duration);
    }

    // ─── LOADING ──────────────────────────────────────────────────────────
    function showLoading(show) {
        loadingOverlay.classList.toggle('active', show);
    }

    // ─── API CALLS ────────────────────────────────────────────────────────
    async function apiFetch(endpoint, options = {}) {
        try {
            const res = await fetch(`${API_BASE}/api/${endpoint}`, {
                ...options,
                headers: {
                    'Content-Type': 'application/json',
                    ...(options.headers || {})
                }
            });
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            return await res.json();
        } catch (err) {
            console.error(`API Error (${endpoint}):`, err);
            throw err;
        }
    }

    // ─── RENDER FUNCTIONS ──────────────────────────────────────────────────

    function renderStats() {
        const s = state.stats;
        statUsers.textContent = s.totalUsers;
        statHosted.textContent = s.hostedCount;
        statRunning.textContent = s.runningCount;
        statUptime.textContent = s.uptime;
    }

    function renderAccounts() {
        const accounts = state.accounts;
        accountCount.textContent = `${accounts.length} / 3`;

        if (accounts.length === 0) {
            accountList.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-user-plus"></i>
                    <p>No accounts hosted yet.<br />Click <strong>Host New</strong> to start.</p>
                </div>
            `;
            return;
        }

        let html = '';
        accounts.forEach((acc) => {
            const statusClass = acc.running ? 'account-row__status--online' : 'account-row__status--offline';
            const statusLabel = acc.running ? '🟢 Running' : '🔴 Stopped';
            const uptimeDisplay = acc.running ? acc.uptime || '0m' : '—';
            const phone = acc.phone || `Account #${acc.slot + 1}`;
            const name = acc.userName || 'User';
            html += `
                <div class="account-row">
                    <div class="account-row__info">
                        <div class="account-row__status ${statusClass}"></div>
                        <div>
                            <div class="account-row__name">${name} · #${acc.slot + 1}</div>
                            <div class="account-row__phone">${phone}</div>
                        </div>
                        <span class="account-row__uptime">⏱ ${uptimeDisplay}</span>
                    </div>
                    <div class="account-row__actions">
                        <button class="btn btn--outline btn--icon" data-action="restart" data-user="${acc.userId || '0'}" data-slot="${acc.slot}" title="Restart">
                            <i class="fas fa-sync-alt"></i>
                        </button>
                        <button class="btn btn--danger btn--icon" data-action="logout" data-user="${acc.userId || '0'}" data-slot="${acc.slot}" title="Logout">
                            <i class="fas fa-sign-out-alt"></i>
                        </button>
                        <span style="font-size:0.65rem;color:var(--text-muted);padding-left:4px;">${statusLabel}</span>
                    </div>
                </div>
            `;
        });
        accountList.innerHTML = html;

        // attach events to action buttons
        accountList.querySelectorAll('[data-action]').forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.stopPropagation();
                const action = this.dataset.action;
                const user = parseInt(this.dataset.user) || 0;
                const slot = parseInt(this.dataset.slot);
                handleAccountAction(action, user, slot);
            });
        });
    }

    function renderQuickCommands() {
        const cmds = state.quickCommands;
        let html = '';
        const iconMap = {
            '.alive': 'fa-heart',
            '.ping': 'fa-tachometer-alt',
            '.attack': 'fa-crosshairs',
            '.roast': 'fa-fire',
            '.nuke': 'fa-bomb',
            '.spray': 'fa-water',
            '.stopspray': 'fa-stop-circle',
            '.reply': 'fa-reply-all',
            '.rr': 'fa-smile-wink',
            '.flag': 'fa-flag',
            '.antidel': 'fa-shield-alt',
            '.fastgc': 'fa-bolt',
            '.copy': 'fa-copy',
            '.normal': 'fa-undo',
            '.tts': 'fa-volume-up',
            '.qr': 'fa-qrcode',
            '.setname': 'fa-pen',
            '.setbio': 'fa-pen-fancy',
            '.ban': 'fa-gavel',
            '.mute': 'fa-volume-mute'
        };
        cmds.forEach(cmd => {
            const icon = iconMap[cmd] || 'fa-terminal';
            html += `<div class="cmd-chip"><i class="fas ${icon}"></i> ${cmd}</div>`;
        });
        quickCommands.innerHTML = html;
    }

    // ─── ACTION HANDLERS ─────────────────────────────────────────────────

    function handleAccountAction(action, userId, slot) {
        const label = `Account #${slot + 1}`;
        if (action === 'restart') {
            showToast(`🔄 Restarting ${label}...`, 'info');
            apiFetch('restart', {
                method: 'POST',
                body: JSON.stringify({ userId, slot })
            })
            .then(data => {
                if (data.success) {
                    showToast(`✅ ${label} restarted successfully!`, 'success');
                    refreshDashboard();
                } else {
                    showToast(`❌ Restart failed: ${data.message || 'Unknown error'}`, 'error');
                }
            })
            .catch(() => {
                showToast(`❌ Restart failed — server error`, 'error');
            });
        } else if (action === 'logout') {
            showToast(`🗑️ Logging out ${label}...`, 'info');
            apiFetch('logout', {
                method: 'POST',
                body: JSON.stringify({ userId, slot })
            })
            .then(data => {
                if (data.success) {
                    showToast(`👋 ${label} logged out.`, 'success');
                    refreshDashboard();
                } else {
                    showToast(`❌ Logout failed: ${data.message || 'Unknown error'}`, 'error');
                }
            })
            .catch(() => {
                showToast(`❌ Logout failed — server error`, 'error');
            });
        }
    }

    // ─── HOST NEW ACCOUNT ──────────────────────────────────────────────────

    function hostNewAccount() {
        const phone = phoneInput.value.trim();
        const name = nameInput.value.trim() || 'New User';

        if (!phone) {
            showToast('❌ Please enter a phone number', 'error');
            return;
        }

        const digits = phone.replace(/[^0-9+]/g, '');
        if (digits.length < 7) {
            showToast('❌ Invalid phone number. Use format: +91XXXXXXXXXX', 'error');
            return;
        }

        showLoading(true);
        apiFetch('host', {
            method: 'POST',
            body: JSON.stringify({ phone, name })
        })
        .then(data => {
            showLoading(false);
            if (data.success) {
                showToast(`🚀 ${name} hosted successfully!`, 'success');
                closeModal();
                refreshDashboard();
            } else {
                showToast(`❌ Host failed: ${data.message || 'Unknown error'}`, 'error');
            }
        })
        .catch(err => {
            showLoading(false);
            showToast(`❌ Host failed — server error: ${err.message}`, 'error');
        });
    }

    // ─── REFRESH DASHBOARD ─────────────────────────────────────────────────

    function refreshDashboard() {
        const btn = $('#btnRefresh');
        btn.innerHTML = '<span class="spinner"></span> Refreshing';
        btn.disabled = true;

        showLoading(true);

        Promise.all([
            apiFetch('stats'),
            apiFetch('accounts')
        ])
        .then(([statsData, accountsData]) => {
            showLoading(false);
            if (statsData) {
                state.stats = statsData;
                renderStats();
            }
            if (accountsData && Array.isArray(accountsData)) {
                state.accounts = accountsData;
                renderAccounts();
            }
            btn.innerHTML = '<i class="fas fa-sync-alt"></i> Refresh';
            btn.disabled = false;
            showToast('🔄 Dashboard refreshed', 'info', 2000);
        })
        .catch(err => {
            showLoading(false);
            btn.innerHTML = '<i class="fas fa-sync-alt"></i> Refresh';
            btn.disabled = false;
            showToast('❌ Refresh failed', 'error');
            console.error('Refresh error:', err);
        });
    }

    // ─── COMMANDS POPUP ──────────────────────────────────────────────────

    function showAllCommands() {
        const all = [
            '.alive', '.ping', '.attack', '.roast', '.diss', '.war', '.savage',
            '.ultra', '.godwar', '.combo', '.troll', '.shame', '.fire', '.devil',
            '.karma', '.ghost', '.legend', '.doom', '.nuke', '.storm', '.blizzard',
            '.venom', '.reply', '.rr', '.flag', '.hrr', '.replygod', '.replysid',
            '.spray', '.dspray', '.tspray', '.rspray', '.multispray', '.countspray',
            '.spraydelay', '.addtext', '.listtexts', '.edittext', '.deltext',
            '.cleartext', '.antidel', '.watchspam', '.unwatchspam', '.watchlist',
            '.setgpfp', '.addgpfp', '.listgpfp', '.autogpfp', '.stopgpfp',
            '.ar', '.sar', '.fastgc', '.tts', '.qrcode', '.fancy', '.style',
            '.emoji', '.calc', '.weather', '.ip', '.short', '.info', '.copy',
            '.normal', '.music', '.dmusic', '.setname', '.setbio', '.setpp',
            '.getpp', '.ban', '.unban', '.kick', '.promote', '.demote', '.mute',
            '.unmute', '.gmute', '.gunmute', '.mutelist', '.purge', '.throw',
            '.lock', '.unlock', '.addbots', '.warn', '.warnlist', '.clearwarn',
            '.pin', '.unpin', '.groupinfo', '.membercount', '.invitelink',
            '.flip', '.dice', '.rps', '.8ball', '.choose', '.joke', '.riddle',
            '.fact', '.quote', '.truth', '.dare', '.pickup', '.compliment',
            '.roastme', '.del', '.echo', '.react', '.read', '.typing', '.online',
            '.myip', '.hex', '.octal', '.ascii', '.charcount', '.palindrome',
            '.vowels', '.titlecase', '.snake', '.shout', '.alternating',
            '.spaceit', '.wordfreq', '.removespaces', '.truncate', '.percentage',
            '.square', '.prime', '.factorial', '.fibonacci', '.bmi', '.age',
            '.coin', '.lucky', '.roll', '.number', '.clap', '.mock', '.strike',
            '.spoiler', '.mirror', '.emoji2text', '.lettercount', '.nato',
            '.boxtext', '.countdown', '.tinytext', '.bubble', '.square_text',
            '.encrypt', '.decrypt', '.sha1', '.sha512', '.charinfo', '.timer',
            '.typetest', '.sysinfo', '.table', '.roman', '.randname', '.randcolor',
            '.flip_text', '.crypto', '.translate', '.imdb'
        ];
        const chunkSize = 12;
        let msg = '📜 All Commands (500+)\n━━━━━━━━━━━━━━━\n';
        for (let i = 0; i < all.length; i += chunkSize) {
            msg += all.slice(i, i + chunkSize).join('  ') + '\n';
        }
        msg += '━━━━━━━━━━━━━━━\nPrefix: .  |  Total: ' + all.length;
        alert(msg);
    }

    // ─── MODAL ────────────────────────────────────────────────────────────

    function openModal() {
        hostModal.classList.add('active');
        phoneInput.focus();
    }

    function closeModal() {
        hostModal.classList.remove('active');
        phoneInput.value = '';
        nameInput.value = '';
    }

    // ─── INIT ─────────────────────────────────────────────────────────────

    function init() {
        refreshDashboard();

        // Event listeners
        $('#btnRefresh').addEventListener('click', refreshDashboard);
        $('#btnHost').addEventListener('click', openModal);
        $('#btnCommands').addEventListener('click', showAllCommands);
        $('#modalClose').addEventListener('click', closeModal);
        $('#modalCancel').addEventListener('click', closeModal);
        $('#modalHost').addEventListener('click', hostNewAccount);

        phoneInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') nameInput.focus();
        });
        nameInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') hostNewAccount();
        });

        hostModal.addEventListener('click', (e) => {
            if (e.target === hostModal) closeModal();
        });

        setInterval(refreshDashboard, 30000);

        // API status blink
        setInterval(() => {
            apiStatus.style.opacity = apiStatus.style.opacity === '0.4' ? '1' : '0.4';
        }, 1200);

        showToast('🚀 SID Hoster Web V3 loaded', 'success', 2500);
    }

    document.addEventListener('DOMContentLoaded', init);
})();
