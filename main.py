# backend/main.py
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(exam.router,      prefix="/api/exam",  tags=["Exam"])
app.include_router(staff.router,     prefix="/api/staff", tags=["Staff"])
app.include_router(dashboard_router)


# ==================== GLOBAL ERROR HANDLER ====================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": str(exc), "data": None}
    )


# ==================== ROOT & HEALTH ====================

@app.get("/", tags=["Health"])
def root():
    return {
        "status": "running",
        "message": "Modern College Exam Portal API",
        "version": "2.0.0",
        "docs": "/docs"
    }


@app.get("/health", tags=["Health"])
async def health():
    """Health check — also pings the remote DB via dashboard_stats"""
    try:
        stats = await infinityfree_client.get_dashboard_stats()
        return {
            "status": "healthy",
            "db": "connected",
            "stats": stats
        }
    except Exception as e:
        return {
            "status": "degraded",
            "db": "unreachable",
            "error": str(e)
        }


# ==================== DEBUG ENDPOINTS ====================

@app.get("/api/debug/env", tags=["Debug"])
async def debug_environment():
    """Check if environment variables are loaded"""
    return {
        "INFINITYFREE_API_KEY": os.getenv("INFINITYFREE_API_KEY", "NOT SET"),
        "INFINITYFREE_BASE_URL": os.getenv("INFINITYFREE_BASE_URL", "NOT SET"),
        "API_KEY_LENGTH": len(os.getenv("INFINITYFREE_API_KEY", "")),
    }


@app.get("/api/debug/direct", tags=["Debug"])
async def debug_direct_call():
    """Test direct HTTP call to InfinityFree API"""
    api_key = os.getenv("INFINITYFREE_API_KEY", "render_backend_key_7x9k2m")
    base_url = os.getenv("INFINITYFREE_BASE_URL", "https://lmsmodern.infinityfree.me/proctored_api.php")
    
    # Build URL with api_key as query parameter
    url = f"{base_url}?endpoint=students&api_key={api_key}"
    
    results = {
        "url_called": url,
        "api_key_used": api_key[:10] + "...",
        "base_url_used": base_url
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0, verify=True) as client:
            response = await client.get(url)
            results["status_code"] = response.status_code
            results["response_preview"] = response.text[:500] if response.text else "Empty response"
            
            # Try to parse JSON
            try:
                import json
                data = json.loads(response.text)
                results["success"] = data.get("success", False)
                results["data_count"] = len(data.get("data", [])) if data.get("data") else 0
            except:
                results["json_parse_error"] = True
                
    except httpx.TimeoutException:
        results["error"] = "Timeout - InfinityFree took too long to respond"
    except httpx.ConnectError as e:
        results["error"] = f"Connection error: {str(e)}"
    except Exception as e:
        results["error"] = str(e)
    
    return results


@app.get("/api/debug/client", tags=["Debug"])
async def debug_client_call():
    """Test the infinityfree_client directly"""
    try:
        students = await infinityfree_client.get_all_students(limit=5)
        return {
            "success": True,
            "student_count": len(students),
            "students": students[:3] if students else [],
            "error": None
        }
    except Exception as e:
        return {
            "success": False,
            "student_count": 0,
            "students": [],
            "error": str(e)
        }


@app.get("/api/debug/ping", tags=["Debug"])
async def debug_ping():
    """Test if InfinityFree domain is reachable"""
    results = {}
    
    # Test 1: Basic ping to domain
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get("https://lmsmodern.infinityfree.me")
            results["domain_reachable"] = True
            results["domain_status"] = response.status_code
    except Exception as e:
        results["domain_reachable"] = False
        results["domain_error"] = str(e)
    
    # Test 2: DNS resolution
    try:
        import socket
        ip = socket.gethostbyname("lmsmodern.infinityfree.me")
        results["ip_address"] = ip
    except Exception as e:
        results["ip_error"] = str(e)
    
    return results


# ==================== STUDENTS ====================

@app.get("/api/students", tags=["Students"])
async def get_all_students(limit: int = 100):
    """Get all students"""
    try:
        students = await infinityfree_client.get_all_students(limit)
        return {"success": True, "count": len(students), "data": students}
    except Exception as e:
        print(f"❌ /api/students error: {e}")
        return {"success": False, "error": str(e), "data": []}


