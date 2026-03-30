from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from database import get_db
from models import ExamSession, Flag, Warning, Result
from exam_data import EXAM_DATA
from ws_manager import manager
from pydantic import BaseModel
from typing import Optional, List, Any
import hashlib, os, json, cloudinary, cloudinary.uploader
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

EXAM_TOKEN   = os.getenv("EXAM_TOKEN", "MCT-XXJFB-1W6Y7")

# Cloudinary config (optional — works without it, snapshots stored in memory)
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD", ""),
    api_key=os.getenv("CLOUDINARY_KEY", ""),
    api_secret=os.getenv("CLOUDINARY_SECRET", "")
)


# ── Pydantic schemas ─────────────────────────────────────────

class LoginData(BaseModel):
    name: str
    dob: str
    token: str

class PhotoData(BaseModel):
    photo: str          # base64 data URL
    student_hash: str

class DraftData(BaseModel):
    student_hash: str
    answers: List[Any]
    flagged: List[bool]
    current_q: int
    timer: int
    notes: Optional[str] = ""

class SubmitData(BaseModel):
    student_hash: str
    answers: List[Any]
    flagged: List[bool]
    timer: int


# ── Helper ───────────────────────────────────────────────────

def make_hash(name: str, dob: str, token: str) -> str:
    return hashlib.md5(f"{name.strip().lower()}{dob}{token}".encode()).hexdigest()


def calculate_score(answers: list) -> dict:
    total = 0
    obtained = 0
    all_questions = []
    for sec in EXAM_DATA["sections"]:
        all_questions.extend(sec["questions"])

    for i, q in enumerate(all_questions):
        total += q["marks"]
        a = answers[i] if i < len(answers) else None
        if a is None:
            continue
        if q["type"] == "MCQ" and a == q["correct"]:
            obtained += q["marks"]
        elif q["type"] == "FILL":
            if str(a).strip().lower() == q["correct"].strip().lower():
                obtained += q["marks"]

    return {
        "total_marks": total,
        "obtained_marks": obtained,
        "percentage": round(obtained / total * 100, 2) if total else 0
    }


# ── Routes ───────────────────────────────────────────────────

@router.post("/login")
def login(data: LoginData, db: Session = Depends(get_db)):
    if data.token != EXAM_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid exam token")
    if not data.name.strip():
        raise HTTPException(status_code=400, detail="Name is required")
    if not data.dob.strip():
        raise HTTPException(status_code=400, detail="Date of birth is required")

    student_hash = make_hash(data.name, data.dob, data.token)

    # Get or create session
    session = db.query(ExamSession).filter(
        ExamSession.student_hash == student_hash,
        ExamSession.status == "active"
    ).first()

    if not session:
        session = ExamSession(
            student_name=data.name.strip(),
            student_hash=student_hash,
            status="active",
            timer_remaining=EXAM_DATA["total_time"]
        )
        db.add(session)
        db.commit()
        db.refresh(session)

    return {
        "success": True,
        "student_hash": student_hash,
        "session_id": session.id,
        "student_name": data.name.strip()
    }


