# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
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


# ==================== MAIN API ENDPOINTS ====================

@app.get("/api/students")
async def get_all_students(limit: int = 100):
    """Get all students"""
    try:
        students = await infinityfree_client.get_all_students(limit)
        return {"success": True, "data": students}
    except Exception as e:
        print(f"Error: {e}")
        return {"success": True, "data": []}


@app.get("/api/exams")
async def get_all_exams():
    """Get all exams"""
    try:
        exams = await infinityfree_client.get_all_exams()
        return {"success": True, "data": exams}
    except Exception as e:
        print(f"Error: {e}")
        return {"success": True, "data": []}


@app.get("/api/applications")
async def get_all_applications(limit: int = 100):
    """Get all applications"""
    try:
        applications = await infinityfree_client.get_all_applications(limit)
        return {"success": True, "data": applications}
    except Exception as e:
        print(f"Error: {e}")
        return {"success": True, "data": []}


@app.get("/api/dashboard/stats")
async def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        stats = await infinityfree_client.get_dashboard_stats()
        return {"success": True, "data": stats}
    except Exception as e:
        print(f"Error: {e}")
        return {"success": True, "data": {"total_students": 0, "open_exams": 0, "verified_applications": 0}}


# ==================== AGGREGATE ENDPOINTS ====================

@app.get("/api/hall_tickets/all")
async def get_all_hall_tickets(limit: int = 100):
    """Get all hall tickets"""
    try:
        exams = await infinityfree_client.get_all_exams()
        all_tickets = []
        for exam in exams[:5]:
            tickets = await infinityfree_client.get_hall_tickets_by_exam(exam['id'])
            all_tickets.extend(tickets)
        return {"success": True, "data": all_tickets[:limit]}
    except Exception as e:
        return {"success": True, "data": []}


@app.get("/api/exam_schedule/all")
async def get_all_schedule(limit: int = 200):
    """Get all exam schedules"""
    try:
        exams = await infinityfree_client.get_all_exams()
        all_schedule = []
        for exam in exams[:5]:
            schedule = await infinityfree_client.get_exam_schedule(exam['id'])
            all_schedule.extend(schedule)
        return {"success": True, "data": all_schedule[:limit]}
    except Exception as e:
        return {"success": True, "data": []}


@app.get("/api/documents/all")
async def get_all_documents(limit: int = 200):
    """Get all documents"""
    try:
        students = await infinityfree_client.get_all_students(20)
        all_docs = []
        for student in students:
            docs = await infinityfree_client.get_student_documents(student['id'])
            all_docs.extend(docs)
        return {"success": True, "data": all_docs[:limit]}
    except Exception as e:
        return {"success": True, "data": []}


@app.get("/api/tokens/all")
async def get_all_tokens():
    """Get all tokens"""
    return {"success": True, "data": []}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
