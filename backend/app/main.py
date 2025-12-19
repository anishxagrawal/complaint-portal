from fastapi import FastAPI

from app.routers import users, complaints, departments, issue_types

app = FastAPI(
    title="Complaint Portal API",
    description="Backend API for a city complaint management system",
    version="1.0.0"
)

# Include routers
app.include_router(users.router)
app.include_router(complaints.router)
app.include_router(departments.router)
app.include_router(issue_types.router)
