from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from database import engine
import models
import os
from dotenv import load_dotenv
from routes import exam, staff

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
        "*"   # Remove this in production, replace with exact Vercel URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(exam.router,   prefix="/api/exam",  tags=["Exam"])
app.include_router(staff.router,  prefix="/api/staff", tags=["Staff"])


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
