from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.middlewares.request_id import add_request_id
from sqlalchemy.exc import IntegrityError
from app.exceptions.handlers import integrity_error_handler

from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.admin_users import router as admin_users_router
from app.api.v1.vendors import router as vendors_router
from app.api.v1.operators import router as operators_router


app = FastAPI(
    title="QOS Platform API",
    version="1.0.0",
)


app.include_router(auth_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(admin_users_router, prefix="/api/v1")

# Middleware
app.middleware("http")(add_request_id)

# Exceptions Handlers
app.add_exception_handler(
    IntegrityError,
    integrity_error_handler
)

app.include_router(
    vendors_router,
    prefix="/api/v1",
)

app.include_router(
    operators_router,
    prefix="/api/v1",
)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/")
async def root():
    return {
        "message": "QOS Platform API is running",
        "status": "ok",
    }