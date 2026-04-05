# backend/config/infinityfree_client.py
import httpx
import json
from typing import List, Dict, Optional
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY  = os.getenv("INFINITYFREE_API_KEY", "render_backend_key_7x9k2m")
BASE_URL = os.getenv("INFINITYFREE_BASE_URL", "https://lmsmodern.infinityfree.me/proctored_api.php")


class InfinityFreeClient:
    def __init__(self):
        self.base_url = BASE_URL
        self.api_key  = API_KEY
        
    def _build_url(self, endpoint: str, params: Dict = None) -> str:
        """Build full URL with endpoint + api_key + optional extra params."""
        url = f"{self.base_url}?endpoint={endpoint}&api_key={self.api_key}"
        if params:
            for key, value in params.items():
                if value is not None:
                    url += f"&{key}={value}"
        return url
    
    def _get_headers(self) -> Dict:
        """Return browser-like headers to avoid blocking"""
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site"
        }

    # ==================== CORE REQUEST HELPERS ====================

    async def _get(self, endpoint: str, params: Dict = None):
        url = self._build_url(endpoint, params)
        headers = self._get_headers()
        
        print(f"📡 GET {endpoint} → {url[:100]}...")
        
        async with httpx.AsyncClient(timeout=60.0, verify=False, follow_redirects=True) as client:
            try:
                response = await client.get(url, headers=headers)
                print(f"📡 Response Status: {response.status_code}")
                print(f"📡 Response Type: {response.headers.get('content-type', 'unknown')}")
                
                # Check if we got HTML instead of JSON (blocked)
                if response.headers.get('content-type', '').startswith('text/html'):
                    print(f"⚠️ Received HTML instead of JSON - InfinityFree is blocking this request")
                    print(f"   Response preview: {response.text[:200]}")
                    # Try to extract any JSON if it's embedded
                    return await self._parse_html_response(response, endpoint)
                
                return await self._parse_json_response(response, endpoint)
                
            except httpx.TimeoutException:
                print(f"⏱️ Timeout on GET {endpoint}")
                return None
            except Exception as e:
                print(f"❌ GET {endpoint} error: {e}")
                return None

    async def _post(self, endpoint: str, data: Dict):
        url = self._build_url(endpoint)
        headers = self._get_headers()
        headers["Content-Type"] = "application/json"
        
        async with httpx.AsyncClient(timeout=60.0, verify=False, follow_redirects=True) as client:
            try:
                response = await client.post(url, json=data, headers=headers)
                print(f"📡 POST {endpoint} → {response.status_code}")
                return await self._parse_json_response(response, endpoint)
            except httpx.TimeoutException:
                print(f"⏱️ Timeout on POST {endpoint}")
                return None
            except Exception as e:
                print(f"❌ POST {endpoint} error: {e}")
                return None

    async def _put(self, endpoint: str, data: Dict):
        url = self._build_url(endpoint)
        headers = self._get_headers()
        headers["Content-Type"] = "application/json"
        
        async with httpx.AsyncClient(timeout=60.0, verify=False, follow_redirects=True) as client:
            try:
                response = await client.put(url, json=data, headers=headers)
                print(f"📡 PUT {endpoint} → {response.status_code}")
                return await self._parse_json_response(response, endpoint)
            except httpx.TimeoutException:
                print(f"⏱️ Timeout on PUT {endpoint}")
                return None
            except Exception as e:
                print(f"❌ PUT {endpoint} error: {e}")
                return None

    async def _parse_html_response(self, response: httpx.Response, endpoint: str):
        """Try to extract JSON from HTML response (InfinityFree anti-bot page)"""
        text = response.text
        
        # Look for JSON pattern in the HTML
        import re
        json_pattern = r'(\{[^{]*"success"[^}]*\})'
        matches = re.findall(json_pattern, text)
        
        for match in matches:
            try:
                payload = json.loads(match)
                if payload.get("success"):
                    print(f"✅ Extracted JSON from HTML response for {endpoint}")
                    return payload.get("data")
            except:
                continue
        
        # If no JSON found, raise error
        raise ConnectionError(f"InfinityFree is blocking requests from Render. Response: {text[:300]}")

    async def _parse_json_response(self, response: httpx.Response, endpoint: str):
        """Parse normal JSON response"""
        if response.status_code == 401:
            raise PermissionError(f"API key rejected by {endpoint}. Make sure API key is correct.")
        if response.status_code == 404:
            raise ValueError(f"Unknown endpoint: {endpoint}")
        if response.status_code != 200:
            raise ConnectionError(f"HTTP {response.status_code} from {endpoint}")

        text = response.text.strip()
        if not text:
            print(f"⚠️ Empty response from {endpoint}")
            return None

        # Clean any PHP warnings/notices before JSON
        json_start = text.find('{')
        arr_start = text.find('[')
        if arr_start != -1 and (json_start == -1 or arr_start < json_start):
            json_start = arr_start
        if json_start > 0:
            print(f"⚠️ Trimming {json_start} non-JSON bytes from {endpoint} response")
            text = text[json_start:]

        try:
            payload = json.loads(text)
        except json.JSONDecodeError as e:
            print(f"❌ JSON decode error for {endpoint}: {e}")
            print(f"Raw response: {text[:500]}")
            return None

        if payload.get("success"):
            return payload.get("data")

        err = payload.get("error", "Unknown API error")
        hint = payload.get("hint", "")
        print(f"⚠️ API error for {endpoint}: {err}")
        if hint:
            print(f"   Hint: {hint}")
        raise RuntimeError(f"{err} {hint}".strip())

    # ==================== STUDENTS ====================

    async def get_all_students(self, limit: int = 100) -> List[Dict]:
        r = await self._get("students", {"limit": limit})
        return r if isinstance(r, list) else []

    async def get_student_by_id(self, student_id: int) -> Optional[Dict]:
        r = await self._get("students", {"id": student_id})
        return r if isinstance(r, dict) else None

    # ==================== AUTH ====================

    async def student_login(self, email: str, password: str) -> Optional[Dict]:
        r = await self._post("auth", {"email": email, "password": password})
        return r if isinstance(r, dict) else None

    # ==================== EXAMS ====================

    async def get_all_exams(self) -> List[Dict]:
        r = await self._get("exams")
        return r if isinstance(r, list) else []

    async def get_exam_by_id(self, exam_id: int) -> Optional[Dict]:
        r = await self._get("exams", {"id": exam_id})
        return r if isinstance(r, dict) else None

    async def get_exams_by_status(self, status: str) -> List[Dict]:
        r = await self._get("exams", {"status": status})
        return r if isinstance(r, list) else []

    async def get_open_exams(self) -> List[Dict]:
        return await self.get_exams_by_status("open")

    # ==================== APPLICATIONS ====================

    async def get_all_applications(self, limit: int = 100) -> List[Dict]:
        r = await self._get("applications", {"limit": limit})
        return r if isinstance(r, list) else []

    async def get_applications_by_student(self, student_id: int) -> List[Dict]:
        r = await self._get("applications", {"student_id": student_id})
        return r if isinstance(r, list) else []

    async def get_application_by_id(self, application_id: int) -> Optional[Dict]:
        r = await self._get("applications", {"id": application_id})
        return r if isinstance(r, dict) else None

    async def create_application(self, data: Dict) -> Optional[Dict]:
        r = await self._post("applications", data)
        return r if isinstance(r, dict) else None

    async def update_application_status(self, app_id: int, status: str, progress: int = None) -> Optional[Dict]:
        payload = {"id": app_id, "status": status}
        if progress is not None:
            payload["progress_percentage"] = progress
        r = await self._put("applications", payload)
        return r if isinstance(r, dict) else None

    # ==================== HALL TICKETS ====================

    async def get_hall_tickets_by_student(self, student_id: int) -> List[Dict]:
        r = await self._get("hall_tickets", {"student_id": student_id})
        return r if isinstance(r, list) else []

    async def get_hall_tickets_by_exam(self, exam_id: int) -> List[Dict]:
        r = await self._get("hall_tickets", {"exam_id": exam_id})
        return r if isinstance(r, list) else []

    # ==================== EXAM SCHEDULE ====================

    async def get_exam_schedule(self, exam_id: int) -> List[Dict]:
        r = await self._get("exam_schedule", {"exam_id": exam_id})
        return r if isinstance(r, list) else []

    # ==================== SLOT BOOKINGS ====================

    async def get_slot_bookings_by_student(self, student_id: int) -> List[Dict]:
        r = await self._get("slot_bookings", {"student_id": student_id})
        return r if isinstance(r, list) else []

    # ==================== TOKENS ====================

    async def validate_token(self, token_no: str) -> Optional[Dict]:
        r = await self._get("tokens", {"token_no": token_no})
        return r if isinstance(r, dict) else None

    async def mark_token_used(self, token_no: str, ip_address: str = "unknown") -> Optional[Dict]:
        token = await self.validate_token(token_no)
        if not token:
            return None
        r = await self._put("tokens", {"id": token["id"], "status": "used", "used_ip": ip_address})
        return r if isinstance(r, dict) else None

    # ==================== DOCUMENTS ====================

    async def get_student_documents(self, student_id: int) -> List[Dict]:
        r = await self._get("documents", {"student_id": student_id})
        return r if isinstance(r, list) else []

    async def upload_document(self, data: Dict) -> Optional[Dict]:
        r = await self._post("documents", data)
        return r if isinstance(r, dict) else None

    async def update_document_status(self, doc_id: int, status: str,
                                     remark: str = "", verified_by: str = "system") -> Optional[Dict]:
        r = await self._put("documents", {"id": doc_id, "status": status,
                                          "remark": remark, "verified_by": verified_by})
        return r if isinstance(r, dict) else None

    # ==================== VERIFICATION HISTORY ====================

    async def get_verification_history(self, student_id: int) -> List[Dict]:
        r = await self._get("verification_history", {"student_id": student_id})
        return r if isinstance(r, list) else []

    async def add_verification_record(self, data: Dict) -> Optional[Dict]:
        r = await self._post("verification", data)
        return r if isinstance(r, dict) else None

    # ==================== DASHBOARD STATS ====================

    async def get_dashboard_stats(self) -> Dict:
        r = await self._get("dashboard_stats")
        return r if isinstance(r, dict) else {
            "total_students": 0, "total_exams": 0, "total_applications": 0,
            "open_exams": 0, "verified_applications": 0, "pending_applications": 0,
        }

    async def get_student_dashboard(self, student_id: int) -> Dict:
        apps = await self.get_applications_by_student(student_id)
        tickets = await self.get_hall_tickets_by_student(student_id)
        docs = await self.get_student_documents(student_id)
        history = await self.get_verification_history(student_id)
        return {
            "applications": apps,
            "hall_tickets": tickets,
            "documents": docs,
            "verification_history": history,
            "stats": {
                "total_applications": len(apps),
                "verified_applications": len([a for a in apps if a.get("status") == "verified"]),
                "pending_applications": len([a for a in apps if a.get("status") == "submitted"]),
                "total_documents": len(docs),
                "verified_documents": len([d for d in docs if d.get("status") == "verified"]),
            },
        }

    async def get_admin_dashboard(self) -> Dict:
        stats = await self.get_dashboard_stats()
        students = await self.get_all_students(100)
        apps = await self.get_all_applications(100)
        exams = await self.get_all_exams()
        by_status = {"draft": 0, "submitted": 0, "verified": 0, "rejected": 0}
        for a in apps:
            s = a.get("status")
            if s in by_status:
                by_status[s] += 1
        return {
            "stats": stats,
            "total_students": len(students),
            "total_exams": len(exams),
            "applications_by_status": by_status,
            "recent_students": students[:10],
            "recent_applications": apps[:10],
        }


# Singleton
infinityfree_client = InfinityFreeClient()
