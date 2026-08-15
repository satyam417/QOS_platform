from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import uuid

from database import engine, Base, SessionLocal
import models


app = FastAPI(title="QOS Platform API")


# Request ID middleware
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())

    response = await call_next(request)

    response.headers["X-Request-ID"] = request_id

    return response


# Database error handler
@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    return JSONResponse(
        status_code=409,
        content={
            "error": "Database constraint violation",
            "message": "The email may already be registered."
        }
    )


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