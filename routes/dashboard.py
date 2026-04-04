# backend/routes/dashboard.py
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import HTMLResponse
from typing import Dict, List
from datetime import datetime
from config.infinityfree_client import infinityfree_client

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/", response_class=HTMLResponse)
async def get_dashboard_html():
    """Return HTML dashboard page"""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Exam Portal - Complete Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        h1 {
            color: white;
            text-align: center;
            margin-bottom: 10px;
            font-size: 2.5rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }
        
        .subtitle {
            color: rgba(255,255,255,0.9);
            text-align: center;
            margin-bottom: 30px;
            font-size: 1rem;
        }
        
        .refresh-btn {
            display: block;
            margin: 0 auto 20px;
            padding: 12px 24px;
            background: white;
            color: #667eea;
            border: none;
            border-radius: 25px;
            font-size: 1rem;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }
        
        .refresh-btn:hover {
            transform: scale(1.05);
            box-shadow: 0 6px 20px rgba(0,0,0,0.3);
        }
        
        .loading {
            text-align: center;
            color: white;
            font-size: 1.2rem;
            padding: 50px;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: white;
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            transition: transform 0.3s;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
        }
        
        .stat-number {
            font-size: 2.5rem;
            font-weight: bold;
            color: #667eea;
        }
        
        .stat-label {
            color: #666;
            margin-top: 10px;
            font-size: 0.9rem;
        }
        
        .section {
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        
        .section-title {
            font-size: 1.5rem;
            margin-bottom: 20px;
            color: #333;
            border-left: 4px solid #667eea;
            padding-left: 15px;
        }
        
        .table-wrapper {
            overflow-x: auto;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
        }
        
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        
        th {
            background: #667eea;
            color: white;
            font-weight: bold;
        }
        
        tr:hover {
            background: #f5f5f5;
        }
        
        .badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: bold;
        }
        
        .badge-success {
            background: #d4edda;
            color: #155724;
        }
        
        .badge-warning {
            background: #fff3cd;
            color: #856404;
        }
        
        .badge-danger {
            background: #f8d7da;
            color: #721c24;
        }
        
        .badge-info {
            background: #d1ecf1;
            color: #0c5460;
        }
        
        .error {
            background: #f8d7da;
            color: #721c24;
            padding: 15px;
            border-radius: 10px;
            margin: 20px 0;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .spinner {
            border: 4px solid rgba(255,255,255,0.3);
            border-radius: 50%;
            border-top: 4px solid white;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }
        
        .footer {
            text-align: center;
            color: rgba(255,255,255,0.8);
            margin-top: 30px;
            padding: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Exam Portal Dashboard</h1>
        <div class="subtitle">Real-time data from InfinityFree Database</div>
        
        <button class="refresh-btn" onclick="fetchAllData()">🔄 Refresh All Data</button>
        
        <div id="loading" class="loading">
            <div class="spinner"></div>
            Loading data from database...
        </div>
        
        <div id="content" style="display: none;"></div>
        
        <div class="footer">
            Last updated: <span id="timestamp">-</span>
        </div>
    </div>
    
    <script>
        const API_BASE = window.location.origin;
        
        async function fetchAllData() {
            document.getElementById('loading').style.display = 'block';
            document.getElementById('content').style.display = 'none';
            
            try {
                // Fetch all data in parallel
                const [students, exams, applications, hallTickets, schedule, documents, tokens, stats] = await Promise.all([
                    fetchData('/api/students'),
                    fetchData('/api/exams'),
                    fetchData('/api/applications'),
                    fetchData('/api/hall_tickets/all'),
                    fetchData('/api/exam_schedule/all'),
                    fetchData('/api/documents/all'),
                    fetchData('/api/tokens/all'),
                    fetchData('/api/dashboard/stats')
                ]);
                
                // Render everything
                renderDashboard({
                    students: students.data || [],
                    exams: exams.data || [],
                    applications: applications.data || [],
                    hallTickets: hallTickets.data || [],
                    schedule: schedule.data || [],
                    documents: documents.data || [],
                    tokens: tokens.data || [],
                    stats: stats.data || {}
                });
                
                document.getElementById('timestamp').innerText = new Date().toLocaleString();
                
            } catch (error) {
                console.error('Error fetching data:', error);
                document.getElementById('content').innerHTML = `<div class="error">❌ Error loading data: ${error.message}</div>`;
            } finally {
                document.getElementById('loading').style.display = 'none';
                document.getElementById('content').style.display = 'block';
            }
        }
        
        async function fetchData(endpoint) {
            const response = await fetch(`${API_BASE}${endpoint}`);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${endpoint}`);
            }
            return await response.json();
        }
        
        function renderDashboard(data) {
            const students = data.students || [];
            const exams = data.exams || [];
            const applications = data.applications || [];
            const hallTickets = data.hallTickets || [];
            const schedule = data.schedule || [];
            const documents = data.documents || [];
            const tokens = data.tokens || [];
            const stats = data.stats || {};
            
            const verifiedApps = applications.filter(a => a.status === 'verified').length;
            const pendingApps = applications.filter(a => a.status === 'submitted').length;
            const verifiedDocs = documents.filter(d => d.status === 'verified').length;
            
            const html = `
                <!-- Statistics Cards -->
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-number">${students.length}</div>
                        <div class="stat-label">👨‍🎓 Total Students</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${exams.length}</div>
                        <div class="stat-label">📝 Active Exams</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${applications.length}</div>
                        <div class="stat-label">📋 Applications</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${verifiedApps}</div>
                        <div class="stat-label">✅ Verified Applications</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${pendingApps}</div>
                        <div class="stat-label">⏳ Pending Verification</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${hallTickets.length}</div>
                        <div class="stat-label">🎫 Hall Tickets</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${documents.length}</div>
                        <div class="stat-label">📄 Documents Uploaded</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${verifiedDocs}</div>
                        <div class="stat-label">✓ Verified Documents</div>
                    </div>
                </div>
                
                <!-- Students Section -->
                <div class="section">
                    <h2 class="section-title">👨‍🎓 Students (${students.length})</h2>
                    <div class="table-wrapper">
                        <table>
                            <thead>
                                <tr><th>ID</th><th>Student ID</th><th>Name/Email</th><th>Phone</th><th>Status</th><th>Created</th></tr>
                            </thead>
                            <tbody>
                                ${students.map(s => `
                                    <tr>
                                        <td>${s.id || '-'}</td>
                                        <td>${s.student_id || '-'}</td>
                                        <td>${s.email || '-'}</td>
                                        <td>${s.phone || '-'}</td>
                                        <td><span class="badge ${s.status === 'active' ? 'badge-success' : 'badge-warning'}">${s.status || 'active'}</span></td>
                                        <td>${s.created_at ? new Date(s.created_at).toLocaleDateString() : '-'}</td>
                                    </tr>
                                `).join('')}
                                ${students.length === 0 ? '<tr><td colspan="6" style="text-align:center">No students found</td></tr>' : ''}
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- Exams Section -->
                <div class="section">
                    <h2 class="section-title">📝 Exams (${exams.length})</h2>
                    <div class="table-wrapper">
                        <table>
                            <thead>
                                <tr><th>ID</th><th>Exam Code</th><th>Exam Name</th><th>Level</th><th>Registration</th><th>Status</th><th>Duration</th></tr>
                            </thead>
                            <tbody>
                                ${exams.map(e => `
                                    <tr>
                                        <td>${e.id || '-'}</td>
                                        <td><strong>${e.exam_code || '-'}</strong></td>
                                        <td>${e.exam_name || '-'}</td>
                                        <td>${e.level || '-'}</td>
                                        <td><span class="badge ${e.registration_status === 'open' ? 'badge-success' : 'badge-danger'}">${e.registration_status || 'closed'}</span></td>
                                        <td><span class="badge ${e.exam_status === 'active' ? 'badge-success' : 'badge-info'}">${e.exam_status || 'upcoming'}</span></td>
                                        <td>${e.duration_minutes || '-'} min</td>
                                    </tr>
                                `).join('')}
                                ${exams.length === 0 ? '<tr><td colspan="7" style="text-align:center">No exams found</td></tr>' : ''}
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- Applications Section -->
                <div class="section">
                    <h2 class="section-title">📋 Exam Applications (${applications.length})</h2>
                    <div class="table-wrapper">
                        <table>
                            <thead>
                                <tr><th>ID</th><th>Student ID</th><th>Exam Name</th><th>Full Name</th><th>Status</th><th>Progress</th><th>Submitted</th></tr>
                            </thead>
                            <tbody>
                                ${applications.map(a => `
                                    <tr>
                                        <td>${a.id || '-'}</td>
                                        <td>${a.student_id || '-'}</td>
                                        <td>${(a.exam_name || '').substring(0, 30)}${(a.exam_name || '').length > 30 ? '...' : ''}</td>
                                        <td>${a.full_name || '-'}</td>
                                        <td><span class="badge ${a.status === 'verified' ? 'badge-success' : a.status === 'submitted' ? 'badge-warning' : 'badge-info'}">${a.status || 'draft'}</span></td>
                                        <td>${a.progress_percentage || 0}%</td>
                                        <td>${a.submitted_at ? new Date(a.submitted_at).toLocaleDateString() : '-'}</td>
                                    </tr>
                                `).join('')}
                                ${applications.length === 0 ? '<tr><td colspan="7" style="text-align:center">No applications found</td></tr>' : ''}
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- Hall Tickets Section -->
                <div class="section">
                    <h2 class="section-title">🎫 Hall Tickets (${hallTickets.length})</h2>
                    <div class="table-wrapper">
                        <table>
                            <thead>
                                <tr><th>Hall Ticket No</th><th>Student Name</th><th>Exam Name</th><th>Center</th><th>Seat</th><th>Slot</th><th>Status</th></tr>
                            </thead>
                            <tbody>
                                ${hallTickets.map(h => `
                                    <tr>
                                        <td><strong>${h.hall_ticket_no || '-'}</strong></td>
                                        <td>${h.full_name || '-'}</td>
                                        <td>${(h.exam_name || '').substring(0, 25)}${(h.exam_name || '').length > 25 ? '...' : ''}</td>
                                        <td>${h.exam_center || '-'}</td>
                                        <td>${h.seat_number || '-'}</td>
                                        <td>${h.slot || '-'}</td>
                                        <td><span class="badge ${h.status === 'issued' ? 'badge-success' : 'badge-warning'}">${h.status || 'draft'}</span></td>
                                    </tr>
                                `).join('')}
                                ${hallTickets.length === 0 ? '<tr><td colspan="7" style="text-align:center">No hall tickets found</td></tr>' : ''}
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- Exam Schedule Section -->
                <div class="section">
                    <h2 class="section-title">📅 Exam Schedule (${schedule.length})</h2>
                    <div class="table-wrapper">
                        <table>
                            <thead>
                                <tr><th>Exam ID</th><th>Day</th><th>Date</th><th>Slot</th><th>Subject</th><th>Time</th><th>Status</th><th>Capacity</th></tr>
                            </thead>
                            <tbody>
                                ${schedule.map(s => `
                                    <tr>
                                        <td>${s.exam_id || '-'}</td>
                                        <td>Day ${s.day_number || '-'}</td>
                                        <td>${s.exam_date || '-'}</td>
                                        <td>${s.slot || '-'}</td>
                                        <td>${s.subject_name || '-'}</td>
                                        <td>${s.slot_start || '-'} - ${s.slot_end || '-'}</td>
                                        <td><span class="badge ${s.status === 'open' ? 'badge-success' : 'badge-info'}">${s.status || 'upcoming'}</span></td>
                                        <td>${s.booked_count || 0}/${s.max_students || '-'}</td>
                                    </tr>
                                `).join('')}
                                ${schedule.length === 0 ? '<tr><td colspan="8" style="text-align:center">No schedule found</td></tr>' : ''}
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- Documents Section -->
                <div class="section">
                    <h2 class="section-title">📄 Student Documents (${documents.length})</h2>
                    <div class="table-wrapper">
                        <table>
                            <thead>
                                <tr><th>ID</th><th>Student ID</th><th>Document Type</th><th>Status</th><th>Verified By</th><th>Uploaded</th></tr>
                            </thead>
                            <tbody>
                                ${documents.map(d => `
                                    <tr>
                                        <td>${d.id || '-'}</td>
                                        <td>${d.student_id || '-'}</td>
                                        <td><strong>${d.document_type || '-'}</strong></td>
                                        <td><span class="badge ${d.status === 'verified' ? 'badge-success' : d.status === 'pending' ? 'badge-warning' : 'badge-info'}">${d.status || 'pending'}</span></td>
                                        <td>${d.verified_by || '-'}</td>
                                        <td>${d.uploaded_at ? new Date(d.uploaded_at).toLocaleDateString() : '-'}</td>
                                    </tr>
                                `).join('')}
                                ${documents.length === 0 ? '<tr><td colspan="6" style="text-align:center">No documents found</td></tr>' : ''}
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- Tokens Section -->
                <div class="section">
                    <h2 class="section-title">🔑 Exam Tokens (${tokens.length})</h2>
                    <div class="table-wrapper">
                        <table>
                            <thead>
                                <tr><th>Token No</th><th>Student ID</th><th>Exam ID</th><th>Status</th><th>Issued</th><th>Expires</th></tr>
                            </thead>
                            <tbody>
                                ${tokens.map(t => `
                                    <tr>
                                        <td><code>${t.token_no || '-'}</code></td>
                                        <td>${t.student_id || '-'}</td>
                                        <td>${t.exam_id || '-'}</td>
                                        <td><span class="badge ${t.status === 'active' ? 'badge-success' : 'badge-danger'}">${t.status || 'active'}</span></td>
                                        <td>${t.issued_at ? new Date(t.issued_at).toLocaleDateString() : '-'}</td>
                                        <td>${t.expires_at ? new Date(t.expires_at).toLocaleDateString() : '-'}</td>
                                    </tr>
                                `).join('')}
                                ${tokens.length === 0 ? '<tr><td colspan="6" style="text-align:center">No tokens found</td></tr>' : ''}
                            </tbody>
                        </table>
                    </div>
                </div>
            `;
            
            document.getElementById('content').innerHTML = html;
        }
        
        // Load data on page load
        fetchAllData();
        
        // Auto-refresh every 30 seconds
        setInterval(fetchAllData, 30000);
    </script>
</body>
</html>
    """
    

@router.get("/data/all")
async def get_all_data():
    """Fetch all data from all tables"""
    try:
        # Fetch all data in parallel
        students = await infinityfree_client.get_all_students(100)
        exams = await infinityfree_client.get_all_exams()
        applications = await infinityfree_client.get_all_applications(100)
        stats = await infinityfree_client.get_dashboard_stats()
        
        # Get additional data
        hall_tickets = []
        for exam in exams[:5]:  # Limit to first 5 exams
            tickets = await infinityfree_client.get_hall_tickets_by_exam(exam['id'])
            hall_tickets.extend(tickets[:20])  # Limit per exam
        
        return {
            "success": True,
            "data": {
                "students": students,
                "exams": exams,
                "applications": applications,
                "hall_tickets": hall_tickets[:100],  # Limit total
                "stats": stats
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
