from fastapi import WebSocket
from typing import Dict, List
import json
import asyncio


class ConnectionManager:
    """
    Manages WebSocket connections for students and proctors.
    Students send camera snapshots → broadcast to all proctors.
    Proctors receive live feeds + can send warnings back to students.
    """

    def __init__(self):
        # student_hash → WebSocket
        self.students: Dict[str, WebSocket] = {}
        # list of proctor WebSockets
        self.proctors: List[WebSocket] = []
        # student metadata: student_hash → {name, session_id}
        self.student_meta: Dict[str, dict] = {}

    # ── Student ──────────────────────────────────────────────
    async def connect_student(self, ws: WebSocket, student_hash: str, meta: dict = {}):
        await ws.accept()
        self.students[student_hash] = ws
        self.student_meta[student_hash] = meta
        # Notify all proctors that student joined
        await self.broadcast_to_proctors({
            "type": "student_joined",
            "student_hash": student_hash,
            "meta": meta
        })

    def disconnect_student(self, student_hash: str):
        self.students.pop(student_hash, None)
        self.student_meta.pop(student_hash, None)

    async def send_to_student(self, student_hash: str, data: dict):
        ws = self.students.get(student_hash)
        if ws:
            try:
                await ws.send_json(data)
            except Exception:
                self.disconnect_student(student_hash)

    # ── Proctor ──────────────────────────────────────────────
    async def connect_proctor(self, ws: WebSocket):
        await ws.accept()
        self.proctors.append(ws)
        # Send current student list to new proctor
        student_list = [
            {"student_hash": h, "meta": m}
            for h, m in self.student_meta.items()
        ]
        try:
            await ws.send_json({
                "type": "student_list",
                "students": student_list
            })
        except Exception:
            pass

    def disconnect_proctor(self, ws: WebSocket):
        if ws in self.proctors:
            self.proctors.remove(ws)

    async def broadcast_to_proctors(self, data: dict):
        dead = []
        for ws in self.proctors:
            try:
                await ws.send_json(data)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect_proctor(ws)

    # ── Utility ──────────────────────────────────────────────
    def get_online_students(self) -> List[str]:
        return list(self.students.keys())

    def is_student_online(self, student_hash: str) -> bool:
        return student_hash in self.students


# Global singleton
manager = ConnectionManager()
