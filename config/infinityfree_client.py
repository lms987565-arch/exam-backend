# backend/config/infinityfree_client.py
import httpx
import json
import os
from typing import Optional, List, Dict, Any
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class InfinityFreeClient:
    """Async HTTP client for Encrypted InfinityFree MySQL database bridge"""
    
    def __init__(self):
        self.base_url = "https://lmsmodern.infinityfree.me/proctored_api.php"
        self.api_key = os.getenv("INFINITYFREE_API_KEY", "render_backend_key_7x9k2m")
        self.timeout = httpx.Timeout(30.0)
        
    async def _request(self, endpoint: str, params: Dict = None, method: str = 'GET', data: Dict = None) -> Dict:
        """Make async request to InfinityFree API with authentication"""
        url = f"{self.base_url}?endpoint={endpoint}"
        
        if method == 'GET' and params:
            for key, value in params.items():
                if value is not None:
                    url += f"&{key}={value}"
        
        headers = {
            'Content-Type': 'application/json',
            'X-API-Key': self.api_key
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(url, headers=headers)
                
                # Check status code
                if response.status_code == 401:
                    print(f"❌ API Key Invalid for endpoint: {endpoint}")
                    return [] if endpoint in ['students', 'exams', 'applications'] else {}
                elif response.status_code == 404:
                    print(f"⚠️ Endpoint not found: {endpoint}")
                    return [] if endpoint in ['students', 'exams', 'applications'] else {}
                elif response.status_code != 200:
                    print(f"⚠️ HTTP {response.status_code} for {endpoint}")
                    return [] if endpoint in ['students', 'exams', 'applications'] else {}
                
                # Try to parse JSON
                try:
                    result = response.json()
                except json.JSONDecodeError as e:
                    print(f"❌ Invalid JSON from {endpoint}: {response.text[:200]}")
                    return [] if endpoint in ['students', 'exams', 'applications'] else {}
                
                # Handle response format
                if isinstance(result, dict) and result.get('success'):
                    return result.get('data', {})
                elif isinstance(result, list):
                    return result
                else:
                    return [] if endpoint in ['students', 'exams', 'applications'] else {}
                    
            except httpx.TimeoutException:
                print(f"⏰ Timeout for {endpoint}")
                return [] if endpoint in ['students', 'exams', 'applications'] else {}
            except Exception as e:
                print(f"❌ Request Error for {endpoint}: {str(e)}")
                return [] if endpoint in ['students', 'exams', 'applications'] else {}
    
    # ==================== STUDENT MANAGEMENT ====================
    
    async def get_all_students(self, limit: int = 100) -> List[Dict]:
        result = await self._request('students', {'limit': limit})
        return result if isinstance(result, list) else []
    
    async def get_all_exams(self) -> List[Dict]:
        result = await self._request('exams')
        return result if isinstance(result, list) else []
    
    async def get_all_applications(self, limit: int = 100) -> List[Dict]:
        result = await self._request('applications', {'limit': limit})
        return result if isinstance(result, list) else []
    
    async def get_hall_tickets_by_exam(self, exam_id: int) -> List[Dict]:
        """Get hall tickets for an exam"""
        result = await self._request('hall_tickets', {'exam_id': exam_id})
        return result if isinstance(result, list) else []
    
    async def get_exam_schedule(self, exam_id: int) -> List[Dict]:
        result = await self._request('exam_schedule', {'exam_id': exam_id})
        return result if isinstance(result, list) else []
    
    async def get_student_documents(self, student_id: int) -> List[Dict]:
        result = await self._request('documents', {'student_id': student_id})
        return result if isinstance(result, list) else []
    
    async def get_dashboard_stats(self) -> Dict:
        result = await self._request('dashboard_stats')
        return result if isinstance(result, dict) else {'total_students': 0, 'open_exams': 0, 'verified_applications': 0}


# Singleton instance
infinityfree_client = InfinityFreeClient()
