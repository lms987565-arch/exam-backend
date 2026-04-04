# backend/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import httpx
from dotenv import load_dotenv
from routes import exam, staff
from routes.dashboard import router as dashboard_router
from config.infinityfree_client import infinityfree_client

load_dotenv()

app = FastAPI(
    title="Modern College Exam Portal API",
    description="Online proctored examination system",
    version="2.0.0"
)

# CORS configuration
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        FRONTEND_URL,
        "http://localhost:3000",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:8080",
        "https://exam-frontend-8m0b.onrender.com",
        "https://*.onrender.com",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(exam.router, prefix="/api/exam", tags=["Exam"])
app.include_router(staff.router, prefix="/api/staff", tags=["Staff"])
app.include_router(dashboard_router)


@app.get("/")
def root():
    return {
        "status": "running",
        "message": "Modern College Exam Portal API",
        "version": "2.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


# ==================== DEBUG ENDPOINT ====================

@app.get("/api/debug/test-connection")
async def test_connection():
    """Debug endpoint to test InfinityFree connectivity from Render"""
    results = {}
    
    # Test 1: Direct HTTP request to InfinityFree
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get("https://lmsmodern.infinityfree.me/proctored_api.php?endpoint=students")
            results['direct_request'] = {
                'status': response.status_code,
                'success': response.status_code == 200,
                'preview': response.text[:200] if response.status_code == 200 else None
            }
    except Exception as e:
        results['direct_request'] = {'error': str(e)}
    
    # Test 2: Through our client
    try:
        students = await infinityfree_client.get_all_students(5)
        results['client_test'] = {
            'success': True,
            'count': len(students),
            'sample': students[:2] if students else []
        }
    except Exception as e:
        results['client_test'] = {'error': str(e)}
    
    return results


# ==================== MAIN API ENDPOINTS (with fallbacks) ====================

@app.get("/api/students")
async def get_all_students(limit: int = 100):
    """Get all students - with fallback to empty list on error"""
    try:
        students = await infinityfree_client.get_all_students(limit)
        if not isinstance(students, list):
            students = []
        return {"success": True, "data": students}
    except Exception as e:
        print(f"Error in /api/students: {str(e)}")
        # Return empty list instead of 500 error
        return {"success": True, "data": []}


@app.get("/api/exams")
async def get_all_exams():
    """Get all exams - with fallback to empty list on error"""
    try:
        exams = await infinityfree_client.get_all_exams()
        if not isinstance(exams, list):
            exams = []
        return {"success": True, "data": exams}
    except Exception as e:
        print(f"Error in /api/exams: {str(e)}")
        return {"success": True, "data": []}


@app.get("/api/applications")
async def get_all_applications(limit: int = 100):
    """Get all applications - with fallback to empty list on error"""
    try:
        applications = await infinityfree_client.get_all_applications(limit)
        if not isinstance(applications, list):
            applications = []
        return {"success": True, "data": applications}
    except Exception as e:
        print(f"Error in /api/applications: {str(e)}")
        return {"success": True, "data": []}


@app.get("/api/hall_tickets/all")
async def get_all_hall_tickets(limit: int = 100):
    """Get all hall tickets from all exams - with fallback"""
    try:
        exams = await infinityfree_client.get_all_exams()
        if not isinstance(exams, list):
            return {"success": True, "data": []}
        
        all_tickets = []
        for exam in exams[:5]:  # Limit to first 5 exams to avoid timeout
            tickets = await infinityfree_client.get_hall_tickets_by_exam(exam['id'])
            if isinstance(tickets, list):
                all_tickets.extend(tickets)
        return {"success": True, "data": all_tickets[:limit]}
    except Exception as e:
        print(f"Error in /api/hall_tickets/all: {str(e)}")
        return {"success": True, "data": []}


@app.get("/api/exam_schedule/all")
async def get_all_schedule(limit: int = 200):
    """Get all exam schedules - with fallback"""
    try:
        exams = await infinityfree_client.get_all_exams()
        if not isinstance(exams, list):
            return {"success": True, "data": []}
        
        all_schedule = []
        for exam in exams[:5]:  # Limit to first 5 exams to avoid timeout
            schedule = await infinityfree_client.get_exam_schedule(exam['id'])
            if isinstance(schedule, list):
                all_schedule.extend(schedule)
        return {"success": True, "data": all_schedule[:limit]}
    except Exception as e:
        print(f"Error in /api/exam_schedule/all: {str(e)}")
        return {"success": True, "data": []}


@app.get("/api/documents/all")
async def get_all_documents(limit: int = 200):
    """Get all documents from all students - with fallback"""
    try:
        students = await infinityfree_client.get_all_students(20)  # Limit students
        if not isinstance(students, list):
            return {"success": True, "data": []}
        
        all_docs = []
        for student in students:
            if isinstance(student, dict) and student.get('id'):
                docs = await infinityfree_client.get_student_documents(student['id'])
                if isinstance(docs, list):
                    all_docs.extend(docs)
        return {"success": True, "data": all_docs[:limit]}
    except Exception as e:
        print(f"Error in /api/documents/all: {str(e)}")
        return {"success": True, "data": []}


@app.get("/api/tokens/all")
async def get_all_tokens(limit: int = 100):
    """Get all tokens - returns empty as placeholder"""
    return {"success": True, "data": []}


@app.get("/api/dashboard/stats")
async def get_dashboard_stats():
    """Get dashboard statistics - with fallback values"""
    try:
        stats = await infinityfree_client.get_dashboard_stats()
        if not isinstance(stats, dict):
            stats = {
                'total_students': 0,
                'open_exams': 0,
                'verified_applications': 0
            }
        return {"success": True, "data": stats}
    except Exception as e:
        print(f"Error in /api/dashboard/stats: {str(e)}")
        # Return default stats instead of 500 error
        return {
            "success": True, 
            "data": {
                "total_students": 0,
                "open_exams": 0,
                "verified_applications": 0
            }
        }


# ==================== INDIVIDUAL ENDPOINTS (for dashboard) ====================

@app.get("/api/hall_tickets")
async def get_hall_tickets(student_id: int = None, exam_id: int = None):
    """Get hall tickets by student_id or exam_id"""
    try:
        if student_id:
            tickets = await infinityfree_client.get_hall_tickets_by_student(student_id)
        elif exam_id:
            tickets = await infinityfree_client.get_hall_tickets_by_exam(exam_id)
        else:
            tickets = []
        
        if not isinstance(tickets, list):
            tickets = []
        return {"success": True, "data": tickets}
    except Exception as e:
        print(f"Error in /api/hall_tickets: {str(e)}")
        return {"success": True, "data": []}


@app.get("/api/exam_schedule")
async def get_exam_schedule(exam_id: int):
    """Get exam schedule by exam_id"""
    try:
        if not exam_id:
            return {"success": True, "data": []}
        schedule = await infinityfree_client.get_exam_schedule(exam_id)
        if not isinstance(schedule, list):
            schedule = []
        return {"success": True, "data": schedule}
    except Exception as e:
        print(f"Error in /api/exam_schedule: {str(e)}")
        return {"success": True, "data": []}


@app.get("/api/documents")
async def get_documents(student_id: int):
    """Get documents by student_id"""
    try:
        if not student_id:
            return {"success": True, "data": []}
        documents = await infinityfree_client.get_student_documents(student_id)
        if not isinstance(documents, list):
            documents = []
        return {"success": True, "data": documents}
    except Exception as e:
        print(f"Error in /api/documents: {str(e)}")
        return {"success": True, "data": []}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
