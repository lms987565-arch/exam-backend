# backend/config/infinityfree_client.py
import httpx
import json
from typing import Optional, List, Dict, Any
from datetime import datetime
import os
import asyncio

class InfinityFreeClient:
    """Async HTTP client for InfinityFree MySQL database bridge"""
    
    def __init__(self):
        self.base_url = "https://lmsmodern.infinityfree.me/proctored_api.php"
        self.api_key = os.getenv("INFINITYFREE_API_KEY", "render_backend_key_7x9k2m")
        self.timeout = httpx.Timeout(30.0)
        
    async def _request(self, endpoint: str, params: Dict = None, method: str = 'GET', data: Dict = None) -> Dict:
        """Make async request to InfinityFree API"""
        url = f"{self.base_url}?endpoint={endpoint}"
        
        # Add query parameters
        if method == 'GET' and params:
            for key, value in params.items():
                url += f"&{key}={value}"
        
        headers = {
            'Content-Type': 'application/json',
            'X-API-Key': self.api_key
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
                
                response.raise_for_status()
                result = response.json()
                
                if result.get('success'):
                    return result.get('data', {})
                else:
                    raise Exception(result.get('error', 'Unknown error'))
                    
            except httpx.HTTPStatusError as e:
                print(f"HTTP Error: {e}")
                raise Exception(f"API request failed: {str(e)}")
            except Exception as e:
                print(f"Request Error: {e}")
                raise
    
    # ==================== STUDENT MANAGEMENT ====================
    
    async def get_all_students(self, limit: int = 50) -> List[Dict]:
        """Get all students"""
        return await self._request('students', {'limit': limit})
    
    async def get_student_by_id(self, student_id: int) -> Optional[Dict]:
        """Get student by ID"""
        result = await self._request('students', {'id': student_id})
        return result if result else None
    
    async def get_student_by_email(self, email: str) -> Optional[Dict]:
        """Get student by email"""
        students = await self.get_all_students(500)
        for student in students:
            if student.get('email') == email:
                return student
        return None
    
    async def get_student_by_student_id(self, student_id_str: str) -> Optional[Dict]:
        """Get student by student_id (STU20260001 format)"""
        students = await self.get_all_students(500)
        for student in students:
            if student.get('student_id') == student_id_str:
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
        return await self._request('exams')
    
    async def get_exam_by_id(self, exam_id: int) -> Optional[Dict]:
        """Get exam by ID"""
        return await self._request('exams', {'id': exam_id})
    
    async def get_exams_by_status(self, status: str) -> List[Dict]:
        """Get exams by registration status (open/closed)"""
        return await self._request('exams', {'status': status})
    
    async def get_open_exams(self) -> List[Dict]:
        """Get open exams for registration"""
        return await self.get_exams_by_status('open')
    
    async def get_exam_by_code(self, exam_code: str) -> Optional[Dict]:
        """Get exam by exam code"""
        exams = await self.get_all_exams()
        for exam in exams:
            if exam.get('exam_code') == exam_code:
                return exam
        return None
    
    # ==================== APPLICATION MANAGEMENT ====================
    
    async def get_applications_by_student(self, student_id: int) -> List[Dict]:
        """Get applications for a student"""
        return await self._request('applications', {'student_id': student_id})
    
    async def get_application_by_id(self, application_id: int) -> Optional[Dict]:
        """Get application by ID"""
        return await self._request('applications', {'id': application_id})
    
    async def create_application(self, application_data: Dict) -> Dict:
        """Create new application"""
        return await self._request('applications', method='POST', data=application_data)
    
    async def get_all_applications(self, limit: int = 50) -> List[Dict]:
        """Get all applications (admin only)"""
        return await self._request('applications', {'limit': limit})
    
    # ✅ NEW METHOD (MERGED)
    async def get_all_applications_extended(self, limit: int = 100) -> List[Dict]:
        """Get all applications"""
        return await self._request('applications', {'limit': limit})
    
    async def get_applications_by_status(self, status: str) -> List[Dict]:
        """Get applications by status"""
        all_apps = await self.get_all_applications(500)
        return [app for app in all_apps if app.get('status') == status]
    
    async def update_application_status(self, application_id: int, status: str, progress: int = None) -> Dict:
        """Update application status"""
        update_data = {'status': status}
        if progress is not None:
            update_data['progress_percentage'] = progress
        return await self._request('applications', method='PUT', data={'id': application_id, **update_data})
    
    # ==================== HALL TICKET MANAGEMENT ====================
    
    async def get_hall_tickets_by_student(self, student_id: int) -> List[Dict]:
        """Get hall tickets for a student"""
        return await self._request('hall_tickets', {'student_id': student_id})
    
    async def get_hall_tickets_by_exam(self, exam_id: int) -> List[Dict]:
        """Get hall tickets for an exam"""
        return await self._request('hall_tickets', {'exam_id': exam_id})
    
    # ✅ NEW METHOD (MERGED)
    async def get_all_hall_tickets(self, limit: int = 100) -> List[Dict]:
        """Get all hall tickets"""
        exams = await self.get_all_exams()
        all_tickets = []
        for exam in exams[:10]:
            tickets = await self.get_hall_tickets_by_exam(exam['id'])
            all_tickets.extend(tickets[:20])
        return all_tickets[:limit]
    
    async def get_hall_ticket_by_number(self, hall_ticket_no: str) -> Optional[Dict]:
        """Get hall ticket by number"""
        exams = await self.get_all_exams()
        for exam in exams:
            tickets = await self.get_hall_tickets_by_exam(exam['id'])
            for ticket in tickets:
                if ticket.get('hall_ticket_no') == hall_ticket_no:
                    return ticket
        return None
    
    # ==================== DOCUMENT MANAGEMENT ====================
    
    async def get_student_documents(self, student_id: int) -> List[Dict]:
        """Get documents for a student"""
        return await self._request('documents', {'student_id': student_id})
    
    # ✅ NEW METHOD (MERGED)
    async def get_all_documents(self, limit: int = 200) -> List[Dict]:
        """Get all documents"""
        students = await self.get_all_students(50)
        all_docs = []
        for student in students:
            docs = await self.get_student_documents(student['id'])
            all_docs.extend(docs)
        return all_docs[:limit]
    
    async def upload_document(self, document_data: Dict) -> Dict:
        """Upload document record"""
        return await self._request('documents', method='POST', data=document_data)
    
    async def get_document_by_type(self, student_id: int, document_type: str) -> Optional[Dict]:
        """Get document by type"""
        documents = await self.get_student_documents(student_id)
        for doc in documents:
            if doc.get('document_type') == document_type:
                return doc
        return None
    
    async def update_document_status(self, document_id: int, status: str, remark: str = None, verified_by: str = None) -> Dict:
        """Update document verification status"""
        update_data = {
            'id': document_id,
            'status': status,
            'remark': remark or '',
            'verified_by': verified_by or 'system'
        }
        return await self._request('documents', method='PUT', data=update_data)
    
    async def are_all_documents_uploaded(self, student_id: int) -> bool:
        """Check if all required documents are uploaded"""
        documents = await self.get_student_documents(student_id)
        required_docs = ['aadhaar', 'ssc_marksheet', 'hsc_marksheet', 'photo', 'signature']
        uploaded_types = [doc.get('document_type') for doc in documents]
        return all(doc_type in uploaded_types for doc_type in required_docs)
    
    # ==================== VERIFICATION HISTORY ====================
    
    async def get_verification_history(self, student_id: int) -> List[Dict]:
        """Get verification history for a student"""
        return await self._request('verification_history', {'student_id': student_id})
    
    async def add_verification_record(self, record_data: Dict) -> Dict:
        """Add verification record"""
        return await self._request('verification', method='POST', data=record_data)
    
    # ==================== DASHBOARD & STATISTICS ====================
    
    async def get_dashboard_stats(self) -> Dict:
        """Get dashboard statistics"""
        return await self._request('dashboard_stats')
    
    async def get_student_dashboard(self, student_id: int) -> Dict:
        """Get student dashboard data"""
        applications, hall_tickets, documents, verification_history = await asyncio.gather(
            self.get_applications_by_student(student_id),
            self.get_hall_tickets_by_student(student_id),
            self.get_student_documents(student_id),
            self.get_verification_history(student_id)
        )
        
        return {
            'applications': applications,
            'hall_tickets': hall_tickets,
            'documents': documents,
            'verification_history': verification_history,
            'stats': {
                'total_applications': len(applications),
                'verified_applications': len([a for a in applications if a.get('status') == 'verified']),
                'pending_applications': len([a for a in applications if a.get('status') == 'submitted']),
                'total_documents': len(documents),
                'verified_documents': len([d for d in documents if d.get('status') == 'verified'])
            }
        }
    
    async def get_admin_dashboard(self) -> Dict:
        """Get admin dashboard data"""
        stats, all_students, all_applications, all_exams = await asyncio.gather(
            self.get_dashboard_stats(),
            self.get_all_students(100),
            self.get_all_applications(100),
            self.get_all_exams()
        )
        
        applications_by_status = {
            'draft': 0,
            'submitted': 0,
            'verified': 0,
            'rejected': 0
        }
        
        for app in all_applications:
            status = app.get('status')
            if status in applications_by_status:
                applications_by_status[status] += 1
        
        return {
            'stats': stats,
            'total_students': len(all_students),
            'total_exams': len(all_exams),
            'applications_by_status': applications_by_status,
            'recent_students': all_students[:10],
            'recent_applications': all_applications[:10]
        }


# Singleton instance
infinityfree_client = InfinityFreeClient()
