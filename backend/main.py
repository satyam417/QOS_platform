from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import uuid
from passlib.context import CryptContext

from database import engine, Base, SessionLocal
import models

from app.api.v1.auth import router as auth_router
from app.api.v1.customer import router as customer_router

app = FastAPI(title="QOS Platform API")

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


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

# Login request model


class LoginRequest(BaseModel):
    email: str
    password: str

# Home API


@app.get("/")
def home():
    return {
        "message": "QOS Platform API is running"
    }


# Health API
@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


# Ready API
@app.get("/ready")
def ready():
    return {
        "status": "ready"
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
        password=hash_password(user.password),
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

# Login API


@app.post("/api/v1/auth/login")
def login(
    user: LoginRequest,
    db: Session = Depends(get_db)
):
    existing_user = db.query(models.User).filter(
        models.User.email == user.email
    ).first()

    if not existing_user:
        return JSONResponse(
            status_code=401,
            content={
                "error": "Authentication failed",
                "message": "Invalid email or password."
            }
        )

    if not verify_password(user.password, existing_user.password):
        return JSONResponse(
            status_code=401,
            content={
                "error": "Authentication failed",
                "message": "Invalid email or password."
            }
        )

    return {
        "message": "Login successful",
        "name": existing_user.name,
        "email": existing_user.email,
        "role": existing_user.role
    }
