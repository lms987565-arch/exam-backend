from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from database import engine
import models
import os
from dotenv import load_dotenv
from routes import exam, staff

# ✅ NEW IMPORT
from routes.dashboard import router as dashboard_router

# ✅ IMPORT CLIENT (singleton instance)
from config.infinityfree_client import infinityfree_client

load_dotenv()

# Create all DB tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Modern College Exam Portal API",
    description="Online proctored examination system",
    version="2.0.0"
)

# CORS — allow frontend (Vercel) and localhost
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        FRONTEND_URL,
        "http://localhost:3000",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:8080",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(exam.router,   prefix="/api/exam",  tags=["Exam"])
app.include_router(staff.router,  prefix="/api/staff", tags=["Staff"])

# ✅ DASHBOARD ROUTER
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


# ==================== DASHBOARD APIs ====================

@app.get("/api/students")
async def get_all_students(limit: int = 100):
    try:
        students = await infinityfree_client.get_all_students(limit)
        return {"success": True, "data": students}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/exams")
async def get_all_exams():
    try:
        exams = await infinityfree_client.get_all_exams()
        return {"success": True, "data": exams}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/applications")
async def get_all_applications(limit: int = 100):
    try:
        applications = await infinityfree_client.get_all_applications(limit)
        return {"success": True, "data": applications}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/hall_tickets/all")
async def get_all_hall_tickets(limit: int = 100):
    try:
        exams = await infinityfree_client.get_all_exams()
        all_tickets = []
        for exam in exams[:10]:
            tickets = await infinityfree_client.get_hall_tickets_by_exam(exam['id'])
            all_tickets.extend(tickets)
        return {"success": True, "data": all_tickets[:limit]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/exam_schedule/all")
async def get_all_schedule(limit: int = 200):
    try:
        exams = await infinityfree_client.get_all_exams()
        all_schedule = []
        for exam in exams:
            schedule = await infinityfree_client.get_exam_schedule(exam['id'])
            all_schedule.extend(schedule)
        return {"success": True, "data": all_schedule[:limit]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/documents/all")
async def get_all_documents(limit: int = 200):
    try:
        students = await infinityfree_client.get_all_students(50)
        all_docs = []
        for student in students:
            docs = await infinityfree_client.get_student_documents(student['id'])
            all_docs.extend(docs)
        return {"success": True, "data": all_docs[:limit]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tokens/all")
async def get_all_tokens(limit: int = 100):
    try:
        exams = await infinityfree_client.get_all_exams()
        all_tokens = []
        return {"success": True, "data": all_tokens}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ✅ ✅ ✅ FIXED MISSING ENDPOINT (IMPORTANT)

@app.get("/api/dashboard/stats")
async def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        stats = await infinityfree_client.get_dashboard_stats()
        return {"success": True, "data": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
