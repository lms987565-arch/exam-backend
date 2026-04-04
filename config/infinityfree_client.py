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
        # IMPORTANT: Use the exact API key from your proctored_api.php
        self.api_key = os.getenv("INFINITYFREE_API_KEY", "render_backend_key_7x9k2m")
        self.timeout = httpx.Timeout(30.0)
        
    async def _request(self, endpoint: str, params: Dict = None, method: str = 'GET', data: Dict = None) -> Dict:
        """Make async request to InfinityFree API with authentication"""
        url = f"{self.base_url}?endpoint={endpoint}"
        
        # Add query parameters for GET requests
        if method == 'GET' and params:
            for key, value in params.items():
                if value is not None:
                    url += f"&{key}={value}"
        
        headers = {
            'Content-Type': 'application/json',
            'X-API-Key': self.api_key  # Required for authentication
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                if method == 'GET':
                    response = await client.get(url, headers=headers)
                elif method == 'POST':
                    response = await client.post(url, headers=headers, json=data)
                elif method == 'PUT':
                    response = await client.put(url, headers=headers, json=data)
                elif method == 'DELETE':
                    response = await client.delete(url, headers=headers)
                else:
                    raise ValueError(f"Unsupported method: {method}")
                
                # Check for HTTP errors
                response.raise_for_status()
                result = response.json()
                
                # Handle the response format from encrypted API
                if result.get('success'):
                    return result.get('data', {})
                else:
                    # Return appropriate empty type based on endpoint
                    if endpoint in ['students', 'exams', 'applications', 'hall_tickets', 
                                   'exam_schedule', 'documents', 'verification_history']:
                        return []
                    return {}
                    
            except httpx.HTTPStatusError as e:
                print(f"HTTP Error {e.response.status_code}: {e}")
                if e.response.status_code == 401:
                    print("❌ Invalid API Key - Check INFINITYFREE_API_KEY")
                elif e.response.status_code == 429:
                    print("⚠️ Rate limit exceeded - Try again later")
                return [] if endpoint in ['students', 'exams', 'applications'] else {}
            except Exception as e:
                print(f"Request Error: {e}")
                return [] if endpoint in ['students', 'exams', 'applications'] else {}
    
    # ==================== STUDENT MANAGEMENT ====================
    
    async def get_all_students(self, limit: int = 100) -> List[Dict]:
        """Get all students"""
        result = await self._request('students', {'limit': limit})
        return result if isinstance(result, list) else []
    
    async def get_student_by_id(self, student_id: int) -> Optional[Dict]:
        """Get student by ID"""
        result = await self._request('students', {'id': student_id})
        return result if result and isinstance(result, dict) else None
    
    async def get_student_by_email(self, email: str) -> Optional[Dict]:
        """Get student by email"""
        students = await self.get_all_students(500)
        for student in students:
            if student.get('email') == email:
                return student
        return None
    
    async def create_student(self, student_data: Dict) -> Dict:
        """Create new student"""
        return await self._request('students', method='POST', data=student_data)
    
    async def student_login(self, email: str, password: str) -> Dict:
        """Student login"""
        return await self._request('auth', method='POST', data={'email': email, 'password': password})
    
    # ==================== EXAM MANAGEMENT ====================
    
    async def get_all_exams(self) -> List[Dict]:
        """Get all exams"""
        result = await self._request('exams')
        return result if isinstance(result, list) else []
    
    async def get_exam_by_id(self, exam_id: int) -> Optional[Dict]:
        """Get exam by ID"""
        result = await self._request('exams', {'id': exam_id})
        return result if result and isinstance(result, dict) else None
    
    async def get_exams_by_status(self, status: str) -> List[Dict]:
        """Get exams by registration status"""
        result = await self._request('exams', {'status': status})
        return result if isinstance(result, list) else []
    
    async def get_open_exams(self) -> List[Dict]:
        """Get open exams for registration"""
        return await self.get_exams_by_status('open')
    
    # ==================== APPLICATION MANAGEMENT ====================
    
    async def get_applications_by_student(self, student_id: int) -> List[Dict]:
        """Get applications for a student"""
        result = await self._request('applications', {'student_id': student_id})
        return result if isinstance(result, list) else []
    
    async def get_application_by_id(self, application_id: int) -> Optional[Dict]:
        """Get application by ID"""
        result = await self._request('applications', {'id': application_id})
        return result if result and isinstance(result, dict) else None
    
    async def create_application(self, application_data: Dict) -> Dict:
        """Create new application"""
        return await self._request('applications', method='POST', data=application_data)
    
    async def get_all_applications(self, limit: int = 100) -> List[Dict]:
        """Get all applications"""
        result = await self._request('applications', {'limit': limit})
        return result if isinstance(result, list) else []
    
    # ==================== HALL TICKET MANAGEMENT ====================
    
    async def get_hall_tickets_by_student(self, student_id: int) -> List[Dict]:
        """Get hall tickets for a student"""
        result = await self._request('hall_tickets', {'student_id': student_id})
        return result if isinstance(result, list) else []
    
    async def get_hall_tickets_by_exam(self, exam_id: int) -> List[Dict]:
        """Get hall tickets for an exam"""
        result = await self._request('hall_tickets', {'exam_id': exam_id})
        return result if isinstance(result, list) else []
    
    # ==================== EXAM SCHEDULE ====================
    
    async def get_exam_schedule(self, exam_id: int) -> List[Dict]:
        """Get schedule for an exam"""
        result = await self._request('exam_schedule', {'exam_id': exam_id})
        return result if isinstance(result, list) else []
    
    # ==================== DOCUMENT MANAGEMENT ====================
    
    async def get_student_documents(self, student_id: int) -> List[Dict]:
        """Get documents for a student"""
        result = await self._request('documents', {'student_id': student_id})
        return result if isinstance(result, list) else []
    
    # ==================== VERIFICATION HISTORY ====================
    
    async def get_verification_history(self, student_id: int) -> List[Dict]:
        """Get verification history for a student"""
        result = await self._request('verification_history', {'student_id': student_id})
        return result if isinstance(result, list) else []
    
    # ==================== DASHBOARD STATISTICS ====================
    
    async def get_dashboard_stats(self) -> Dict:
        """Get dashboard statistics"""
        result = await self._request('dashboard_stats')
        return result if isinstance(result, dict) else {
            'total_students': 0,
            'open_exams': 0,
            'verified_applications': 0
        }


# Singleton instance
infinityfree_client = InfinityFreeClient()
