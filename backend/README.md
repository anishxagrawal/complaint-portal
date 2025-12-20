🏙️ Smart City Complaint Management Portal

A FastAPI-powered backend system for managing citizen complaints in a smart city.
Citizens can submit complaints via text (voice-ready), and the system automatically validates, categorizes, and routes them to the appropriate municipal departments.

🎯 Built with clean architecture, strong validation, and production-ready practices.

✨ Key Features
👤 User Management

Citizen registration with Indian phone number validation

Email validation

OTP verification-ready architecture

User roles and verification status

📝 Complaint Handling

Text-based complaint submission

Automatic form filling

Status & urgency tracking

🤖 Smart Classification (Planned)

ML-based issue type classification

Automatic department routing

🧱 Backend Architecture

Service-layer pattern (clean separation of concerns)

Fully validated request/response schemas

Graceful error handling with HTTP status codes

🧪 Testing

26 automated tests

Covers happy paths, edge cases, and validation failures

📊 Project Status
Week	Progress
Week 1	✅ Complete
Week 2+	🚧 In Progress
✅ Completed in Week 1

Project structure & architecture

Database schema & models

Full CRUD APIs

Input validation using Pydantic

Centralized error handling

Service layer separation

26 passing test cases

🛠️ Tech Stack
Layer	Technology
Framework	FastAPI
ORM	SQLAlchemy
Database	SQLite
Validation	Pydantic
Testing	Pytest
Server	Uvicorn
🚀 Quick Start
Prerequisites

Python 3.11+

pip

SQLite (bundled with Python)

🔧 Installation
# Clone repository
git clone https://github.com/anishxagrawal/complaint-portal.git
cd complaint-portal/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

▶️ Run the Application
uvicorn app.main:app --reload


📍 API available at:

http://localhost:8000

Swagger UI: http://localhost:8000/docs

ReDoc: http://localhost:8000/redoc

🧪 Running Tests
pytest
pytest -v
pytest tests/test_complaints.py -v
pytest --cov=app


✅ Expected Result: All 26 tests pass

📁 Project Structure
complaint-portal/backend/
├── app/
│   ├── main.py
│   ├── database.py
│   ├── config.py
│   ├── deps.py
│   ├── models/
│   ├── schemas/
│   ├── routers/
│   └── services/
│
├── tests/
│   ├── conftest.py
│   ├── test_users.py
│   ├── test_departments.py
│   ├── test_issue_types.py
│   └── test_complaints.py
│
├── app.db
├── requirements.txt
└── README.md

📚 API Endpoints
👤 Users

POST /users/

GET /users/

GET /users/{user_id}

🏢 Departments

POST /departments/

GET /departments/

GET /departments/{dept_id}

🧩 Issue Types

POST /issue-types/

GET /issue-types/

GET /issue-types/{issue_id}

📝 Complaints

POST /complaints/

GET /complaints/

GET /complaints/{complaint_id}

💾 Database Schema Overview
Users

id (PK)

phone_number (Unique, +91XXXXXXXXXX)

full_name

email (Unique)

residential_address

role

is_verified

created_at, updated_at

Departments

id (PK)

name (Unique)

is_active

created_at

Issue Types

id (PK)

name

department_id (FK)

is_active

created_at

Complaints

id (PK)

user_id (FK)

issue_type_id (FK)

description

address

status

urgency

created_at, updated_at

🔄 Request Flow
Client Request
      ↓
Pydantic Validation
      ↓
FastAPI Router
      ↓
Service Layer
      ↓
Database
      ↓
Response

⚙️ Configuration

Example .env file:

DATABASE_URL=sqlite:///./app.db
DEBUG=true
ENVIRONMENT=development
SECRET_KEY=dev-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

📝 Example API Usage
Create User
curl -X POST "http://localhost:8000/users/" \
-H "Content-Type: application/json" \
-d '{
  "full_name": "John Doe",
  "phone_number": "+919876543210",
  "email": "john@example.com",
  "residential_address": "123 Main Street"
}'

📈 Test Results
26 passed in 2.41s ✅


Users: 3 tests

Departments: 7 tests

Issue Types: 7 tests

Complaints: 9 tests

🚀 Roadmap (Week 2+)

OTP-based authentication + JWT

Officer workflow & complaint assignment

ML-based complaint categorization

Duplicate complaint detection

Analytics dashboard

WebSocket real-time updates

Rate limiting & security hardening

👤 Author

Anish Agrawal
Computer Science Student | Backend & AI Enthusiast

📄 License

MIT License
