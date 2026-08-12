from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import engine, Base, SessionLocal
import models


app = FastAPI(title="QOS Platform API")


# Create database tables
Base.metadata.create_all(bind=engine)


# Database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Registration request model
class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    role: str


# Home API
@app.get("/")
def home():
    return {
        "message": "QOS Platform API is running"
    }


# Register API
@app.post("/api/v1/auth/register")
def register(
    user: RegisterRequest,
    db: Session = Depends(get_db)
):
    new_user = models.User(
        name=user.name,
        email=user.email,
        password=user.password,
        role=user.role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "Registration successful",
        "name": new_user.name,
        "email": new_user.email,
        "role": new_user.role
    }