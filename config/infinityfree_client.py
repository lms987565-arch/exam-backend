# backend/config/infinityfree_client.py
import httpx
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()

class InfinityFreeClient:
    def __init__(self):
        self.base_url = "https://lmsmodern.infinityfree.me/proctored_api.php"
        
    async def _request(self, endpoint: str, params: Dict = None) -> Dict:
        """Make request to InfinityFree API"""
        url = f"{self.base_url}?endpoint={endpoint}"
        
        if params:
            for key, value in params.items():
                if value is not None:
                    url += f"&{key}={value}"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(url)
                print(f"📡 {endpoint} - Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        return data.get('data', [])
                    else:
                        print(f"⚠️ API error for {endpoint}: {data.get('error')}")
                        return []
                else:
                    print(f"❌ HTTP {response.status_code} for {endpoint}")
                    return []
                    
            except Exception as e:
                print(f"❌ Error fetching {endpoint}: {e}")
                return []
    
    # ==================== MAIN ENDPOINTS ====================
    
    async def get_all_students(self, limit: int = 100) -> List[Dict]:
        """Get all students"""
        result = await self._request('students', {'limit': limit})
        return result if isinstance(result, list) else []
    
    async def get_all_exams(self) -> List[Dict]:
        """Get all exams"""
        result = await self._request('exams')
        return result if isinstance(result, list) else []
    
    async def get_all_applications(self, limit: int = 100) -> List[Dict]:
        """Get all applications"""
        result = await self._request('applications', {'limit': limit})
        return result if isinstance(result, list) else []
    
    async def get_dashboard_stats(self) -> Dict:
        """Get dashboard statistics"""
        result = await self._request('dashboard_stats')
        return result if isinstance(result, dict) else {
            'total_students': 0,
            'open_exams': 0,
            'verified_applications': 0
        }
    
    # ==================== EXTRA ENDPOINTS ====================
    
    async def get_hall_tickets_by_exam(self, exam_id: int) -> List[Dict]:
        """Get hall tickets for an exam"""
        result = await self._request('hall_tickets', {'exam_id': exam_id})
        return result if isinstance(result, list) else []
    
    async def get_exam_schedule(self, exam_id: int) -> List[Dict]:
        """Get exam schedule"""
        result = await self._request('exam_schedule', {'exam_id': exam_id})
        return result if isinstance(result, list) else []
    
    async def get_student_documents(self, student_id: int) -> List[Dict]:
        """Get student documents"""
        result = await self._request('documents', {'student_id': student_id})
        return result if isinstance(result, list) else []


# Singleton instance
infinityfree_client = InfinityFreeClient()
