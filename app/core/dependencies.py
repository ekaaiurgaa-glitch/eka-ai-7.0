from fastapi import Depends, HTTPException, status
from app.db.session import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# In a real app, you might have more dependencies here, for example:
# - Getting the current tenant
# - Getting a Redis connection
# - etc.
