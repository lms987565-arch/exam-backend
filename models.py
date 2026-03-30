from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float
from sqlalchemy.sql import func
from database import Base


class Student(Base):
    __tablename__ = "students"
    id            = Column(Integer, primary_key=True, index=True)
    name          = Column(String(100), nullable=False)
    dob           = Column(String(20), nullable=False)
    enrollment_no = Column(String(50), unique=True, nullable=True)
    student_hash  = Column(String(64), unique=True, index=True)
    created_at    = Column(DateTime, default=func.now())


class ExamSession(Base):
    __tablename__ = "exam_sessions"
    id            = Column(Integer, primary_key=True, index=True)
    student_id    = Column(Integer, nullable=True)
    student_name  = Column(String(100))
    student_hash  = Column(String(64), index=True)
    exam_id       = Column(Integer, nullable=True)
    start_time    = Column(DateTime, default=func.now())
    end_time      = Column(DateTime, nullable=True)
    status        = Column(String(20), default="active")   # active/submitted/terminated
    photo_url     = Column(String(512), nullable=True)
    snapshot_url  = Column(String(512), nullable=True)     # latest camera snapshot
    answers_json  = Column(Text, nullable=True)            # JSON blob of answers
    timer_remaining = Column(Integer, default=3600)
    flag_count    = Column(Integer, default=0)


class Flag(Base):
    __tablename__ = "flags"
    id          = Column(Integer, primary_key=True, index=True)
    session_id  = Column(Integer, index=True)
    flag_type   = Column(String(50))
    severity    = Column(String(20), default="MEDIUM")     # LOW/MEDIUM/HIGH/CRITICAL
    description = Column(Text)
    created_at  = Column(DateTime, default=func.now())
    resolved    = Column(Boolean, default=False)


class Warning(Base):
    __tablename__ = "warnings"
    id           = Column(Integer, primary_key=True, index=True)
    session_id   = Column(Integer, index=True)
    message      = Column(Text)
    severity     = Column(String(20), default="MEDIUM")
    sent_at      = Column(DateTime, default=func.now())
    acknowledged = Column(Boolean, default=False)


class Staff(Base):
    __tablename__ = "staff"
    id         = Column(Integer, primary_key=True, index=True)
    username   = Column(String(50), unique=True)
    password   = Column(String(255))
    name       = Column(String(100))
    role       = Column(String(20), default="proctor")
    created_at = Column(DateTime, default=func.now())


class Result(Base):
    __tablename__ = "results"
    id             = Column(Integer, primary_key=True, index=True)
    session_id     = Column(Integer, unique=True)
    student_hash   = Column(String(64))
    total_marks    = Column(Integer)
    obtained_marks = Column(Integer)
    percentage     = Column(Float)
    submitted_at   = Column(DateTime, default=func.now())
