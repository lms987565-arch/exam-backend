# backend/config/infinityfree_api.py
import requests
import json
from typing import Optional, List, Dict, Any
from datetime import datetime
import os

class InfinityFreeAPI:
    """API client for InfinityFree MySQL database bridge"""
    
    def __init__(self):
        self.base_url = "https://lmsmodern.infinityfree.me/proctored_api.php"
        self.api_key = "render_backend_key_7x9k2m"  # Your API key
        self.use_encryption = False
        
    def _request(self, endpoint: str, params: Dict = None, method: str = 'GET', data: Dict = None) -> Dict:
        """Make request to InfinityFree API"""
        url = f"{self.base_url}?endpoint={endpoint}"
        
        if self.use_encryption:
            url += "&encrypt=true"
        
        # Add query parameters
        if method == 'GET' and params:
            for key, value in params.items():
                url += f"&{key}={value}"
        
        headers = {
            'Content-Type': 'application/json',
            'X-API-Key': self.api_key
        }
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=data)
            elif method == 'PUT':
                response = requests.put(url, headers=headers, json=data)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response.raise_for_status()
            result = response.json()
            
            if result.get('success'):
                return result.get('data', {})
            else:
                raise Exception(result.get('error', 'Unknown error'))
                
        except requests.exceptions.RequestException as e:
            print(f"API Request Error: {e}")
            raise Exception(f"Failed to connect to InfinityFree API: {str(e)}")
    
    # ==================== STUDENT MANAGEMENT ====================
    
    def get_all_students(self, limit: int = 50) -> List[Dict]:
        """Get all students"""
        return self._request('students', {'limit': limit})
    
    def get_student_by_id(self, student_id: int) -> Optional[Dict]:
        """Get student by ID"""
        result = self._request('students', {'id': student_id})
        return result if result else None
    
    def get_student_by_email(self, email: str) -> Optional[Dict]:
        """Get student by email"""
        students = self.get_all_students(500)
        for student in students:
            if student.get('email') == email:
                return student
        return None
    
    def get_student_by_student_id(self, student_id_str: str) -> Optional[Dict]:
        """Get student by student_id (STU20260001 format)"""
        students = self.get_all_students(500)
        for student in students:
            if student.get('student_id') == student_id_str:
                return student
        return None
    
    def create_student(self, student_data: Dict) -> Dict:
        """Create new student"""
        return self._request('students', method='POST', data=student_data)
    
    def student_login(self, email: str, password: str) -> Dict:
        """Student login"""
        return self._request('auth', method='POST', data={'email': email, 'password': password})
    
    # ==================== EXAM MANAGEMENT ====================
    
    def get_all_exams(self) -> List[Dict]:
        """Get all exams"""
        return self._request('exams')
    
    def get_exam_by_id(self, exam_id: int) -> Optional[Dict]:
        """Get exam by ID"""
        return self._request('exams', {'id': exam_id})
    
    def get_exams_by_status(self, status: str) -> List[Dict]:
        """Get exams by registration status (open/closed)"""
        return self._request('exams', {'status': status})
    
    def get_open_exams(self) -> List[Dict]:
        """Get open exams for registration"""
        return self.get_exams_by_status('open')
    
    def get_exam_by_code(self, exam_code: str) -> Optional[Dict]:
        """Get exam by exam code"""
        exams = self.get_all_exams()
        for exam in exams:
            if exam.get('exam_code') == exam_code:
                return exam
        return None
    
    # ==================== APPLICATION MANAGEMENT ====================
    
    def get_applications_by_student(self, student_id: int) -> List[Dict]:
        """Get applications for a student"""
        return self._request('applications', {'student_id': student_id})
    
    def get_application_by_id(self, application_id: int) -> Optional[Dict]:
        """Get application by ID"""
        return self._request('applications', {'id': application_id})
    
    def create_application(self, application_data: Dict) -> Dict:
        """Create new application"""
        return self._request('applications', method='POST', data=application_data)
    
    def get_all_applications(self, limit: int = 50) -> List[Dict]:
        """Get all applications (admin only)"""
        return self._request('applications', {'limit': limit})
    
    def get_applications_by_status(self, status: str) -> List[Dict]:
        """Get applications by status"""
        all_apps = self.get_all_applications(500)
        return [app for app in all_apps if app.get('status') == status]
    
    def update_application_status(self, application_id: int, status: str, progress: int = None) -> Dict:
        """Update application status"""
        update_data = {'status': status}
        if progress is not None:
            update_data['progress_percentage'] = progress
        return self._request('applications', method='PUT', data={'id': application_id, **update_data})
    
    # ==================== HALL TICKET MANAGEMENT ====================
    
    def get_hall_tickets_by_student(self, student_id: int) -> List[Dict]:
        """Get hall tickets for a student"""
        return self._request('hall_tickets', {'student_id': student_id})
    
    def get_hall_tickets_by_exam(self, exam_id: int) -> List[Dict]:
        """Get hall tickets for an exam"""
        return self._request('hall_tickets', {'exam_id': exam_id})
    
    def get_hall_ticket_by_number(self, hall_ticket_no: str) -> Optional[Dict]:
        """Get hall ticket by number"""
        # This would need a specific endpoint, for now search through exams
        exams = self.get_all_exams()
        for exam in exams:
            tickets = self.get_hall_tickets_by_exam(exam['id'])
            for ticket in tickets:
                if ticket.get('hall_ticket_no') == hall_ticket_no:
                    return ticket
        return None
    
    # ==================== EXAM SCHEDULE ====================
    
    def get_exam_schedule(self, exam_id: int) -> List[Dict]:
        """Get schedule for an exam"""
        return self._request('exam_schedule', {'exam_id': exam_id})
    
    def get_today_schedule(self) -> List[Dict]:
        """Get today's schedule for all exams"""
        exams = self.get_all_exams()
        today = datetime.now().date().isoformat()
        schedule = []
        
        for exam in exams:
            exam_schedule = self.get_exam_schedule(exam['id'])
            today_schedule = [s for s in exam_schedule if s.get('exam_date') == today]
            schedule.extend(today_schedule)
        
        return schedule
    
    def get_active_exam_slots(self) -> List[Dict]:
        """Get currently active exam slots"""
        now = datetime.now()
        current_time = now.time().strftime('%H:%M:%S')
        today = now.date().isoformat()
        
        exams = self.get_all_exams()
        active_slots = []
        
        for exam in exams:
            schedule = self.get_exam_schedule(exam['id'])
            for slot in schedule:
                if (slot.get('exam_date') == today and 
                    slot.get('slot_start') <= current_time <= slot.get('slot_end') and
                    slot.get('status') == 'open'):
                    active_slots.append(slot)
        
        return active_slots
    
    # ==================== SLOT BOOKINGS ====================
    
    def get_slot_bookings_by_student(self, student_id: int) -> List[Dict]:
        """Get slot bookings for a student"""
        return self._request('slot_bookings', {'student_id': student_id})
    
    # ==================== TOKEN MANAGEMENT ====================
    
    def validate_token(self, token_no: str) -> Optional[Dict]:
        """Validate exam token"""
        return self._request('tokens', {'token_no': token_no})
    
    def can_access_exam(self, token_no: str) -> bool:
        """Check if token is valid for exam access"""
        token = self.validate_token(token_no)
        if not token:
            return False
        
        now = datetime.now()
        expiry = datetime.fromisoformat(token.get('expires_at', '').replace(' ', 'T'))
        
        return token.get('status') == 'active' and now < expiry
    
    def mark_token_used(self, token_no: str, ip_address: str = None) -> Dict:
        """Mark token as used"""
        token = self.validate_token(token_no)
        if token:
            return self._request('tokens', method='PUT', data={
                'id': token['id'],
                'status': 'used',
                'used_ip': ip_address or 'unknown'
            })
        return {'error': 'Token not found'}
    
    # ==================== DOCUMENT MANAGEMENT ====================
    
    def get_student_documents(self, student_id: int) -> List[Dict]:
        """Get documents for a student"""
        return self._request('documents', {'student_id': student_id})
    
    def upload_document(self, document_data: Dict) -> Dict:
        """Upload document record"""
        return self._request('documents', method='POST', data=document_data)
    
    def get_document_by_type(self, student_id: int, document_type: str) -> Optional[Dict]:
        """Get document by type"""
        documents = self.get_student_documents(student_id)
        for doc in documents:
            if doc.get('document_type') == document_type:
                return doc
        return None
    
    def update_document_status(self, document_id: int, status: str, remark: str = None, verified_by: str = None) -> Dict:
        """Update document verification status"""
        update_data = {
            'id': document_id,
            'status': status,
            'remark': remark or '',
            'verified_by': verified_by or 'system'
        }
        return self._request('documents', method='PUT', data=update_data)
    
    def are_all_documents_uploaded(self, student_id: int) -> bool:
        """Check if all required documents are uploaded"""
        documents = self.get_student_documents(student_id)
        required_docs = ['aadhaar', 'ssc_marksheet', 'hsc_marksheet', 'photo', 'signature']
        uploaded_types = [doc.get('document_type') for doc in documents]
        return all(doc_type in uploaded_types for doc_type in required_docs)
    
    # ==================== VERIFICATION HISTORY ====================
    
    def get_verification_history(self, student_id: int) -> List[Dict]:
        """Get verification history for a student"""
        return self._request('verification_history', {'student_id': student_id})
    
    def add_verification_record(self, record_data: Dict) -> Dict:
        """Add verification record"""
        return self._request('verification', method='POST', data=record_data)
    
    # ==================== DASHBOARD & STATISTICS ====================
    
    def get_dashboard_stats(self) -> Dict:
        """Get dashboard statistics"""
        return self._request('dashboard_stats')
    
    async def get_student_dashboard(self, student_id: int) -> Dict:
        """Get student dashboard data"""
        applications = self.get_applications_by_student(student_id)
        hall_tickets = self.get_hall_tickets_by_student(student_id)
        documents = self.get_student_documents(student_id)
        verification_history = self.get_verification_history(student_id)
        
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
        stats = self.get_dashboard_stats()
        all_students = self.get_all_students(100)
        all_applications = self.get_all_applications(100)
        all_exams = self.get_all_exams()
        
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
infinityfree_api = InfinityFreeAPI()
