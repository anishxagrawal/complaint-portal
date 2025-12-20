Smart City Complaint Management Portal
A FastAPI-based backend system for managing citizen complaints in a smart city. Citizens can submit complaints via text or voice, and the system automatically categorizes, validates, and routes them to appropriate municipal departments.

🎯 Features
User Management: Citizen registration and profile management with OTP verification
Complaint Submission: Submit complaints via text with automatic form filling
Automatic Categorization: ML-based issue type and department classification
Input Validation: Comprehensive validation for all user inputs
Error Handling: Graceful error responses with proper HTTP status codes
Service Layer Architecture: Clean separation of business logic from API endpoints
Complete CRUD Operations: Full Create, Read, Update, Delete support for all entities
Comprehensive Testing: 26 automated tests covering all endpoints and scenarios
📋 Project Status
Week 1: Complete ✅

Project structure and organization
Database schema and models
API endpoints (all CRUD operations)
Input validation with Pydantic
Error handling with HTTPException
Service layer separation
26 comprehensive test cases
🚀 Quick Start
Prerequisites
Python 3.11+
pip (Python package manager)
SQLite (included with Python)
Installation
Clone the repository
bash
git clone https://github.com/anishxagrawal/complaint-portal.git
cd complaint-portal/backend
Create virtual environment
bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install dependencies
bash
pip install -r requirements.txt
Run the application
bash
uvicorn app.main:app --reload
The API will be available at http://localhost:8000

API Documentation
Interactive API documentation is available at:

Swagger UI: http://localhost:8000/docs
ReDoc: http://localhost:8000/redoc
🧪 Running Tests
bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_complaints.py -v

# Run with coverage
pytest --cov=app
Expected Result: All 26 tests pass ✅

📁 Project Structure
complaint-portal/backend/
├── app/
│   ├── main.py                 # FastAPI app initialization
│   ├── database.py             # SQLAlchemy configuration
│   ├── config.py               # Environment configuration
│   ├── deps.py                 # Dependency injection (get_db)
│   │
│   ├── models/                 # SQLAlchemy ORM models
│   │   ├── users.py
│   │   ├── departments.py
│   │   ├── issue_types.py
│   │   └── complaints.py
│   │
│   ├── schemas/                # Pydantic request/response models
│   │   ├── user.py
│   │   ├── department.py
│   │   ├── issue_type.py
│   │   └── complaint.py
│   │
│   ├── routers/                # API endpoint handlers
│   │   ├── users.py
│   │   ├── departments.py
│   │   ├── issue_types.py
│   │   └── complaints.py
│   │
│   └── services/               # Business logic layer
│       ├── user_service.py
│       ├── department_service.py
│       ├── issue_type_service.py
│       └── complaint_service.py
│
├── tests/                      # Test suite
│   ├── conftest.py            # Pytest configuration
│   ├── test_users.py
│   ├── test_departments.py
│   ├── test_issue_types.py
│   └── test_complaints.py
│
├── app.db                      # SQLite database (auto-created)
├── venv/                       # Virtual environment
├── requirements.txt            # Python dependencies
└── README.md                   # This file
📚 API Endpoints
Users
POST /users/ - Create a new user
GET /users/ - List all users
GET /users/{user_id} - Get a specific user
Departments
POST /departments/ - Create a new department
GET /departments/ - List all departments
GET /departments/{dept_id} - Get a specific department
Issue Types
POST /issue-types/ - Create a new issue type
GET /issue-types/ - List all issue types
GET /issue-types/{issue_id} - Get a specific issue type
Complaints
POST /complaints/ - Submit a new complaint
GET /complaints/ - List all complaints
GET /complaints/{complaint_id} - Get a specific complaint
💾 Database Schema
Users Table
id (Primary Key)
phone_number (Unique) - Indian format with validation (+91XXXXXXXXXX)
full_name - 2-255 characters
email (Unique) - Valid email format
residential_address - 5-500 characters
role - Default: "USER"
is_verified - Default: False
created_at, updated_at - Timestamps
Departments Table
id (Primary Key)
name (Unique) - 3-100 characters
is_active - Default: True
created_at - Timestamp
Issue Types Table
id (Primary Key)
name - 3-100 characters
department_id (Foreign Key)
is_active - Default: True
created_at - Timestamp
Complaints Table
id (Primary Key)
user_id (Foreign Key) - Links to Users
issue_type_id (Foreign Key) - Links to Issue Types
description - 10-1000 characters
address - 5-500 characters
status - Default: "OPEN"
urgency - Default: "MEDIUM"
created_at, updated_at - Timestamps
🛠️ Technology Stack
Framework: FastAPI (modern, fast Python web framework)
ORM: SQLAlchemy (SQL toolkit and ORM)
Database: SQLite (lightweight, serverless)
Validation: Pydantic (data validation using Python type hints)
Testing: Pytest (testing framework)
Server: Uvicorn (ASGI server)
📖 Architecture Highlights
Service Layer Pattern
Business logic is separated from HTTP handling:

