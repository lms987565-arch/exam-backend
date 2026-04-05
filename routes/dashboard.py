<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Exam Portal — Admin Dashboard</title>
    <style>
        :root {
            --primary: #4f46e5;
            --success: #059669;
            --warning: #d97706;
            --danger: #dc2626;
            --gray-100: #f3f4f6;
            --gray-200: #e5e7eb;
            --gray-500: #6b7280;
            --gray-700: #374151;
            --gray-900: #111827;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: system-ui, -apple-system, sans-serif;
            background: var(--gray-100);
            color: var(--gray-900);
        }
        .header {
            background: var(--primary);
            color: white;
            padding: 0 24px;
            height: 60px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            position: sticky;
            top: 0;
            z-index: 100;
        }
        .header-title { font-size: 1.2rem; font-weight: 700; }
        .header-actions { display: flex; gap: 12px; align-items: center; }
        .btn {
            padding: 6px 14px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
        }
        .btn-white { background: white; color: var(--primary); }
        .badge-live {
            background: #22c55e;
            color: white;
            font-size: 0.7rem;
            padding: 3px 8px;
            border-radius: 20px;
        }
        .page { max-width: 1400px; margin: 0 auto; padding: 24px; }
        
        /* Stats Grid */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }
        .stat-card {
            background: white;
            border-radius: 10px;
            padding: 16px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .stat-value { font-size: 2rem; font-weight: 800; color: var(--primary); }
        .stat-label { font-size: 0.75rem; color: var(--gray-500); text-transform: uppercase; }
        
        /* Tabs */
        .tabs {
            display: flex;
            gap: 4px;
            border-bottom: 2px solid var(--gray-200);
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        .tab {
            padding: 10px 20px;
            border: none;
            background: none;
            cursor: pointer;
            font-weight: 600;
            color: var(--gray-500);
            border-bottom: 2px solid transparent;
        }
        .tab.active {
            color: var(--primary);
            border-bottom-color: var(--primary);
        }
        
        /* Tables */
        .section {
            background: white;
            border-radius: 10px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .section-header {
            padding: 16px 20px;
            border-bottom: 1px solid var(--gray-200);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 10px;
        }
        .table-wrapper { overflow-x: auto; }
        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.875rem;
        }
        th {
            text-align: left;
            padding: 10px 16px;
            background: var(--gray-100);
            color: var(--gray-500);
            font-size: 0.7rem;
            text-transform: uppercase;
        }
        td {
            padding: 10px 16px;
            border-bottom: 1px solid var(--gray-200);
        }
        tr:last-child td { border-bottom: none; }
        
        .tag {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 20px;
            font-size: 0.7rem;
            font-weight: 600;
        }
        .tag-open, .tag-verified { background: #d1fae5; color: #065f46; }
        .tag-closed, .tag-rejected { background: #fee2e2; color: #991b1b; }
        .tag-submitted { background: #fef3c7; color: #92400e; }
        
        .loading-overlay {
            position: fixed;
            inset: 0;
            background: rgba(255,255,255,0.9);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 200;
        }
        .spinner {
            width: 40px;
            height: 40px;
            border: 4px solid var(--gray-200);
            border-top-color: var(--primary);
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
        
        .error-banner {
            background: #fee2e2;
            border: 1px solid #fca5a5;
            color: #991b1b;
            padding: 12px 16px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        
        .tab-panel { display: none; }
        .tab-panel.active { display: block; }
        
        .search-bar {
            padding: 6px 12px;
            border: 1px solid var(--gray-200);
            border-radius: 6px;
            outline: none;
        }
        .search-bar:focus { border-color: var(--primary); }
        
        code { background: var(--gray-100); padding: 2px 5px; border-radius: 4px; font-size: 0.8rem; }
    </style>
</head>
<body>

<header class="header">
    <div class="header-title">📋 Exam Portal <span>Admin Dashboard</span></div>
    <div class="header-actions">
        <span class="badge-live">● LIVE</span>
        <span id="last-updated">--:--:--</span>
        <button class="btn btn-white" onclick="loadAllData()">🔄 Refresh</button>
    </div>
</header>

<div class="loading-overlay" id="overlay">
    <div class="spinner"></div>
</div>

<div class="page">
    <div id="error-container"></div>
    
    <!-- Stats -->
    <div class="stats-grid" id="stats-grid">
        <div class="stat-card"><div class="stat-value" id="stat-students">-</div><div class="stat-label">Students</div></div>
        <div class="stat-card"><div class="stat-value" id="stat-exams">-</div><div class="stat-label">Exams</div></div>
        <div class="stat-card"><div class="stat-value" id="stat-applications">-</div><div class="stat-label">Applications</div></div>
        <div class="stat-card"><div class="stat-value" id="stat-verified">-</div><div class="stat-label">Verified</div></div>
        <div class="stat-card"><div class="stat-value" id="stat-pending">-</div><div class="stat-label">Pending</div></div>
        <div class="stat-card"><div class="stat-value" id="stat-open">-</div><div class="stat-label">Open Exams</div></div>
    </div>
    
    <!-- Tabs -->
    <div class="tabs">
        <button class="tab active" onclick="switchTab('students', this)">👨‍🎓 Students</button>
        <button class="tab" onclick="switchTab('exams', this)">📝 Exams</button>
        <button class="tab" onclick="switchTab('applications', this)">📂 Applications</button>
        <button class="tab" onclick="switchTab('hall_tickets', this)">🎫 Hall Tickets</button>
        <button class="tab" onclick="switchTab('documents', this)">📄 Documents</button>
    </div>
    
    <!-- Students Tab -->
    <div id="tab-students" class="tab-panel active">
        <div class="section">
            <div class="section-header">
                <span>👨‍🎓 Students</span>
                <div><input class="search-bar" id="search-students" placeholder="Search..." oninput="filterTable('students-table-body', this.value)"></div>
            </div>
            <div class="table-wrapper">
                <table>
                    <thead><tr><th>#</th><th>Student ID</th><th>Name</th><th>Email</th><th>Phone</th></tr></thead>
                    <tbody id="students-table-body"><tr><td colspan="5">Loading...</td></tr></tbody>
                </table>
            </div>
        </div>
    </div>
    
    <!-- Exams Tab -->
    <div id="tab-exams" class="tab-panel">
        <div class="section">
            <div class="section-header"><span>📝 Exams</span></div>
            <div class="table-wrapper">
                <table>
                    <thead><tr><th>ID</th><th>Exam Code</th><th>Exam Name</th><th>Status</th></tr></thead>
                    <tbody id="exams-table-body"><tr><td colspan="4">Loading...</td></tr></tbody>
                </table>
            </div>
        </div>
    </div>
    
    <!-- Applications Tab -->
    <div id="tab-applications" class="tab-panel">
        <div class="section">
            <div class="section-header"><span>📂 Applications</span></div>
            <div class="table-wrapper">
                <table>
                    <thead><tr><th>ID</th><th>Student ID</th><th>Exam ID</th><th>Status</th><th>Progress</th></tr></thead>
                    <tbody id="applications-table-body"><tr><td colspan="5">Loading...</td></tr></tbody>
                </table>
            </div>
        </div>
    </div>
    
    <!-- Hall Tickets Tab -->
    <div id="tab-hall_tickets" class="tab-panel">
        <div class="section">
            <div class="section-header"><span>🎫 Hall Tickets</span></div>
            <div class="table-wrapper">
                <table>
                    <thead><tr><th>ID</th><th>Ticket No</th><th>Student ID</th><th>Exam ID</th><th>Status</th></tr></thead>
                    <tbody id="halltickets-table-body"><tr><td colspan="5">Loading...</td></tr></tbody>
                </table>
            </div>
        </div>
    </div>
    
    <!-- Documents Tab -->
    <div id="tab-documents" class="tab-panel">
        <div class="section">
            <div class="section-header"><span>📄 Documents</span></div>
            <div class="table-wrapper">
                <table>
                    <thead><tr><th>ID</th><th>Student ID</th><th>Document Type</th><th>Status</th></tr></thead>
                    <tbody id="documents-table-body"><tr><td colspan="4">Loading...</td></tr></tbody>
                </table>
            </div>
        </div>
    </div>
</div>

<script>
    // ========== CONFIGURATION ==========
    const API_BASE_URL = "https://lmsmodern.infinityfree.me/proctored_api.php";
    const API_KEY = "render_backend_key_7x9k2m";
    
    // ========== HELPER FUNCTIONS ==========
    function buildUrl(endpoint, params = {}) {
        const urlParams = new URLSearchParams({
            endpoint: endpoint,
            api_key: API_KEY,
            ...params
        });
        return `${API_BASE_URL}?${urlParams.toString()}`;
    }
    
    async function apiCall(endpoint, params = {}) {
        const url = buildUrl(endpoint, params);
        console.log(`📡 Calling: ${url}`);
        
        try {
            const response = await fetch(url);
            const text = await response.text();
            
            // Clean any PHP warnings/notices before JSON
            let cleanText = text;
            const jsonStart = text.indexOf('{');
            const arrayStart = text.indexOf('[');
            let startPos = -1;
            if (arrayStart !== -1 && (jsonStart === -1 || arrayStart < jsonStart)) startPos = arrayStart;
            else if (jsonStart !== -1) startPos = jsonStart;
            
            if (startPos > 0) {
                console.warn(`⚠️ Trimmed ${startPos} characters of PHP output`);
                cleanText = text.substring(startPos);
            }
            
            const data = JSON.parse(cleanText);
            
            if (!data.success) {
                throw new Error(data.error || 'API returned error');
            }
            
            return data.data;
        } catch (error) {
            console.error(`API Error [${endpoint}]:`, error);
            throw error;
        }
    }
    
    function getStatusTag(status) {
        if (!status) return '<span class="tag">-</span>';
        const statusClass = {
            'open': 'tag-open', 'closed': 'tag-closed',
            'verified': 'tag-verified', 'submitted': 'tag-submitted',
            'rejected': 'tag-rejected'
        }[status.toLowerCase()] || 'tag-open';
        return `<span class="tag ${statusClass}">${status}</span>`;
    }
    
    function filterTable(tableId, searchText) {
        const tbody = document.getElementById(tableId);
        if (!tbody) return;
        const rows = tbody.querySelectorAll('tr');
        const search = searchText.toLowerCase();
        rows.forEach(row => {
            if (row.cells) {
                const text = Array.from(row.cells).map(cell => cell.textContent.toLowerCase()).join(' ');
                row.style.display = text.includes(search) ? '' : 'none';
            }
        });
    }
    
    function switchTab(tabName, btnElement) {
        document.querySelectorAll('.tab-panel').forEach(panel => panel.classList.remove('active'));
        document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
        document.getElementById(`tab-${tabName}`).classList.add('active');
        if (btnElement) btnElement.classList.add('active');
    }
    
    // ========== RENDER FUNCTIONS ==========
    function renderStudents(students) {
        const tbody = document.getElementById('students-table-body');
        if (!students || students.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5">No students found</td></tr>';
            return;
        }
        tbody.innerHTML = students.map((s, i) => `
            <tr>
                <td>${i + 1}</td>
                <td><code>${escapeHtml(s.student_id || '-')}</code></td>
                <td>${escapeHtml(s.full_name || s.name || '-')}</td>
                <td>${escapeHtml(s.email || '-')}</td>
                <td>${escapeHtml(s.phone || '-')}</td>
            </tr>
        `).join('');
    }
    
    function renderExams(exams) {
        const tbody = document.getElementById('exams-table-body');
        if (!exams || exams.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4">No exams found</td></tr>';
            return;
        }
        tbody.innerHTML = exams.map(e => `
            <tr>
                <td>${e.id}</td>
                <td><code>${escapeHtml(e.exam_code || '-')}</code></td>
                <td>${escapeHtml(e.exam_name || '-')}</td>
                <td>${getStatusTag(e.registration_status || e.status)}</td>
            </tr>
        `).join('');
    }
    
    function renderApplications(applications) {
        const tbody = document.getElementById('applications-table-body');
        if (!applications || applications.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5">No applications found</td></tr>';
            return;
        }
        tbody.innerHTML = applications.map(a => `
            <tr>
                <td>${a.id}</td>
                <td>${a.student_id}</td>
                <td>${a.exam_id}</td>
                <td>${getStatusTag(a.status)}</td>
                <td>${a.progress_percentage || 0}%</td>
            </tr>
        `).join('');
    }
    
    function renderHallTickets(tickets) {
        const tbody = document.getElementById('halltickets-table-body');
        if (!tickets || tickets.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5">No hall tickets found</td></tr>';
            return;
        }
        tbody.innerHTML = tickets.map(t => `
            <tr>
                <td>${t.id}</td>
                <td><code>${escapeHtml(t.hall_ticket_no || '-')}</code></td>
                <td>${t.student_id}</td>
                <td>${t.exam_id}</td>
                <td>${getStatusTag(t.status)}</td>
            </tr>
        `).join('');
    }
    
    function renderDocuments(documents) {
        const tbody = document.getElementById('documents-table-body');
        if (!documents || documents.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4">No documents found</td></tr>';
            return;
        }
        tbody.innerHTML = documents.map(d => `
            <tr>
                <td>${d.id}</td>
                <td>${d.student_id}</td>
                <td><code>${escapeHtml(d.document_type || '-')}</code></td>
                <td>${getStatusTag(d.status)}</td>
            </tr>
        `).join('');
    }
    
    function updateStats(stats, studentsCount, examsCount, appsCount) {
        document.getElementById('stat-students').textContent = stats?.total_students ?? studentsCount ?? 0;
        document.getElementById('stat-exams').textContent = stats?.total_exams ?? examsCount ?? 0;
        document.getElementById('stat-applications').textContent = stats?.total_applications ?? appsCount ?? 0;
        document.getElementById('stat-verified').textContent = stats?.verified_applications ?? 0;
        document.getElementById('stat-pending').textContent = stats?.pending_applications ?? 0;
        document.getElementById('stat-open').textContent = stats?.open_exams ?? 0;
    }
    
    function escapeHtml(str) {
        if (!str) return '';
        return String(str).replace(/[&<>]/g, function(m) {
            if (m === '&') return '&amp;';
            if (m === '<') return '&lt;';
            if (m === '>') return '&gt;';
            return m;
        });
    }
    
    function showError(message) {
        const container = document.getElementById('error-container');
        container.innerHTML = `<div class="error-banner">❌ ${escapeHtml(message)}</div>`;
        setTimeout(() => { if (container.innerHTML) container.innerHTML = ''; }, 8000);
    }
    
    // ========== MAIN LOAD FUNCTION ==========
    async function loadAllData() {
        const overlay = document.getElementById('overlay');
        overlay.style.display = 'flex';
        document.getElementById('error-container').innerHTML = '';
        
        try {
            // Fetch all data in parallel
            const [students, exams, applications, stats] = await Promise.all([
                apiCall('students', { limit: 200 }),
                apiCall('exams'),
                apiCall('applications', { limit: 200 }),
                apiCall('dashboard_stats')
            ]);
            
            const studentsArr = Array.isArray(students) ? students : [];
            const examsArr = Array.isArray(exams) ? exams : [];
            const appsArr = Array.isArray(applications) ? applications : [];
            const statsObj = stats && typeof stats === 'object' ? stats : {};
            
            // Fetch hall tickets (limit to first 3 exams)
            let allTickets = [];
            for (const exam of examsArr.slice(0, 3)) {
                try {
                    const tickets = await apiCall('hall_tickets', { exam_id: exam.id });
                    if (Array.isArray(tickets)) allTickets.push(...tickets);
                } catch (e) {
                    console.warn(`Failed to get tickets for exam ${exam.id}`);
                }
            }
            
            // Fetch documents (limit to first 5 students)
            let allDocs = [];
            for (const student of studentsArr.slice(0, 5)) {
                try {
                    const docs = await apiCall('documents', { student_id: student.id });
                    if (Array.isArray(docs)) allDocs.push(...docs);
                } catch (e) {
                    console.warn(`Failed to get documents for student ${student.id}`);
                }
            }
            
            // Render everything
            renderStudents(studentsArr);
            renderExams(examsArr);
            renderApplications(appsArr);
            renderHallTickets(allTickets);
            renderDocuments(allDocs);
            updateStats(statsObj, studentsArr.length, examsArr.length, appsArr.length);
            
            document.getElementById('last-updated').textContent = new Date().toLocaleTimeString();
            
        } catch (error) {
            console.error('Load error:', error);
            showError(`Failed to load data: ${error.message}`);
        } finally {
            overlay.style.display = 'none';
        }
    }
    
    // Connect search inputs
    document.getElementById('search-students')?.addEventListener('input', (e) => {
        filterTable('students-table-body', e.target.value);
    });
    
    // Load on page load
    loadAllData();
    setInterval(loadAllData, 60000); // Auto-refresh every minute
</script>
</body>
</html>
