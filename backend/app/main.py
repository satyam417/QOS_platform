from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy import text

from sqlalchemy.exc import IntegrityError
from app.middleware.request_id import add_request_id
from app.exceptions.handlers import integrity_error_handler

from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.admin_users import router as admin_users_router
from app.api.v1.vendors import router as vendors_router
from app.api.v1.operators import router as operators_router
from app.api.v1.categories import router as categories_router
from app.api.v1.services import router as services_router
from app.api.deps import redis_client
from app.core.database import engine


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
    categories_router,
    prefix="/api/v1",
)

app.include_router(
    operators_router,
    services_router,
    prefix="/api/v1",
)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/ready")
async def ready():
    postgres_ok = False
    redis_ok = False

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        postgres_ok = True
    except Exception:
        pass

    try:
        await redis_client.ping()
        redis_ok = True
    except Exception:
        pass

    if postgres_ok and redis_ok:
        return {
            "status": "ready",
            "postgres": "ok",
            "redis": "ok",
        }

    return JSONResponse(
        status_code=503,
        content={
            "status": "not_ready",
            "postgres": "ok" if postgres_ok else "error",
            "redis": "ok" if redis_ok else "error",
        },
    )


@app.get("/")
async def root():
    return {
        "message": "QOS Platform API is running",
        "status": "ok"
    }
