<h1 align="center">🏙️ Smart City Complaint Management Portal</h1>

<p align="center">
A clean, scalable FastAPI backend for managing citizen complaints in a smart city.
</p>

---

## 🌟 Overview

Urban complaint systems often fail due to:

- Poor input validation  
- No structured routing  
- Messy backend logic  

This project solves those problems using:

- Strict validation  
- Service-layer architecture  
- Test-driven development  

---

## ✨ Features

- Citizen registration with Indian phone validation  
- Complaint submission & tracking  
- Automatic issue categorization (ML-ready)  
- Clean service-layer architecture  
- Full CRUD APIs  
- 26 automated tests  

---

## 🧱 Architecture Overview

```mermaid
graph TD
    A[Client / UI] --> B[FastAPI Router]
    B --> C[Pydantic Validation]
    C --> D[Service Layer]
    D --> E[Database]
🔄 Request Lifecycle
mermaid
Copy code
sequenceDiagram
    participant Client
    participant API
    participant Service
    participant DB

    Client->>API: HTTP Request
    API->>API: Validate Input (Pydantic)
    API->>Service: Call Business Logic
    Service->>DB: Read / Write Data
    DB-->>Service: Result
    Service-->>API: Response
    API-->>Client: JSON Response
🚀 Quick Start
Prerequisites
Python 3.11+

pip

Setup
bash
Copy code
git clone https://github.com/anishxagrawal/complaint-portal.git
cd complaint-portal/backend

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
Run Server
bash
Copy code
uvicorn app.main:app --reload
API: http://localhost:8000

Docs: http://localhost:8000/docs

📁 Project Structure
text
Copy code
backend/
├── app/
│   ├── main.py
│   ├── database.py
│   ├── deps.py
│   ├── models/
│   ├── schemas/
│   ├── routers/
│   └── services/
├── tests/
├── app.db
└── requirements.txt
📚 API Endpoints
<details> <summary><strong>👤 Users</strong></summary>
POST /users/

GET /users/

GET /users/{user_id}

</details> <details> <summary><strong>🏢 Departments</strong></summary>
POST /departments/

GET /departments/

GET /departments/{id}

</details> <details> <summary><strong>🧩 Issue Types</strong></summary>
POST /issue-types/

GET /issue-types/

GET /issue-types/{id}

</details> <details> <summary><strong>📝 Complaints</strong></summary>
POST /complaints/

GET /complaints/

GET /complaints/{id}

</details>
💾 Database Schema
<details> <summary><strong>👤 Users Table</strong></summary>
Column	Type	Notes
id	Integer	Primary Key
phone_number	String	Unique, +91XXXXXXXXXX
full_name	String	2–255 chars
email	String	Unique
residential_address	String	5–500 chars
role	String	Default: USER
is_verified	Boolean	Default: false
created_at	Timestamp	Auto
updated_at	Timestamp	Auto

</details> <details> <summary><strong>🏢 Departments Table</strong></summary>
Column	Type	Notes
id	Integer	Primary Key
name	String	Unique
is_active	Boolean	Default: true
created_at	Timestamp	Auto

</details> <details> <summary><strong>🧩 Issue Types Table</strong></summary>
Column	Type	Notes
id	Integer	Primary Key
name	String	3–100 chars
department_id	Integer	Foreign Key
is_active	Boolean	Default: true
created_at	Timestamp	Auto

</details> <details> <summary><strong>📝 Complaints Table</strong></summary>
Column	Type	Notes
id	Integer	Primary Key
user_id	Integer	FK → Users
issue_type_id	Integer	FK → Issue Types
description	String	10–1000 chars
address	String	5–500 chars
status	String	OPEN
urgency	String	MEDIUM
created_at	Timestamp	Auto
updated_at	Timestamp	Auto

</details>
🧪 Testing
bash
Copy code
pytest
pytest -v
pytest --cov=app
✅ 26 tests passing

🚀 Roadmap
OTP authentication + JWT

Officer workflows

ML-based categorization

Duplicate complaint detection

Admin dashboard

WebSockets for live updates

👤 Author
Anish Agrawal
Computer Science Student | Backend & AI Enthusiast

📄 License
MIT License
