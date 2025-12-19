from app.database import engine, Base
from app.models import users, departments, issue_types, complaints

Base.metadata.create_all(bind=engine)

print("✅ Tables created successfully")