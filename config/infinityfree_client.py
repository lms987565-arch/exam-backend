# backend/config/infinityfree_client.py
import httpx
import asyncio
import os
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()

class InfinityFreeClient:
    def __init__(self):
        self.base_url = "https://lmsmodern.infinityfree.me/proctored_api.php"
        self.api_key = os.getenv("INFINITYFREE_API_KEY", "render_backend_key_7x9k2m")
        
    async def _request(self, endpoint: str, params: Dict = None, max_retries: int = 3) -> Dict:
        """Make request with retries"""
        url = f"{self.base_url}?endpoint={endpoint}"
        
        if params:
            for key, value in params.items():
                if value is not None:
                    url += f"&{key}={value}"
        
        headers = {
            'X-API-Key': self.api_key,
            'User-Agent': 'Render-Backend/1.0'
        }
        
        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient(timeout=30.0, verify=True) as client:
                    response = await client.get(url, headers=headers)
                    
                    print(f"Attempt {attempt + 1}: {endpoint} - Status: {response.status_code}")
                    
                    if response.status_code == 200:
                        try:
                            data = response.json()
                            if data.get('success'):
                                return data.get('data', [])
                            else:
                                print(f"API returned error: {data.get('error')}")
                                return []
                        except Exception as e:
                            print(f"JSON parse error: {e}")
                            return []
                    elif response.status_code == 401:
                        print(f"❌ API Key invalid for {endpoint}")
                        return []
                    else:
                        print(f"⚠️ HTTP {response.status_code} for {endpoint}")
                        
            except httpx.TimeoutException:
                print(f"⏰ Timeout on attempt {attempt + 1} for {endpoint}")
            except httpx.ConnectError as e:
                print(f"🔌 Connection error on attempt {attempt + 1}: {e}")
            except Exception as e:
                print(f"❌ Error on attempt {attempt + 1}: {e}")
            
            if attempt < max_retries - 1:
                await asyncio.sleep(1)  # Wait 1 second before retry
        
        return []
    
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
        return result if isinstance(result, dict) else {
            'total_students': 0,
            'open_exams': 0,
            'verified_applications': 0
        }

# Singleton
infinityfree_client = InfinityFreeClient()
