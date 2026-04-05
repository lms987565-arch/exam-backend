# backend/routes/dashboard.py
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/", response_class=HTMLResponse)
async def get_dashboard_html():
    """Return HTML dashboard page"""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Exam Portal — Admin Dashboard</title>
    <style>
        :root {
            --primary: #4f46e5;
            --primary-dark: #3730a3;
            --primary-light: #e0e7ff;
            --success: #059669;
            --warning: #d97706;
            --danger: #dc2626;
            --gray-50: #f9fafb;
            --gray-100: #f3f4f6;
            --gray-200: #e5e7eb;
            --gray-500: #6b7280;
            --gray-700: #374151;
            --gray-900: #111827;
        }

        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            background: var(--gray-100);
            color: var(--gray-900);
            min-height: 100vh;
        }

        /* ── HEADER ── */
        .header {
            background: var(--primary);
            color: white;
            padding: 0 32px;
            height: 60px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            box-shadow: 0 2px 8px rgba(0,0,0,.25);
            position: sticky;
            top: 0;
            z-index: 100;
        }
        .header-title { font-size: 1.2rem; font-weight: 700; letter-spacing: .3px; }
        .header-title span { opacity: .6; font-weight: 400; margin-left: 8px; font-size: .9rem; }
        .header-actions { display: flex; align-items: center; gap: 12px; }
        .badge-live {
            background: #22c55e; color: white; font-size: .7rem; font-weight: 700;
            padding: 3px 8px; border-radius: 20px; letter-spacing: .5px;
            animation: pulse 2s infinite;
        }
        @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.6} }
        .btn {
            padding: 7px 16px; border: none; border-radius: 6px;
            font-size: .85rem; font-weight: 600; cursor: pointer; transition: all .15s;
        }
        .btn-white { background: white; color: var(--primary); }
        .btn-white:hover { background: var(--primary-light); }
        #last-updated { font-size: .78rem; opacity: .75; }

        /* ── LAYOUT ── */
        .page { max-width: 1400px; margin: 0 auto; padding: 28px 24px; }

        /* ── TABS ── */
        .tabs { display: flex; gap: 4px; margin-bottom: 24px; border-bottom: 2px solid var(--gray-200); }
        .tab {
            padding: 10px 20px; border: none; background: none; cursor: pointer;
            font-size: .9rem; font-weight: 600; color: var(--gray-500);
            border-bottom: 2px solid transparent; margin-bottom: -2px; transition: all .15s;
        }
        .tab:hover { color: var(--primary); }
        .tab.active { color: var(--primary); border-bottom-color: var(--primary); }

        /* ── STATS GRID ── */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
            gap: 16px;
            margin-bottom: 28px;
        }
        .stat-card {
            background: white; border-radius: 10px; padding: 20px 16px;
            box-shadow: 0 1px 4px rgba(0,0,0,.08);
            display: flex; flex-direction: column; gap: 6px;
        }
        .stat-icon { font-size: 1.6rem; line-height: 1; }
        .stat-value { font-size: 2rem; font-weight: 800; color: var(--primary); line-height: 1; }
        .stat-label { font-size: .78rem; color: var(--gray-500); font-weight: 500; text-transform: uppercase; letter-spacing: .5px; }

        /* ── SECTION ── */
        .section {
            background: white; border-radius: 10px;
            box-shadow: 0 1px 4px rgba(0,0,0,.08);
            margin-bottom: 24px; overflow: hidden;
        }
        .section-header {
            display: flex; align-items: center; justify-content: space-between;
            padding: 16px 20px; border-bottom: 1px solid var(--gray-200);
        }
        .section-title { font-size: 1rem; font-weight: 700; color: var(--gray-900); }
        .section-count {
            background: var(--primary-light); color: var(--primary);
            font-size: .75rem; font-weight: 700; padding: 2px 10px; border-radius: 20px;
        }

        /* ── TABLE ── */
        .table-wrapper { overflow-x: auto; }
        table { width: 100%; border-collapse: collapse; font-size: .875rem; }
        thead th {
            background: var(--gray-50); color: var(--gray-500);
            font-size: .72rem; font-weight: 700; text-transform: uppercase;
            letter-spacing: .5px; padding: 10px 16px; text-align: left;
            border-bottom: 1px solid var(--gray-200);
        }
        tbody td { padding: 11px 16px; border-bottom: 1px solid var(--gray-100); color: var(--gray-700); }
        tbody tr:last-child td { border-bottom: none; }
        tbody tr:hover { background: var(--gray-50); }
        .empty-row td { text-align: center; color: var(--gray-500); padding: 32px; font-style: italic; }

        /* ── BADGES ── */
        .tag {
            display: inline-block; padding: 2px 9px; border-radius: 20px;
            font-size: .72rem; font-weight: 700; text-transform: capitalize;
        }
        .tag-open, .tag-verified, .tag-active { background: #d1fae5; color: #065f46; }
        .tag-closed, .tag-rejected { background: #fee2e2; color: #991b1b; }
        .tag-submitted, .tag-pending { background: #fef3c7; color: #92400e; }
        .tag-draft { background: var(--gray-200); color: var(--gray-700); }

        /* ── LOADING / ERROR ── */
        .loading-overlay {
            position: fixed; inset: 0; background: rgba(255,255,255,.8);
            display: flex; flex-direction: column; align-items: center; justify-content: center;
            z-index: 200; gap: 16px;
        }
        .spinner {
            width: 40px; height: 40px; border: 4px solid var(--primary-light);
            border-top-color: var(--primary); border-radius: 50%;
            animation: spin 0.8s linear infinite;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
        .loading-text { color: var(--primary); font-weight: 600; }

        .error-banner {
            background: #fee2e2; border: 1px solid #fca5a5; color: #991b1b;
            padding: 12px 16px; border-radius: 8px; margin-bottom: 20px;
            font-size: .875rem;
        }

        /* ── TAB PANELS ── */
        .tab-panel { display: none; }
        .tab-panel.active { display: block; }

        /* ── SEARCH ── */
        .search-bar {
            padding: 8px 12px; border: 1px solid var(--gray-200); border-radius: 6px;
            font-size: .85rem; width: 220px; outline: none;
        }
        .search-bar:focus { border-color: var(--primary); box-shadow: 0 0 0 3px var(--primary-light); }

        code { background: var(--gray-100); padding: 1px 5px; border-radius: 4px; font-size: .85em; }
    </style>
</head>
<body>

<!-- HEADER -->
<header class="header">
    <div class="header-title">
        📋 Exam Portal
        <span>Admin Dashboard</span>
    </div>
    <div class="header-actions">
        <span class="badge-live">● LIVE</span>
        <span id="last-updated">–</span>
        <button class="btn btn-white" onclick="loadAll()">🔄 Refresh</button>
    </div>
</header>

<!-- LOADING OVERLAY -->
<div class="loading-overlay" id="overlay">
    <div class="spinner"></div>
    <div class="loading-text">Fetching data…</div>
</div>

<!-- MAIN PAGE -->
<div class="page">

    <div id="error-container"></div>

    <!-- STATS -->
    <div class="stats-grid" id="stats-grid">
        <div class="stat-card"><div class="stat-icon">👨‍🎓</div><div class="stat-value" id="s-students">–</div><div class="stat-label">Students</div></div>
        <div class="stat-card"><div class="stat-icon">📝</div><div class="stat-value" id="s-exams">–</div><div class="stat-label">Exams</div></div>
        <div class="stat-card"><div class="stat-icon">📂</div><div class="stat-value" id="s-apps">–</div><div class="stat-label">Applications</div></div>
        <div class="stat-card"><div class="stat-icon">✅</div><div class="stat-value" id="s-verified">–</div><div class="stat-label">Verified</div></div>
        <div class="stat-card"><div class="stat-icon">⏳</div><div class="stat-value" id="s-pending">–</div><div class="stat-label">Pending</div></div>
        <div class="stat-card"><div class="stat-icon">🟢</div><div class="stat-value" id="s-open">–</div><div class="stat-label">Open Exams</div></div>
    </div>

    <!-- TABS -->
    <div class="tabs">
        <button class="tab active" onclick="switchTab('students',this)">👨‍🎓 Students</button>
        <button class="tab" onclick="switchTab('exams',this)">📝 Exams</button>
        <button class="tab" onclick="switchTab('applications',this)">📂 Applications</button>
        <button class="tab" onclick="switchTab('hall_tickets',this)">🎫 Hall Tickets</button>
        <button class="tab" onclick="switchTab('documents',this)">📄 Documents</button>
        <button class="tab" onclick="switchTab('schedule',this)">🗓️ Schedule</button>
    </div>

    <!-- STUDENTS TAB -->
    <div class="tab-panel active" id="tab-students">
        <div class="section">
            <div class="section-header">
                <span class="section-title">Students</span>
                <div style="display:flex;gap:10px;align-items:center">
                    <input class="search-bar" id="search-students" placeholder="🔍 Search name / email…" oninput="filterTable('students-tbody','search-students')">
                    <span class="section-count" id="count-students">0</span>
                </div>
            </div>
            <div class="table-wrapper">
                <table>
                    <thead><tr><th>#</th><th>Student ID</th><th>Full Name</th><th>Email</th><th>Phone</th></tr></thead>
                    <tbody id="students-tbody"><tr class="empty-row"><td colspan="5">Loading…</td></tr></tbody>
                </table>
            </div>
        </div>
    </div>

    <!-- EXAMS TAB -->
    <div class="tab-panel" id="tab-exams">
        <div class="section">
            <div class="section-header">
                <span class="section-title">Exams</span>
                <span class="section-count" id="count-exams">0</span>
            </div>
            <div class="table-wrapper">
                <table>
                    <thead><tr><th>ID</th><th>Exam Code</th><th>Exam Name</th><th>Status</th></tr></thead>
                    <tbody id="exams-tbody"><tr class="empty-row"><td colspan="4">Loading…</td></tr></tbody>
                </table>
            </div>
        </div>
    </div>

    <!-- APPLICATIONS TAB -->
    <div class="tab-panel" id="tab-applications">
        <div class="section">
            <div class="section-header">
                <span class="section-title">Applications</span>
                <div style="display:flex;gap:10px;align-items:center">
                    <input class="search-bar" id="search-apps" placeholder="🔍 Search…" oninput="filterTable('apps-tbody','search-apps')">
                    <span class="section-count" id="count-apps">0</span>
                </div>
            </div>
            <div class="table-wrapper">
                <table>
                    <thead><tr><th>ID</th><th>Student ID</th><th>Exam ID</th><th>Status</th><th>Progress</th><th>Created</th></tr></thead>
                    <tbody id="apps-tbody"><tr class="empty-row"><td colspan="6">Loading…</td></tr></tbody>
                </table>
            </div>
        </div>
    </div>

    <!-- HALL TICKETS TAB -->
    <div class="tab-panel" id="tab-hall_tickets">
        <div class="section">
            <div class="section-header">
                <span class="section-title">Hall Tickets</span>
                <span class="section-count" id="count-hall_tickets">0</span>
            </div>
            <div class="table-wrapper">
                <table>
                    <thead><tr><th>ID</th><th>Hall Ticket No</th><th>Student ID</th><th>Exam ID</th><th>Status</th></tr></thead>
                    <tbody id="hall_tickets-tbody"><tr class="empty-row"><td colspan="5">Loading…</td></tr></tbody>
                </table>
            </div>
        </div>
    </div>

    <!-- DOCUMENTS TAB -->
    <div class="tab-panel" id="tab-documents">
        <div class="section">
            <div class="section-header">
                <span class="section-title">Student Documents</span>
                <span class="section-count" id="count-documents">0</span>
            </div>
            <div class="table-wrapper">
                <table>
                    <thead><tr><th>ID</th><th>Student ID</th><th>Document Type</th><th>Status</th><th>Remark</th><th>Verified By</th></tr></thead>
                    <tbody id="documents-tbody"><tr class="empty-row"><td colspan="6">Loading…</td></tr></tbody>
                </table>
            </div>
        </div>
    </div>

    <!-- SCHEDULE TAB -->
    <div class="tab-panel" id="tab-schedule">
        <div class="section">
            <div class="section-header">
                <span class="section-title">Exam Schedule</span>
                <span class="section-count" id="count-schedule">0</span>
            </div>
            <div class="table-wrapper">
                <table>
                    <thead><tr><th>ID</th><th>Exam ID</th><th>Date</th><th>Start</th><th>End</th><th>Status</th></tr></thead>
                    <tbody id="schedule-tbody"><tr class="empty-row"><td colspan="6">Loading…</td></tr></tbody>
                </table>
            </div>
        </div>
    </div>

</div><!-- /page -->

<script>
// ==================== HELPERS ====================
const $ = id => document.getElementById(id);

function tag(val) {
    if (!val) return '<span class="tag tag-draft">–</span>';
    const cls = {
        open:'open', closed:'closed', verified:'verified', active:'active',
        submitted:'submitted', pending:'pending', rejected:'rejected', draft:'draft'
    }[val.toLowerCase()] || 'draft';
    return `<span class="tag tag-${cls}">${val}</span>`;
}

function progressBar(pct) {
    const p = parseInt(pct) || 0;
    const color = p >= 100 ? '#059669' : p >= 50 ? '#d97706' : '#4f46e5';
    return `<div style="display:flex;align-items:center;gap:8px">
        <div style="flex:1;height:6px;background:#e5e7eb;border-radius:3px;overflow:hidden">
            <div style="width:${p}%;height:100%;background:${color};border-radius:3px"></div>
        </div>
        <span style="font-size:.75rem;color:#6b7280;white-space:nowrap">${p}%</span>
    </div>`;
}

function fmtDate(d) {
    if (!d) return '–';
    return new Date(d).toLocaleDateString('en-IN', {day:'2-digit',month:'short',year:'numeric'});
}

function emptyRow(cols, msg = 'No data found') {
    return `<tr class="empty-row"><td colspan="${cols}">${msg}</td></tr>`;
}

function showError(msg) {
    $('error-container').innerHTML = `<div class="error-banner">⚠️ ${msg}</div>`;
    setTimeout(() => $('error-container').innerHTML = '', 6000);
}

// ==================== TAB SWITCHING ====================
function switchTab(name, btn) {
    document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    $(`tab-${name}`).classList.add('active');
    btn.classList.add('active');
}

// ==================== TABLE FILTER ====================
function filterTable(tbodyId, searchId) {
    const q = $(searchId).value.toLowerCase();
    const rows = $(`${tbodyId}`).querySelectorAll('tr:not(.empty-row)');
    rows.forEach(row => {
        row.style.display = row.innerText.toLowerCase().includes(q) ? '' : 'none';
    });
}

// ==================== RENDER FUNCTIONS ====================
function renderStudents(data) {
    $('count-students').textContent = data.length;
    if (!data.length) { $('students-tbody').innerHTML = emptyRow(5); return; }
    $('students-tbody').innerHTML = data.map((s, i) => `
        <tr>
            <td style="color:#9ca3af">${i + 1}</td>
            <td><code>${s.student_id || '–'}</code></td>
            <td style="font-weight:600">${s.full_name || s.name || '–'}</td>
            <td>${s.email || '–'}</td>
            <td>${s.phone || '–'}</td>
        </tr>`).join('');
}

function renderExams(data) {
    $('count-exams').textContent = data.length;
    if (!data.length) { $('exams-tbody').innerHTML = emptyRow(4); return; }
    $('exams-tbody').innerHTML = data.map(e => `
        <tr>
            <td style="color:#9ca3af">${e.id}</td>
            <td><code>${e.exam_code || '–'}</code></td>
            <td style="font-weight:600">${e.exam_name || '–'}</td>
            <td>${tag(e.registration_status || e.status || '–')}</td>
        </tr>`).join('');
}

function renderApplications(data) {
    $('count-apps').textContent = data.length;
    if (!data.length) { $('apps-tbody').innerHTML = emptyRow(6); return; }
    $('apps-tbody').innerHTML = data.map(a => `
        <tr>
            <td style="color:#9ca3af">${a.id}</td>
            <td>${a.student_id || '–'}</td>
            <td>${a.exam_id || '–'}</td>
            <td>${tag(a.status)}</td>
            <td style="min-width:130px">${progressBar(a.progress_percentage)}</td>
            <td style="color:#9ca3af;font-size:.8rem">${fmtDate(a.created_at)}</td>
        </tr>`).join('');
}

function renderHallTickets(data) {
    $('count-hall_tickets').textContent = data.length;
    if (!data.length) { $('hall_tickets-tbody').innerHTML = emptyRow(5); return; }
    $('hall_tickets-tbody').innerHTML = data.map(t => `
        <tr>
            <td style="color:#9ca3af">${t.id}</td>
            <td><code>${t.hall_ticket_no || '–'}</code></td>
            <td>${t.student_id || '–'}</td>
            <td>${t.exam_id || '–'}</td>
            <td>${tag(t.status)}</td>
        </tr>`).join('');
}

function renderDocuments(data) {
    $('count-documents').textContent = data.length;
    if (!data.length) { $('documents-tbody').innerHTML = emptyRow(6); return; }
    $('documents-tbody').innerHTML = data.map(d => `
        <tr>
            <td style="color:#9ca3af">${d.id}</td>
            <td>${d.student_id || '–'}</td>
            <td><code>${d.document_type || '–'}</code></td>
            <td>${tag(d.status)}</td>
            <td style="color:#6b7280;font-size:.8rem">${d.remark || '–'}</td>
            <td style="color:#6b7280;font-size:.8rem">${d.verified_by || '–'}</td>
        </tr>`).join('');
}

function renderSchedule(data) {
    $('count-schedule').textContent = data.length;
    if (!data.length) { $('schedule-tbody').innerHTML = emptyRow(6); return; }
    $('schedule-tbody').innerHTML = data.map(s => `
        <tr>
            <td style="color:#9ca3af">${s.id}</td>
            <td>${s.exam_id || '–'}</td>
            <td>${s.exam_date || '–'}</td>
            <td>${s.slot_start || '–'}</td>
            <td>${s.slot_end || '–'}</td>
            <td>${tag(s.status)}</td>
        </tr>`).join('');
}

// ==================== STATS ====================
function renderStats(stats, studentCount, examCount, appCount) {
    $('s-students').textContent  = stats.total_students  ?? studentCount  ?? '–';
    $('s-exams').textContent     = stats.total_exams     ?? examCount     ?? '–';
    $('s-apps').textContent      = stats.total_applications ?? appCount   ?? '–';
    $('s-verified').textContent  = stats.verified_applications ?? '–';
    $('s-pending').textContent   = stats.pending_applications  ?? '–';
    $('s-open').textContent      = stats.open_exams             ?? '–';
}

// ==================== SAFE FETCH ====================
async function safeFetch(url) {
    try {
        const r = await fetch(url);
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        const json = await r.json();
        return json.data ?? [];
    } catch (e) {
        showError(`Failed to fetch ${url}: ${e.message}`);
        return [];
    }
}

// ==================== LOAD ALL ====================
async function loadAll() {
    $('overlay').style.display = 'flex';
    $('error-container').innerHTML = '';

    try {
        const [students, exams, applications, hallTickets, documents, schedule, statsRaw] = await Promise.all([
            safeFetch('/api/students?limit=200'),
            safeFetch('/api/exams'),
            safeFetch('/api/applications?limit=200'),
            safeFetch('/api/hall_tickets/all?limit=200'),
            safeFetch('/api/documents/all?limit=200'),
            safeFetch('/api/exam_schedule/all?limit=200'),
            fetch('/api/dashboard/stats').then(r => r.json()).catch(() => ({ data: {} }))
        ]);

        const stats = statsRaw.data || {};
        renderStats(stats, students.length, exams.length, applications.length);
        renderStudents(students);
        renderExams(exams);
        renderApplications(applications);
        renderHallTickets(hallTickets);
        renderDocuments(documents);
        renderSchedule(schedule);

        $('last-updated').textContent = 'Updated ' + new Date().toLocaleTimeString('en-IN');
    } catch (err) {
        showError('Unexpected error: ' + err.message);
    } finally {
        $('overlay').style.display = 'none';
    }
}

// Auto-load + auto-refresh every 60s
loadAll();
setInterval(loadAll, 60000);
</script>
</body>
</html>"""
