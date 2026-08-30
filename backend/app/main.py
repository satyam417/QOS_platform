from fastapi import FastAPI
from sqlalchemy.exc import IntegrityError

from app.api.v1.auth import router as auth_router
from app.api.v1.health import router as health_router
from app.middleware.request_id import add_request_id

from app.exceptions.handlers import integrity_error_handler


app = FastAPI(
    title="QOS Platform API",
    version="1.0.0",
)


app.include_router(
    auth_router,
    prefix="/api/v1",
)

app.include_router(
    health_router
)

# Middleware
app.middleware("http")(add_request_id)

# Exceptions Handlers
app.add_exception_handler(
    IntegrityError,
    integrity_error_handler
)


@app.get("/")
async def root():
    return {
        "message": "QOS Platform API is running",
        "status": "ok"
    }
