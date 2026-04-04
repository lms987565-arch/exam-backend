# backend/routes/dashboard.py
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

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
    <title>Exam Portal Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        h1 { color: white; text-align: center; margin-bottom: 10px; font-size: 2.5rem; }
        .subtitle { color: rgba(255,255,255,0.9); text-align: center; margin-bottom: 30px; }
        .refresh-btn {
            display: block; margin: 0 auto 20px; padding: 12px 24px;
            background: white; color: #667eea; border: none; border-radius: 25px;
            font-size: 1rem; font-weight: bold; cursor: pointer;
            transition: all 0.3s;
        }
        .refresh-btn:hover { transform: scale(1.05); background: #f0f0f0; }
        .loading { text-align: center; color: white; padding: 50px; }
        .stats-grid {
            display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px; margin-bottom: 30px;
        }
        .stat-card {
            background: white; border-radius: 15px; padding: 20px; text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2); transition: transform 0.3s;
        }
        .stat-card:hover { transform: translateY(-5px); }
        .stat-number { font-size: 2.5rem; font-weight: bold; color: #667eea; }
        .stat-label { color: #666; margin-top: 10px; }
        .section {
            background: white; border-radius: 15px; padding: 25px;
            margin-bottom: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .section-title {
            font-size: 1.5rem; margin-bottom: 20px; color: #333;
            border-left: 4px solid #667eea; padding-left: 15px;
        }
        .table-wrapper { overflow-x: auto; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #667eea; color: white; font-weight: bold; }
        tr:hover { background: #f5f5f5; }
        .badge {
            display: inline-block; padding: 4px 12px; border-radius: 20px;
            font-size: 0.85rem; font-weight: bold;
        }
        .badge-success { background: #d4edda; color: #155724; }
        .badge-warning { background: #fff3cd; color: #856404; }
        .badge-info { background: #d1ecf1; color: #0c5460; }
        .error { background: #f8d7da; color: #721c24; padding: 15px; border-radius: 10px; }
        .footer { text-align: center; color: rgba(255,255,255,0.8); margin-top: 30px; }
        .spinner {
            border: 4px solid rgba(255,255,255,0.3); border-radius: 50%;
            border-top: 4px solid white; width: 40px; height: 40px;
            animation: spin 1s linear infinite; margin: 20px auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Exam Portal Dashboard</h1>
        <div class="subtitle">Real-time data from InfinityFree Database</div>
        <button class="refresh-btn" onclick="fetchAllData()">🔄 Refresh All Data</button>
        <div id="loading" class="loading"><div class="spinner"></div>Loading data...</div>
        <div id="content" style="display: none;"></div>
        <div class="footer">Last updated: <span id="timestamp">-</span></div>
    </div>
    
    <script>
        const API_BASE = window.location.origin;
        
        async function fetchAllData() {
            document.getElementById('loading').style.display = 'block';
            document.getElementById('content').style.display = 'none';
            
            try {
                // Fetch data from all endpoints
                const [studentsRes, examsRes, statsRes] = await Promise.all([
                    fetch(`${API_BASE}/api/students`).then(r => r.json()),
                    fetch(`${API_BASE}/api/exams`).then(r => r.json()),
                    fetch(`${API_BASE}/api/dashboard/stats`).then(r => r.json())
                ]);
                
                // Extract data arrays
                const students = studentsRes.data || [];
                const exams = examsRes.data || [];
                const stats = statsRes.data || {};
                
                renderDashboard(students, exams, stats);
                document.getElementById('timestamp').innerText = new Date().toLocaleString();
            } catch (error) {
                console.error('Error:', error);
                document.getElementById('content').innerHTML = `<div class="error">❌ Error loading data: ${error.message}</div>`;
            } finally {
                document.getElementById('loading').style.display = 'none';
                document.getElementById('content').style.display = 'block';
            }
        }
        
        function renderDashboard(students, exams, stats) {
            const html = `
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-number">${students.length || 0}</div>
                        <div class="stat-label">👨‍🎓 Total Students</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${exams.length || 0}</div>
                        <div class="stat-label">📝 Total Exams</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${stats.total_students || 0}</div>
                        <div class="stat-label">📊 Database Count</div>
                    </div>
                </div>
                
                <div class="section">
                    <h2 class="section-title">👨‍🎓 Students (${students.length})</h2>
                    <div class="table-wrapper">
                        <table>
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Student ID</th>
                                    <th>Email</th>
                                    <th>Phone</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${students.map(s => `
                                    <tr>
                                        <td>${s.id || '-'}</td>
                                        <td><strong>${s.student_id || '-'}</strong></td>
                                        <td>${s.email || '-'}</td>
                                        <td>${s.phone || '-'}</td>
                                    </tr>
                                `).join('')}
                                ${students.length === 0 ? '<tr><td colspan="4" style="text-align:center">No students found</td></tr>' : ''}
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <div class="section">
                    <h2 class="section-title">📝 Exams (${exams.length})</h2>
                    <div class="table-wrapper">
                        <table>
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Exam Code</th>
                                    <th>Exam Name</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${exams.map(e => `
                                    <tr>
                                        <td>${e.id || '-'}</td>
                                        <td><strong>${e.exam_code || '-'}</strong></td>
                                        <td>${e.exam_name || '-'}</td>
                                    </tr>
                                `).join('')}
                                ${exams.length === 0 ? '<tr><td colspan="3" style="text-align:center">No exams found</td></tr>' : ''}
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
