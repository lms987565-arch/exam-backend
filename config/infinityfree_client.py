# Add these methods to your InfinityFreeClient class

async def get_all_applications(self, limit: int = 100) -> List[Dict]:
    """Get all applications"""
    return await self._request('applications', {'limit': limit})

async def get_all_hall_tickets(self, limit: int = 100) -> List[Dict]:
    """Get all hall tickets"""
    # This aggregates from multiple exams
    exams = await self.get_all_exams()
    all_tickets = []
    for exam in exams[:10]:
        tickets = await self.get_hall_tickets_by_exam(exam['id'])
        all_tickets.extend(tickets[:20])
    return all_tickets[:limit]

async def get_all_documents(self, limit: int = 200) -> List[Dict]:
    """Get all documents"""
    students = await self.get_all_students(50)
    all_docs = []
    for student in students:
        docs = await self.get_student_documents(student['id'])
        all_docs.extend(docs)
    return all_docs[:limit]
