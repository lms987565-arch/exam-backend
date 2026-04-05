# backend/config/infinityfree_client.py
import httpx
import json
from typing import List, Dict, Optional
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()

API_KEY = os.getenv("INFINITYFREE_API_KEY", "render_backend_key_7x9k2m")
BASE_URL = os.getenv("INFINITYFREE_BASE_URL", "https://lmsmodern.infinityfree.me/proctored_api.php")


class InfinityFreeClient:
    def __init__(self):
        self.base_url = BASE_URL
        self.api_key = API_KEY

    def _build_url(self, endpoint: str, params: Dict = None) -> str:
        """Build full URL with endpoint + api_key + optional extra params."""
        url = f"{self.base_url}?endpoint={endpoint}&api_key={self.api_key}"
        if params:
            for key, value in params.items():
                if value is not None:
                    url += f"&{key}={value}"
        return url

    async def _make_request_with_curl(self, url: str) -> Optional[Dict]:
        """Use curl_cffi to mimic a real browser (bypasses Cloudflare)"""
        try:
            from curl_cffi import requests as curl_requests
            response = curl_requests.get(
                url,
                impersonate="chrome120",  # Impersonates Chrome browser
                timeout=60
            )
            if response.status_code == 200:
                return self._parse_response(response.text)
            return None
        except ImportError:
            print("curl_cffi not installed, falling back to httpx")
            return None
        except Exception as e:
            print(f"curl_cffi error: {e}")
            return None

    async def _make_request_with_httpx(self, url: str) -> Optional[Dict]:
        """Fallback to httpx with browser headers"""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
        }
        
        async with httpx.AsyncClient(timeout=60.0, verify=False, follow_redirects=True) as client:
            response = await client.get(url, headers=headers)
            return self._parse_response(response.text)

    def _parse_response(self, text: str) -> Optional[Dict]:
        """Parse response and extract JSON"""
        text = text.strip()
        
        # Try to find JSON in the response
        import re
        # Look for JSON pattern
        json_match = re.search(r'(\{.*"success".*[\[{].*[\]\}].*\})', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except:
                pass
        
        # Try direct JSON parse
        json_start = text.find('{')
        arr_start = text.find('[')
        if arr_start != -1 and (json_start == -1 or arr_start < json_start):
            json_start = arr_start
        
        if json_start > 0:
            text = text[json_start:]
        
        try:
            return json.loads(text)
        except:
            return None

    async def _get(self, endpoint: str, params: Dict = None):
        url = self._build_url(endpoint, params)
        print(f"📡 Fetching: {endpoint}")
        
        # Try curl_cffi first (bypasses Cloudflare)
        result = await self._make_request_with_curl(url)
        if result and result.get("success"):
            return result.get("data")
        
        # Fallback to httpx
        result = await self._make_request_with_httpx(url)
        if result and result.get("success"):
            return result.get("data")
        
        print(f"⚠️ Failed to get data for {endpoint}")
        return None if params else []

    async def _post(self, endpoint: str, data: Dict):
        url = self._build_url(endpoint)
        headers = {"Content-Type": "application/json"}
        
        async with httpx.AsyncClient(timeout=60.0, verify=False) as client:
            try:
                response = await client.post(url, json=data, headers=headers)
                result = self._parse_response(response.text)
                return result.get("data") if result and result.get("success") else None
            except Exception as e:
                print(f"❌ POST error: {e}")
                return None

    async def _put(self, endpoint: str, data: Dict):
        url = self._build_url(endpoint)
        headers = {"Content-Type": "application/json"}
        
        async with httpx.AsyncClient(timeout=60.0, verify=False) as client:
            try:
                response = await client.put(url, json=data, headers=headers)
                result = self._parse_response(response.text)
                return result.get("data") if result and result.get("success") else None
            except Exception as e:
                print(f"❌ PUT error: {e}")
                return None

    # ==================== API METHODS ====================
    
    async def get_all_students(self, limit: int = 100) -> List[Dict]:
        result = await self._get("students", {"limit": limit})
        return result if isinstance(result, list) else []

    async def get_student_by_id(self, student_id: int) -> Optional[Dict]:
        result = await self._get("students", {"id": student_id})
        return result if isinstance(result, dict) else None

    async def student_login(self, email: str, password: str) -> Optional[Dict]:
        return await self._post("auth", {"email": email, "password": password})

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

    async def get_all_applications(self, limit: int = 100) -> List[Dict]:
        result = await self._get("applications", {"limit": limit})
        return result if isinstance(result, list) else []

    async def get_applications_by_student(self, student_id: int) -> List[Dict]:
        result = await self._get("applications", {"student_id": student_id})
        return result if isinstance(result, list) else []

    async def get_application_by_id(self, application_id: int) -> Optional[Dict]:
        result = await self._get("applications", {"id": application_id})
        return result if isinstance(result, dict) else None

    async def create_application(self, data: Dict) -> Optional[Dict]:
        return await self._post("applications", data)

    async def update_application_status(self, app_id: int, status: str, progress: int = None) -> Optional[Dict]:
        payload = {"id": app_id, "status": status}
        if progress is not None:
            payload["progress_percentage"] = progress
        return await self._put("applications", payload)

    async def get_hall_tickets_by_student(self, student_id: int) -> List[Dict]:
        result = await self._get("hall_tickets", {"student_id": student_id})
        return result if isinstance(result, list) else []

    async def get_hall_tickets_by_exam(self, exam_id: int) -> List[Dict]:
        result = await self._get("hall_tickets", {"exam_id": exam_id})
        return result if isinstance(result, list) else []

    async def get_exam_schedule(self, exam_id: int) -> List[Dict]:
        result = await self._get("exam_schedule", {"exam_id": exam_id})
        return result if isinstance(result, list) else []

    async def get_slot_bookings_by_student(self, student_id: int) -> List[Dict]:
        result = await self._get("slot_bookings", {"student_id": student_id})
        return result if isinstance(result, list) else []

    async def validate_token(self, token_no: str) -> Optional[Dict]:
        result = await self._get("tokens", {"token_no": token_no})
        return result if isinstance(result, dict) else None

    async def mark_token_used(self, token_no: str, ip_address: str = "unknown") -> Optional[Dict]:
        token = await self.validate_token(token_no)
        if not token:
            return None
        return await self._put("tokens", {"id": token["id"], "status": "used", "used_ip": ip_address})

    async def get_student_documents(self, student_id: int) -> List[Dict]:
        result = await self._get("documents", {"student_id": student_id})
        return result if isinstance(result, list) else []

    async def upload_document(self, data: Dict) -> Optional[Dict]:
        return await self._post("documents", data)

    async def update_document_status(self, doc_id: int, status: str, remark: str = "", verified_by: str = "system") -> Optional[Dict]:
        return await self._put("documents", {"id": doc_id, "status": status, "remark": remark, "verified_by": verified_by})

    async def get_verification_history(self, student_id: int) -> List[Dict]:
        result = await self._get("verification_history", {"student_id": student_id})
        return result if isinstance(result, list) else []

    async def add_verification_record(self, data: Dict) -> Optional[Dict]:
        return await self._post("verification", data)

    async def get_dashboard_stats(self) -> Dict:
        result = await self._get("dashboard_stats")
        return result if isinstance(result, dict) else {
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
