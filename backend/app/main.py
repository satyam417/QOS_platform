from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.api.v1.auth import router as auth_router
from app.api.deps import redis_client
from app.core.database import engine


app = FastAPI(
    title="MyApp API",
    version="1.0.0",
)


app.include_router(auth_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(admin_users_router, prefix="/api/v1")


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