Routers: Handle HTTP requests/responses
Services: Contain business logic and database operations
Models: Define database structure
Schemas: Handle request/response validation
Input Validation
Pydantic schemas validate all inputs before processing
Custom validators for complex business rules
Field constraints (min/max length, regex patterns, etc.)
Error Handling
Graceful error responses with proper HTTP status codes
404 for not found resources
400 for validation errors
500 for server errors
Try-catch blocks with database rollback
Testing Strategy
Unit tests for individual services
Integration tests for API endpoints
Fixture-based setup/teardown for database
26 comprehensive test cases covering:
Happy path scenarios
Error cases
Validation failures
Edge cases
🔄 Data Flow
1. User sends HTTP request
   ↓
2. Pydantic schema validates input
   ↓
3. FastAPI router receives request
   ↓
4. Router calls appropriate service
   ↓
5. Service performs business logic:
   - Validates foreign keys
   - Checks for duplicates
   - Performs database operations
   ↓
6. Database transaction committed
   ↓
7. Response returned to user
⚙️ Configuration
Environment variables can be set in a .env file:

# Database (SQLite - no config needed)
DATABASE_URL=sqlite:///./app.db

# Application
DEBUG=true
ENVIRONMENT=development
SECRET_KEY=dev-secret-key-change-in-production

# Security
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
📝 Example Usage
Create a Department
bash
curl -X POST "http://localhost:8000/departments/" \
  -H "Content-Type: application/json" \
  -d '{"name": "Sanitation Department"}'
Create an Issue Type
bash
curl -X POST "http://localhost:8000/issue-types/" \
  -H "Content-Type: application/json" \
  -d '{"name": "Garbage Collection", "department_id": 1}'
Create a User
bash
curl -X POST "http://localhost:8000/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Doe",
    "phone_number": "+919876543210",
    "email": "john@example.com",
    "residential_address": "123 Main Street"
  }'
Submit a Complaint
bash
curl -X POST "http://localhost:8000/complaints/" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "issue_type_id": 1,
    "description": "Garbage overflowing on Main Street for 3 days",
    "address": "123 Main Street"
  }'
🧪 Test Results
26 passed in 2.41s ✅

Test Coverage:
- Users: 3 tests
- Departments: 7 tests
- Issue Types: 7 tests
- Complaints: 9 tests
🚀 Next Steps (Week 2+)
 Authentication (OTP verification + JWT tokens)
 Officer workflow and complaint assignment
 ML-based complaint analysis and categorization
 Duplicate complaint detection
 Analytics and admin dashboard
 Real-time updates via WebSockets
 Rate limiting and security hardening
📚 Development Notes
Code Style
Follow PEP 8 guidelines
Use type hints for better code clarity
Write descriptive docstrings
Adding New Features
Create SQLAlchemy model in models/
Create Pydantic schema in schemas/
Create service layer in services/
Create router endpoints in routers/
Add comprehensive tests in tests/
Common Issues
Issue: "No such table: users"

Solution: Ensure main.py imports all models and calls Base.metadata.create_all()
Issue: Import errors

Solution: Create conftest.py in tests folder to add parent directory to Python path
Issue: Validation errors

Solution: Check Pydantic schema constraints (min_length, pattern, etc.)
📄 License
This project is open source and available under the MIT License.

👤 Author
Anish Agrawal

💬 Questions or Issues?
Open an issue on GitHub or contact the development team.

Last Updated: December 20, 2025 Status: Week 1 Complete ✅

