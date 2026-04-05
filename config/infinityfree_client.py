# backend/config/infinityfree_client.py
import httpx
import json
from typing import List, Dict, Optional
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("INFINITYFREE_API_KEY", "render_backend_key_7x9k2m")
BASE_URL = os.getenv("INFINITYFREE_BASE_URL", "https://lmsmodern.infinityfree.me/proctored_api.php")


class InfinityFreeClient:
    def __init__(self):
        self.base_url = BASE_URL
        self.headers = {
            "Content-Type": "application/json",
            "X-API-Key": API_KEY,
        }

    # ==================== CORE REQUEST HELPERS ====================

    async def _get(self, endpoint: str, params: Dict = None) -> any:
        """Async GET request"""
        url = f"{self.base_url}?endpoint={endpoint}"
        if params:
            for key, value in params.items():
                if value is not None:
                    url += f"&{key}={value}"

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(url, headers=self.headers)
                print(f"📡 GET {endpoint} → {response.status_code}")
                return self._parse(response, endpoint)
            except httpx.TimeoutException:
                print(f"⏱️ Timeout on GET {endpoint}")
                return None
            except Exception as e:
                print(f"❌ GET {endpoint} error: {e}")
                return None

    async def _post(self, endpoint: str, data: Dict) -> any:
        """Async POST request"""
        url = f"{self.base_url}?endpoint={endpoint}"
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(url, headers=self.headers, json=data)
                print(f"📡 POST {endpoint} → {response.status_code}")
                return self._parse(response, endpoint)
            except httpx.TimeoutException:
                print(f"⏱️ Timeout on POST {endpoint}")
                return None
            except Exception as e:
                print(f"❌ POST {endpoint} error: {e}")
                return None

    async def _put(self, endpoint: str, data: Dict) -> any:
        """Async PUT request"""
        url = f"{self.base_url}?endpoint={endpoint}"
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.put(url, headers=self.headers, json=data)
                print(f"📡 PUT {endpoint} → {response.status_code}")
                return self._parse(response, endpoint)
            except httpx.TimeoutException:
                print(f"⏱️ Timeout on PUT {endpoint}")
                return None
            except Exception as e:
                print(f"❌ PUT {endpoint} error: {e}")
                return None

    def _parse(self, response: httpx.Response, endpoint: str) -> any:
        """Parse API response and return data or raise"""
        if response.status_code == 401:
            raise PermissionError(f"API key rejected by {endpoint}")
        if response.status_code == 404:
            raise ValueError(f"Unknown endpoint: {endpoint}")
        if response.status_code != 200:
            raise ConnectionError(f"HTTP {response.status_code} from {endpoint}")

        # Guard against empty / non-JSON body (InfinityFree sometimes returns PHP errors)
        text = response.text.strip()
        if not text:
            print(f"⚠️ Empty response from {endpoint}")
            return None

        # Strip any stray HTML/PHP warnings before the JSON
        json_start = text.find('{')
        if json_start == -1:
            json_start = text.find('[')
        if json_start > 0:
            print(f"⚠️ Non-JSON prefix on {endpoint} response, trimming.")
            text = text[json_start:]

        try:
            payload = json.loads(text)
        except json.JSONDecodeError as e:
            print(f"❌ JSON decode error for {endpoint}: {e}\nRaw: {text[:200]}")
            return None

        if payload.get("success"):
            return payload.get("data")
        else:
            err = payload.get("error", "Unknown API error")
            print(f"⚠️ API returned error for {endpoint}: {err}")
            raise RuntimeError(err)

    # ==================== STUDENTS ====================

    async def get_all_students(self, limit: int = 100) -> List[Dict]:
        result = await self._get("students", {"limit": limit})
        return result if isinstance(result, list) else []

    async def get_student_by_id(self, student_id: int) -> Optional[Dict]:
        result = await self._get("students", {"id": student_id})
        return result if isinstance(result, dict) else None

    # ==================== AUTH ====================

    async def student_login(self, email: str, password: str) -> Optional[Dict]:
        result = await self._post("auth", {"email": email, "password": password})
        return result if isinstance(result, dict) else None

    # ==================== EXAMS ====================

    async def get_all_exams(self) -> List[Dict]:
        result = await self._get("exams")
        return result if isinstance(result, list) else []

    async def get_exam_by_id(self, exam_id: int) -> Optional[Dict]:
        result = await self._get("exams", {"id": exam_id})
        return result if isinstance(result, dict) else None

    async def get_exams_by_status(self, status: str) -> List[Dict]:
        result = await self._get("exams", {"status": status})
        return result if isinstance(result, list) else []

    async def get_open_exams(self) -> List[Dict]:
        return await self.get_exams_by_status("open")

    # ==================== APPLICATIONS ====================

    async def get_all_applications(self, limit: int = 100) -> List[Dict]:
        result = await self._get("applications", {"limit": limit})
        return result if isinstance(result, list) else []

    async def get_applications_by_student(self, student_id: int) -> List[Dict]:
        result = await self._get("applications", {"student_id": student_id})
        return result if isinstance(result, list) else []

    async def get_application_by_id(self, application_id: int) -> Optional[Dict]:
        result = await self._get("applications", {"id": application_id})
        return result if isinstance(result, dict) else None

    async def create_application(self, application_data: Dict) -> Optional[Dict]:
        result = await self._post("applications", application_data)
        return result if isinstance(result, dict) else None

    async def update_application_status(
        self, application_id: int, status: str, progress: int = None
    ) -> Optional[Dict]:
        payload = {"id": application_id, "status": status}
        if progress is not None:
            payload["progress_percentage"] = progress
        result = await self._put("applications", payload)
        return result if isinstance(result, dict) else None

    # ==================== HALL TICKETS ====================

    async def get_hall_tickets_by_student(self, student_id: int) -> List[Dict]:
        result = await self._get("hall_tickets", {"student_id": student_id})
        return result if isinstance(result, list) else []

    async def get_hall_tickets_by_exam(self, exam_id: int) -> List[Dict]:
        result = await self._get("hall_tickets", {"exam_id": exam_id})
        return result if isinstance(result, list) else []

    # ==================== EXAM SCHEDULE ====================

    async def get_exam_schedule(self, exam_id: int) -> List[Dict]:
        result = await self._get("exam_schedule", {"exam_id": exam_id})
        return result if isinstance(result, list) else []

    # ==================== SLOT BOOKINGS ====================

    async def get_slot_bookings_by_student(self, student_id: int) -> List[Dict]:
        result = await self._get("slot_bookings", {"student_id": student_id})
        return result if isinstance(result, list) else []

    # ==================== TOKENS ====================

    async def validate_token(self, token_no: str) -> Optional[Dict]:
        result = await self._get("tokens", {"token_no": token_no})
        return result if isinstance(result, dict) else None

    async def mark_token_used(self, token_no: str, ip_address: str = "unknown") -> Optional[Dict]:
        token = await self.validate_token(token_no)
        if not token:
            return None
        result = await self._put("tokens", {
            "id": token["id"],
            "status": "used",
            "used_ip": ip_address,
        })
        return result if isinstance(result, dict) else None

    # ==================== DOCUMENTS ====================

    async def get_student_documents(self, student_id: int) -> List[Dict]:
        result = await self._get("documents", {"student_id": student_id})
        return result if isinstance(result, list) else []

    async def upload_document(self, document_data: Dict) -> Optional[Dict]:
        result = await self._post("documents", document_data)
        return result if isinstance(result, dict) else None

    async def update_document_status(
        self,
        document_id: int,
        status: str,
        remark: str = "",
        verified_by: str = "system",
    ) -> Optional[Dict]:
        result = await self._put("documents", {
            "id": document_id,
            "status": status,
            "remark": remark,
            "verified_by": verified_by,
        })
        return result if isinstance(result, dict) else None

    # ==================== VERIFICATION HISTORY ====================

    async def get_verification_history(self, student_id: int) -> List[Dict]:
        result = await self._get("verification_history", {"student_id": student_id})
        return result if isinstance(result, list) else []

    async def add_verification_record(self, record_data: Dict) -> Optional[Dict]:
        result = await self._post("verification", record_data)
        return result if isinstance(result, dict) else None

    # ==================== DASHBOARD STATS ====================

    async def get_dashboard_stats(self) -> Dict:
        result = await self._get("dashboard_stats")
        return result if isinstance(result, dict) else {
            "total_students": 0,
            "total_exams": 0,
            "total_applications": 0,
            "open_exams": 0,
            "verified_applications": 0,
            "pending_applications": 0,
        }

    async def get_student_dashboard(self, student_id: int) -> Dict:
        applications        = await self.get_applications_by_student(student_id)
        hall_tickets        = await self.get_hall_tickets_by_student(student_id)
        documents           = await self.get_student_documents(student_id)
        verification_history = await self.get_verification_history(student_id)

        return {
            "applications":          applications,
            "hall_tickets":          hall_tickets,
            "documents":             documents,
            "verification_history":  verification_history,
            "stats": {
                "total_applications":    len(applications),
                "verified_applications": len([a for a in applications if a.get("status") == "verified"]),
                "pending_applications":  len([a for a in applications if a.get("status") == "submitted"]),
                "total_documents":       len(documents),
                "verified_documents":    len([d for d in documents if d.get("status") == "verified"]),
            },
        }

    async def get_admin_dashboard(self) -> Dict:
        stats            = await self.get_dashboard_stats()
        all_students     = await self.get_all_students(100)
        all_applications = await self.get_all_applications(100)
        all_exams        = await self.get_all_exams()

        by_status = {"draft": 0, "submitted": 0, "verified": 0, "rejected": 0}
        for app in all_applications:
            s = app.get("status")
            if s in by_status:
                by_status[s] += 1

        return {
            "stats":                  stats,
            "total_students":         len(all_students),
            "total_exams":            len(all_exams),
            "applications_by_status": by_status,
            "recent_students":        all_students[:10],
            "recent_applications":    all_applications[:10],
        }


# Singleton instance
infinityfree_client = InfinityFreeClient()
