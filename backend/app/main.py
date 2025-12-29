# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from fastapi.openapi.utils import get_openapi

from app.routers import auth, complaints, users, departments, issue_types

# Import all models
from app.models.users import User
from app.models.complaints import Complaint
from app.models.departments import Department
from app.models.issue_types import IssueType

app = FastAPI(
    title="Smart City Complaint Portal",
    description="Citizen complaint management system",
    redirect_slashes=False
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(complaints.router)
app.include_router(departments.router)
app.include_router(issue_types.router)

Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"message": "Smart City Complaint Portal API"}

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version="1.0.0",
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