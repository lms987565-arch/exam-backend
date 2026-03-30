from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from database import get_db
from models import ExamSession, Flag, Warning, Result
from ws_manager import manager
from pydantic import BaseModel
from typing import Optional
import os, json
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

STAFF_USERNAME = os.getenv("STAFF_USERNAME", "proctor")
STAFF_PASSWORD = os.getenv("STAFF_PASSWORD", "proctor123")


# ── Schemas ──────────────────────────────────────────────────

class StaffLoginData(BaseModel):
    username: str
    password: str

class SendWarningData(BaseModel):
    session_id: int
    message: str
    severity: Optional[str] = "MEDIUM"

class ReportViolationData(BaseModel):
    session_id: int
    flag_type: str
    severity: Optional[str] = "HIGH"
    description: Optional[str] = ""

class TerminateData(BaseModel):
    session_id: int


# ── Auth ─────────────────────────────────────────────────────

@router.post("/login")
def staff_login(data: StaffLoginData):
    if data.username == STAFF_USERNAME and data.password == STAFF_PASSWORD:
        return {
            "success": True,
            "staff_name": "Dr. Sharma",
            "role": "proctor"
        }
    raise HTTPException(status_code=401, detail="Invalid credentials")


# ── Session Management ───────────────────────────────────────

@router.get("/sessions")
def get_active_sessions(db: Session = Depends(get_db)):
    sessions = db.query(ExamSession).filter(
        ExamSession.status == "active"
    ).all()

    result = []
    for s in sessions:
        online = manager.is_student_online(s.student_hash)
        result.append({
            "id": s.id,
            "student_name": s.student_name,
            "student_hash": s.student_hash,
            "start_time": str(s.start_time),
            "status": s.status,
            "flag_count": s.flag_count or 0,
            "snapshot_url": s.snapshot_url,
            "online": online
        })

    return {"success": True, "sessions": result}


@router.get("/session/{session_id}")
def get_session_detail(session_id: int, db: Session = Depends(get_db)):
    session = db.query(ExamSession).filter(ExamSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    flags = db.query(Flag).filter(Flag.session_id == session_id).order_by(Flag.created_at.desc()).all()
    warnings = db.query(Warning).filter(Warning.session_id == session_id).order_by(Warning.sent_at.desc()).all()

    return {
        "success": True,
        "session": {
            "id": session.id,
            "student_name": session.student_name,
            "student_hash": session.student_hash,
            "start_time": str(session.start_time),
            "status": session.status,
            "flag_count": session.flag_count or 0,
            "photo_url": session.photo_url,
            "snapshot_url": session.snapshot_url,
            "online": manager.is_student_online(session.student_hash)
        },
        "flags": [
            {
                "id": f.id,
                "flag_type": f.flag_type,
                "severity": f.severity,
                "description": f.description,
                "created_at": str(f.created_at),
                "resolved": f.resolved
            }
            for f in flags
        ],
        "warnings": [
            {
                "id": w.id,
                "message": w.message,
                "severity": w.severity,
                "sent_at": str(w.sent_at),
                "acknowledged": w.acknowledged
            }
            for w in warnings
        ]
    }


@router.post("/send-warning")
async def send_warning(data: SendWarningData, db: Session = Depends(get_db)):
    session = db.query(ExamSession).filter(ExamSession.id == data.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    warning = Warning(
        session_id=data.session_id,
        message=data.message,
        severity=data.severity
    )
    db.add(warning)
    db.commit()

    # Send warning via WebSocket if student is online
    await manager.send_to_student(session.student_hash, {
        "type": "warning",
        "message": data.message,
        "severity": data.severity
    })

    return {"success": True}


@router.post("/report-violation")
async def report_violation(data: ReportViolationData, db: Session = Depends(get_db)):
    session = db.query(ExamSession).filter(ExamSession.id == data.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    flag = Flag(
        session_id=data.session_id,
        flag_type=data.flag_type,
        severity=data.severity,
        description=data.description
    )
    db.add(flag)
    session.flag_count = (session.flag_count or 0) + 1
    db.commit()

    # Notify all proctors of updated flag count
    await manager.broadcast_to_proctors({
        "type": "flag_updated",
        "student_hash": session.student_hash,
        "flag_count": session.flag_count
    })

    return {"success": True}


@router.post("/terminate")
async def terminate_session(data: TerminateData, db: Session = Depends(get_db)):
    session = db.query(ExamSession).filter(ExamSession.id == data.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.status = "terminated"
    db.commit()

    # Notify student
    await manager.send_to_student(session.student_hash, {
        "type": "terminated",
        "message": "Your exam session has been terminated by the proctor."
    })

    return {"success": True}


@router.get("/results")
def get_results(db: Session = Depends(get_db)):
    results = db.query(Result).order_by(Result.submitted_at.desc()).all()
    return {
        "success": True,
        "results": [
            {
                "id": r.id,
                "student_hash": r.student_hash,
                "total_marks": r.total_marks,
                "obtained_marks": r.obtained_marks,
                "percentage": r.percentage,
                "submitted_at": str(r.submitted_at)
            }
            for r in results
        ]
    }


@router.get("/online-students")
def get_online_students():
    return {
        "success": True,
        "online": manager.get_online_students(),
        "count": len(manager.get_online_students())
    }


# ── WebSocket: Proctor receives all camera feeds ─────────────

@router.websocket("/ws/proctor")
async def proctor_websocket(websocket: WebSocket):
    await manager.connect_proctor(websocket)
    try:
        while True:
            # Proctor can send commands
            data = await websocket.receive_json()
            msg_type = data.get("type")

            if msg_type == "ping":
                await websocket.send_json({"type": "pong"})

            elif msg_type == "send_warning":
                student_hash = data.get("student_hash")
                message = data.get("message", "")
                await manager.send_to_student(student_hash, {
                    "type": "warning",
                    "message": message,
                    "severity": data.get("severity", "MEDIUM")
                })

    except WebSocketDisconnect:
        manager.disconnect_proctor(websocket)
