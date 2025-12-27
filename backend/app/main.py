from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base

from app.routers import auth, complaints, users, departments, issue_types

# 🔑 IMPORT ALL MODELS (VERY IMPORTANT)
from app.models.users import User
from app.models.complaints import Complaint
from app.models.departments import Department
from app.models.issue_types import IssueType

app = FastAPI(
    title="Smart City Complaint Portal",
    description="Citizen complaint management system"
)

# Add CORS middleware (allow frontend to call API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router)           # NEW: Auth endpoints
app.include_router(users.router)
app.include_router(complaints.router)
app.include_router(departments.router)
app.include_router(issue_types.router)

Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"message": "Smart City Complaint Portal API"}