@app.get("/api/students/{student_id}", tags=["Students"])
async def get_student(student_id: int):
    """Get single student by DB id"""
    try:
        student = await infinityfree_client.get_student_by_id(student_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        return {"success": True, "data": student}
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ /api/students/{student_id} error: {e}")
        return {"success": False, "error": str(e), "data": None}


# ==================== EXAMS ====================

@app.get("/api/exams", tags=["Exams"])
async def get_all_exams():
    """Get all exams"""
    try:
        exams = await infinityfree_client.get_all_exams()
        return {"success": True, "count": len(exams), "data": exams}
    except Exception as e:
        print(f"❌ /api/exams error: {e}")
        return {"success": False, "error": str(e), "data": []}


@app.get("/api/exams/{exam_id}", tags=["Exams"])
async def get_exam(exam_id: int):
    """Get single exam"""
    try:
        exam_data = await infinityfree_client.get_exam_by_id(exam_id)
        if not exam_data:
            raise HTTPException(status_code=404, detail="Exam not found")
        return {"success": True, "data": exam_data}
    except HTTPException:
        raise
    except Exception as e:
        return {"success": False, "error": str(e), "data": None}


@app.get("/api/exams/open/list", tags=["Exams"])
async def get_open_exams():
    """Get exams open for registration"""
    try:
        exams = await infinityfree_client.get_open_exams()
        return {"success": True, "count": len(exams), "data": exams}
    except Exception as e:
        return {"success": False, "error": str(e), "data": []}


# ==================== APPLICATIONS ====================

@app.get("/api/applications", tags=["Applications"])
async def get_all_applications(limit: int = 100):
    """Get all applications"""
    try:
        applications = await infinityfree_client.get_all_applications(limit)
        return {"success": True, "count": len(applications), "data": applications}
    except Exception as e:
        print(f"❌ /api/applications error: {e}")
        return {"success": False, "error": str(e), "data": []}


@app.get("/api/applications/student/{student_id}", tags=["Applications"])
async def get_student_applications(student_id: int):
    """Get applications for a student"""
    try:
        apps = await infinityfree_client.get_applications_by_student(student_id)
        return {"success": True, "count": len(apps), "data": apps}
    except Exception as e:
        return {"success": False, "error": str(e), "data": []}


# ==================== DASHBOARD STATS ====================

@app.get("/api/dashboard/stats", tags=["Dashboard"])
async def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        stats = await infinityfree_client.get_dashboard_stats()
        return {"success": True, "data": stats}
    except Exception as e:
        print(f"❌ /api/dashboard/stats error: {e}")
        return {
            "success": False,
            "error": str(e),
            "data": {
                "total_students": 0,
                "total_exams": 0,
                "total_applications": 0,
                "open_exams": 0,
                "verified_applications": 0,
                "pending_applications": 0,
            }
        }


@app.get("/api/dashboard/student/{student_id}", tags=["Dashboard"])
async def get_student_dashboard(student_id: int):
    """Get full student dashboard data"""
    try:
        data = await infinityfree_client.get_student_dashboard(student_id)
        return {"success": True, "data": data}
    except Exception as e:
        return {"success": False, "error": str(e), "data": None}


@app.get("/api/dashboard/admin", tags=["Dashboard"])
async def get_admin_dashboard():
    """Get full admin dashboard data"""
    try:
        data = await infinityfree_client.get_admin_dashboard()
        return {"success": True, "data": data}
    except Exception as e:
        return {"success": False, "error": str(e), "data": None}


# ==================== HALL TICKETS ====================

@app.get("/api/hall_tickets/all", tags=["Hall Tickets"])
async def get_all_hall_tickets(limit: int = 100):
    """Get hall tickets across all exams"""
    try:
        exams = await infinityfree_client.get_all_exams()
        all_tickets = []
        for ex in exams[:10]:
            tickets = await infinityfree_client.get_hall_tickets_by_exam(ex["id"])
            all_tickets.extend(tickets)
            if len(all_tickets) >= limit:
                break
        return {"success": True, "count": len(all_tickets[:limit]), "data": all_tickets[:limit]}
    except Exception as e:
        return {"success": False, "error": str(e), "data": []}


@app.get("/api/hall_tickets/student/{student_id}", tags=["Hall Tickets"])
async def get_student_hall_tickets(student_id: int):
    """Get hall tickets for a student"""
    try:
        tickets = await infinityfree_client.get_hall_tickets_by_student(student_id)
        return {"success": True, "count": len(tickets), "data": tickets}
    except Exception as e:
        return {"success": False, "error": str(e), "data": []}


# ==================== EXAM SCHEDULE ====================

@app.get("/api/exam_schedule/all", tags=["Schedule"])
async def get_all_schedule(limit: int = 200):
    """Get schedules across all exams"""
    try:
        exams = await infinityfree_client.get_all_exams()
        all_schedule = []
        for ex in exams[:10]:
            schedule = await infinityfree_client.get_exam_schedule(ex["id"])
            all_schedule.extend(schedule)
            if len(all_schedule) >= limit:
                break
        return {"success": True, "count": len(all_schedule[:limit]), "data": all_schedule[:limit]}
    except Exception as e:
        return {"success": False, "error": str(e), "data": []}


@app.get("/api/exam_schedule/{exam_id}", tags=["Schedule"])
async def get_exam_schedule(exam_id: int):
    """Get schedule for a specific exam"""
    try:
        schedule = await infinityfree_client.get_exam_schedule(exam_id)
        return {"success": True, "count": len(schedule), "data": schedule}
    except Exception as e:
        return {"success": False, "error": str(e), "data": []}


# ==================== DOCUMENTS ====================

@app.get("/api/documents/all", tags=["Documents"])
async def get_all_documents(limit: int = 200):
    """Get documents across all students"""
    try:
        students = await infinityfree_client.get_all_students(20)
        all_docs = []
        for s in students:
            docs = await infinityfree_client.get_student_documents(s["id"])
            all_docs.extend(docs)
            if len(all_docs) >= limit:
                break
        return {"success": True, "count": len(all_docs[:limit]), "data": all_docs[:limit]}
    except Exception as e:
        return {"success": False, "error": str(e), "data": []}


@app.get("/api/documents/student/{student_id}", tags=["Documents"])
async def get_student_documents(student_id: int):
    """Get documents for a student"""
    try:
        docs = await infinityfree_client.get_student_documents(student_id)
        return {"success": True, "count": len(docs), "data": docs}
    except Exception as e:
        return {"success": False, "error": str(e), "data": []}


# ==================== TOKENS ====================

@app.get("/api/tokens/validate/{token_no}", tags=["Tokens"])
async def validate_token(token_no: str):
    """Validate an exam token"""
    try:
        token = await infinityfree_client.validate_token(token_no)
        if not token:
            return {"success": False, "valid": False, "data": None}
        return {"success": True, "valid": True, "data": token}
    except Exception as e:
        return {"success": False, "valid": False, "error": str(e), "data": None}


@app.get("/api/tokens/all", tags=["Tokens"])
async def get_all_tokens():
    """Placeholder — tokens are fetched per-token only"""
    return {"success": True, "data": [], "message": "Use /api/tokens/validate/{token_no} to look up a token"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
