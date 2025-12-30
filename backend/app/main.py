# app/main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from dotenv import load_dotenv
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.database import engine, Base
from app.routers import auth, complaints, users, departments, issue_types, chat, workflow
from app.middleware.error_handler import setup_exception_handlers
from app.core.logging import setup_logging

# Import all models
from app.models.users import User
from app.models.complaints import Complaint
from app.models.departments import Department
from app.models.issue_types import IssueType
from app.models.chats import ChatConversation
from app.models.complaint_status_history import ComplaintStatusHistory  # ✅ NEW


# ==========================================
# 1. Load Environment & Setup Logging
# ==========================================

load_dotenv()
setup_logging(log_level="INFO")

# ==========================================
# 2. Initialize FastAPI App
# ==========================================

app = FastAPI(
    title="Smart City Complaint Portal",
    description="Citizen complaint management system with AI-powered chat and workflow management",
    version="2.0.0",  # ✅ Updated version
    redirect_slashes=False
)

# ==========================================
# 3. Setup Rate Limiting
# ==========================================

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ==========================================
# 4. Setup Error Handlers
# ==========================================

setup_exception_handlers(app)

# ==========================================
# 5. Add CORS Middleware
# ==========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# 6. Register Routers
# ==========================================

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(complaints.router)
app.include_router(departments.router)
app.include_router(issue_types.router)
app.include_router(chat.router)
app.include_router(workflow.router)  # ✅ NEW: Workflow endpoints

# ==========================================
# 7. Create Database Tables
# ==========================================

Base.metadata.create_all(bind=engine)

# ==========================================
# 8. Root Endpoint
# ==========================================

@app.get("/")
def read_root():
    """Health check endpoint"""
    return {
        "message": "Smart City Complaint Portal API",
        "version": "2.0.0",
        "status": "operational",
        "features": [
            "OTP Authentication",
            "Role-Based Access Control",
            "AI-Powered Chat",
            "Complaint Workflow Management",  # ✅ NEW
            "Status History Tracking",  # ✅ NEW
            "Officer Work Queues"  # ✅ NEW
        ]
    }

# ==========================================
# 9. Custom OpenAPI Schema (JWT Auth)
# ==========================================

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version="2.0.0",
        description=app.description,
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }

    # ✅ PUBLIC ENDPOINTS (no auth required)
    PUBLIC_PATHS = [
        "/",
        "/docs",
        "/openapi.json",
        "/redoc",
        "/auth/send-otp/",
        "/auth/verify-otp/"
    ]

    # Apply security only to protected endpoints
    for path, path_item in openapi_schema["paths"].items():
        if path in PUBLIC_PATHS:
            continue
            
        for operation in path_item.values():
            if isinstance(operation, dict) and "tags" in operation:
                operation["security"] = [{"BearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi