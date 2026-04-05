# backend/config/infinityfree_api.py
"""
Synchronous wrapper around InfinityFreeClient.
Use InfinityFreeClient (async) directly inside FastAPI routes.
Use InfinityFreeAPI here only in sync contexts (scripts, tests, etc.).
"""
import asyncio
from typing import Optional, List, Dict
from backend.config.infinityfree_client import InfinityFreeClient


def _run(coro):
    """Run an async coroutine from sync code."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Inside an already-running loop (e.g. Jupyter): use nest_asyncio or a thread
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(asyncio.run, coro)
                return future.result()
        return loop.run_until_complete(coro)
    except RuntimeError:
        return asyncio.run(coro)


class InfinityFreeAPI:
    """Synchronous façade – thin wrapper over the async client."""

    def __init__(self):
        self._client = InfinityFreeClient()

    # ==================== STUDENTS ====================

    def get_all_students(self, limit: int = 50) -> List[Dict]:
        return _run(self._client.get_all_students(limit))

    def get_student_by_id(self, student_id: int) -> Optional[Dict]:
        return _run(self._client.get_student_by_id(student_id))

    def get_student_by_email(self, email: str) -> Optional[Dict]:
        students = self.get_all_students(500)
        return next((s for s in students if s.get("email") == email), None)

    def get_student_by_student_id(self, student_id_str: str) -> Optional[Dict]:
        students = self.get_all_students(500)
        return next((s for s in students if s.get("student_id") == student_id_str), None)

    def create_student(self, student_data: Dict) -> Optional[Dict]:
        return _run(self._client._post("students", student_data))

    def student_login(self, email: str, password: str) -> Optional[Dict]:
        return _run(self._client.student_login(email, password))

    # ==================== EXAMS ====================

    def get_all_exams(self) -> List[Dict]:
        return _run(self._client.get_all_exams())

    def get_exam_by_id(self, exam_id: int) -> Optional[Dict]:
        return _run(self._client.get_exam_by_id(exam_id))

    def get_exams_by_status(self, status: str) -> List[Dict]:
        return _run(self._client.get_exams_by_status(status))

    def get_open_exams(self) -> List[Dict]:
        return _run(self._client.get_open_exams())

    def get_exam_by_code(self, exam_code: str) -> Optional[Dict]:
        exams = self.get_all_exams()
        return next((e for e in exams if e.get("exam_code") == exam_code), None)

    # ==================== APPLICATIONS ====================

    def get_applications_by_student(self, student_id: int) -> List[Dict]:
        return _run(self._client.get_applications_by_student(student_id))

    def get_application_by_id(self, application_id: int) -> Optional[Dict]:
        return _run(self._client.get_application_by_id(application_id))

    def create_application(self, application_data: Dict) -> Optional[Dict]:
        return _run(self._client.create_application(application_data))

    def get_all_applications(self, limit: int = 50) -> List[Dict]:
        return _run(self._client.get_all_applications(limit))

    def get_applications_by_status(self, status: str) -> List[Dict]:
        all_apps = self.get_all_applications(500)
        return [a for a in all_apps if a.get("status") == status]

    def update_application_status(self, application_id: int, status: str, progress: int = None) -> Optional[Dict]:
        return _run(self._client.update_application_status(application_id, status, progress))

    # ==================== HALL TICKETS ====================

    def get_hall_tickets_by_student(self, student_id: int) -> List[Dict]:
        return _run(self._client.get_hall_tickets_by_student(student_id))

    def get_hall_tickets_by_exam(self, exam_id: int) -> List[Dict]:
        return _run(self._client.get_hall_tickets_by_exam(exam_id))

    # ==================== EXAM SCHEDULE ====================

    def get_exam_schedule(self, exam_id: int) -> List[Dict]:
        return _run(self._client.get_exam_schedule(exam_id))

    # ==================== SLOT BOOKINGS ====================

    def get_slot_bookings_by_student(self, student_id: int) -> List[Dict]:
        return _run(self._client.get_slot_bookings_by_student(student_id))

    # ==================== TOKENS ====================

    def validate_token(self, token_no: str) -> Optional[Dict]:
        return _run(self._client.validate_token(token_no))

    def mark_token_used(self, token_no: str, ip_address: str = "unknown") -> Optional[Dict]:
        return _run(self._client.mark_token_used(token_no, ip_address))

    # ==================== DOCUMENTS ====================

    def get_student_documents(self, student_id: int) -> List[Dict]:
        return _run(self._client.get_student_documents(student_id))

    def upload_document(self, document_data: Dict) -> Optional[Dict]:
        return _run(self._client.upload_document(document_data))

    def get_document_by_type(self, student_id: int, document_type: str) -> Optional[Dict]:
        docs = self.get_student_documents(student_id)
        return next((d for d in docs if d.get("document_type") == document_type), None)

    def update_document_status(
        self, document_id: int, status: str, remark: str = "", verified_by: str = "system"
    ) -> Optional[Dict]:
        return _run(self._client.update_document_status(document_id, status, remark, verified_by))

    def are_all_documents_uploaded(self, student_id: int) -> bool:
        required = {"aadhaar", "ssc_marksheet", "hsc_marksheet", "photo", "signature"}
        uploaded = {d.get("document_type") for d in self.get_student_documents(student_id)}
        return required.issubset(uploaded)

    # ==================== VERIFICATION HISTORY ====================

    def get_verification_history(self, student_id: int) -> List[Dict]:
        return _run(self._client.get_verification_history(student_id))

    def add_verification_record(self, record_data: Dict) -> Optional[Dict]:
        return _run(self._client.add_verification_record(record_data))

    # ==================== DASHBOARD ====================

    def get_dashboard_stats(self) -> Dict:
        return _run(self._client.get_dashboard_stats())

    async def get_student_dashboard(self, student_id: int) -> Dict:
        return await self._client.get_student_dashboard(student_id)

    async def get_admin_dashboard(self) -> Dict:
        return await self._client.get_admin_dashboard()


# Singleton instance
infinityfree_api = InfinityFreeAPI()
