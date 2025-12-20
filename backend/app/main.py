# app/main.py
from fastapi import FastAPI
from app.database import engine, Base

# ✅ IMPORT ALL MODELS (must be before create_all)
from app.models import users, departments, issue_types, complaints

# ✅ Import routers
from app.routers import users as users_router
from app.routers import complaints as complaints_router
from app.routers import departments as departments_router
from app.routers import issue_types as issue_types_router

# ✅ CREATE ALL TABLES ON STARTUP
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Complaint Portal API",
    description="Backend API for a city complaint management system",
    version="1.0.0"
)

# Include routers (use aliases to avoid name conflicts)
app.include_router(users_router.router)
app.include_router(complaints_router.router)
app.include_router(departments_router.router)
app.include_router(issue_types_router.router)