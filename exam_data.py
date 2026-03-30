EXAM_DATA = {
    "exam_name": "B.Sc. Computer Science — Unit Test I",
    "exam_code": "CS401",
    "total_time": 3600,
    "total_marks": 30,
    "sections": [
        {
            "id": "A",
            "name": "Section A",
            "subtitle": "Fundamentals",
            "color": "#1a73e8",
            "bg": "#e8f0fe",
            "questions": [
                {
                    "id": 1,
                    "text": "What is the time complexity of Binary Search?",
                    "type": "MCQ",
                    "marks": 2,
                    "opts": ["O(n)", "O(log n)", "O(n²)", "O(1)"],
                    "correct": 1
                },
                {
                    "id": 2,
                    "text": "Which data structure uses LIFO (Last In First Out) principle?",
                    "type": "MCQ",
                    "marks": 2,
                    "opts": ["Queue", "Linked List", "Stack", "Tree"],
                    "correct": 2
                },
                {
                    "id": 3,
                    "text": "What does CPU stand for?",
                    "type": "MCQ",
                    "marks": 1,
                    "opts": [
                        "Central Processing Unit",
                        "Computer Processing Unit",
                        "Core Processing Unit",
                        "Central Program Unit"
                    ],
                    "correct": 0
                },
                {
                    "id": 4,
                    "text": "Which of the following is NOT a programming paradigm?",
                    "type": "MCQ",
                    "marks": 2,
                    "opts": ["Object Oriented", "Functional", "Structural", "Sequential"],
                    "correct": 3
                },
                {
                    "id": 5,
                    "text": "What is the output of: print(2 ** 3) in Python?",
                    "type": "MCQ",
                    "marks": 1,
                    "opts": ["6", "8", "9", "5"],
                    "correct": 1
                }
            ]
        },
        {
            "id": "B",
            "name": "Section B",
            "subtitle": "Databases & Networking",
            "color": "#34a853",
            "bg": "#e6f4ea",
            "questions": [
                {
                    "id": 6,
                    "text": "SQL stands for ___________",
                    "type": "FILL",
                    "marks": 2,
                    "correct": "structured query language"
                },
                {
                    "id": 7,
                    "text": "Which layer of the OSI model handles routing?",
                    "type": "MCQ",
                    "marks": 2,
                    "opts": ["Physical", "Data Link", "Network", "Transport"],
                    "correct": 2
                },
                {
                    "id": 8,
                    "text": "What does HTML stand for?",
                    "type": "FILL",
                    "marks": 1,
                    "correct": "hypertext markup language"
                },
                {
                    "id": 9,
                    "text": "Which type of key uniquely identifies each row in a table?",
                    "type": "MCQ",
                    "marks": 2,
                    "opts": ["Foreign Key", "Primary Key", "Composite Key", "Candidate Key"],
                    "correct": 1
                },
                {
                    "id": 10,
                    "text": "HTTP stands for ___________",
                    "type": "FILL",
                    "marks": 1,
                    "correct": "hypertext transfer protocol"
                }
            ]
        },
        {
            "id": "C",
            "name": "Section C",
            "subtitle": "Algorithms & Advanced",
            "color": "#7c4dff",
            "bg": "#f3e8ff",
            "questions": [
                {
                    "id": 11,
                    "text": "Which sorting algorithm has best average-case O(n log n) performance?",
                    "type": "MCQ",
                    "marks": 3,
                    "opts": ["Bubble Sort", "Insertion Sort", "Merge Sort", "Selection Sort"],
                    "correct": 2
                },
                {
                    "id": 12,
                    "text": "The binary representation of decimal 10 is ___________",
                    "type": "FILL",
                    "marks": 2,
                    "correct": "1010"
                },
                {
                    "id": 13,
                    "text": "Which graph traversal uses a queue?",
                    "type": "MCQ",
                    "marks": 2,
                    "opts": ["DFS", "BFS", "Dijkstra", "Prim"],
                    "correct": 1
                },
                {
                    "id": 14,
                    "text": "What is the worst-case time complexity of QuickSort?",
                    "type": "MCQ",
                    "marks": 3,
                    "opts": ["O(n log n)", "O(n)", "O(n²)", "O(log n)"],
                    "correct": 2
                },
                {
                    "id": 15,
                    "text": "A stack overflow typically occurs due to ___________",
                    "type": "FILL",
                    "marks": 2,
                    "correct": "infinite recursion"
                }
            ]
        }
    ]
}