@router.post("/save-photo")
def save_photo(data: PhotoData, db: Session = Depends(get_db)):
    session = db.query(ExamSession).filter(
        ExamSession.student_hash == data.student_hash
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    photo_url = None

    # Try Cloudinary upload
    if os.getenv("CLOUDINARY_CLOUD"):
        try:
            result = cloudinary.uploader.upload(
                data.photo,
                public_id=f"exam_photos/{data.student_hash}",
                overwrite=True,
                format="jpg"
            )
            photo_url = result["secure_url"]
        except Exception as e:
            print(f"Cloudinary error: {e}")

    # Fallback: store base64 directly (not recommended for prod)
    if not photo_url:
        photo_url = data.photo[:100] + "..."  # truncate for DB

    session.photo_url = photo_url
    db.commit()

    return {"success": True, "photo_url": photo_url}


@router.get("/questions")
def get_questions():
    return {"success": True, "data": EXAM_DATA}


@router.post("/save-draft")
def save_draft(data: DraftData, db: Session = Depends(get_db)):
    session = db.query(ExamSession).filter(
        ExamSession.student_hash == data.student_hash,
        ExamSession.status == "active"
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.answers_json = json.dumps({
        "answers": data.answers,
        "flagged": data.flagged,
        "current_q": data.current_q,
        "timer": data.timer,
        "notes": data.notes
    })
    session.timer_remaining = data.timer
    db.commit()

    return {"success": True}


@router.post("/load-draft")
def load_draft(payload: dict, db: Session = Depends(get_db)):
    student_hash = payload.get("student_hash")
    session = db.query(ExamSession).filter(
        ExamSession.student_hash == student_hash,
        ExamSession.status == "active"
    ).first()

    if not session or not session.answers_json:
        return {"success": False, "message": "No draft found"}

    draft = json.loads(session.answers_json)
    return {"success": True, "draft": draft}


@router.post("/submit")
def submit_exam(data: SubmitData, db: Session = Depends(get_db)):
    session = db.query(ExamSession).filter(
        ExamSession.student_hash == data.student_hash,
        ExamSession.status == "active"
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    score = calculate_score(data.answers)

    session.status = "submitted"
    session.answers_json = json.dumps({
        "answers": data.answers,
        "flagged": data.flagged,
        "timer": data.timer
    })
    db.commit()

    # Save result
    result = Result(
        session_id=session.id,
        student_hash=data.student_hash,
        total_marks=score["total_marks"],
        obtained_marks=score["obtained_marks"],
        percentage=score["percentage"]
    )
    db.add(result)
    db.commit()

    return {"success": True, "score": score}


@router.get("/session/{student_hash}/warnings")
def get_warnings(student_hash: str, db: Session = Depends(get_db)):
    """Student polls this to check for new warnings from proctor."""
    session = db.query(ExamSession).filter(
        ExamSession.student_hash == student_hash
    ).first()
    if not session:
        return {"warnings": []}

    warnings = db.query(Warning).filter(
        Warning.session_id == session.id,
        Warning.acknowledged == False
    ).all()

    # Mark as acknowledged
    for w in warnings:
        w.acknowledged = True
    db.commit()

    return {
        "warnings": [
            {"message": w.message, "severity": w.severity}
            for w in warnings
        ]
    }


# ── WebSocket: Student camera feed ───────────────────────────

@router.websocket("/ws/student/{student_hash}")
async def student_websocket(
    websocket: WebSocket,
    student_hash: str,
    db: Session = Depends(get_db)
):
    session = db.query(ExamSession).filter(
        ExamSession.student_hash == student_hash,
        ExamSession.status == "active"
    ).first()

    if not session:
        await websocket.close(code=4001)
        return

    meta = {
        "student_name": session.student_name,
        "session_id": session.id,
        "enrollment_no": "",
        "flag_count": session.flag_count
    }

    await manager.connect_student(websocket, student_hash, meta)

    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type")

            if msg_type == "snapshot":
                # Store latest snapshot URL in session
                snap = data.get("snapshot", "")
                snap_url = snap

                # Try upload to Cloudinary
                if os.getenv("CLOUDINARY_CLOUD") and snap.startswith("data:"):
                    try:
                        result = cloudinary.uploader.upload(
                            snap,
                            public_id=f"snapshots/{student_hash}",
                            overwrite=True,
                            format="jpg",
                            quality=60,
                            width=320,
                            height=240,
                            crop="fill"
                        )
                        snap_url = result["secure_url"]
                        session.snapshot_url = snap_url
                        db.commit()
                    except Exception as e:
                        print(f"Cloudinary snapshot error: {e}")

                # Forward to all proctors
                await manager.broadcast_to_proctors({
                    "type": "snapshot",
                    "student_hash": student_hash,
                    "snapshot": snap,          # base64 for instant display
                    "snapshot_url": snap_url,
                    "meta": meta
                })

            elif msg_type == "ping":
                await websocket.send_json({"type": "pong"})

            elif msg_type == "flag":
                # Student self-reports a proctoring event (tab switch etc.)
                flag_type = data.get("flag_type", "UNKNOWN")
                flag = Flag(
                    session_id=session.id,
                    flag_type=flag_type,
                    severity=data.get("severity", "MEDIUM"),
                    description=data.get("description", "")
                )
                db.add(flag)
                session.flag_count = (session.flag_count or 0) + 1
                db.commit()

                await manager.broadcast_to_proctors({
                    "type": "violation",
                    "student_hash": student_hash,
                    "flag_type": flag_type,
                    "severity": data.get("severity", "MEDIUM"),
                    "description": data.get("description", ""),
                    "meta": meta,
                    "flag_count": session.flag_count
                })

    except WebSocketDisconnect:
        manager.disconnect_student(student_hash)
        await manager.broadcast_to_proctors({
            "type": "student_disconnected",
            "student_hash": student_hash
        })
