from fastapi import FastAPI

from app.api.v1.auth import router as auth_router
from app.api.v1.categories import router as categories_router
from app.api.v1.services import router as services_router


app = FastAPI(
    title="MyApp API",
    version="1.0.0",
)


app.include_router(
    auth_router,
    prefix="/api/v1",
)

app.include_router(
    categories_router,
    prefix="/api/v1",
)

app.include_router(
    services_router,
    prefix="/api/v1",
)


@app.get("/health")
async def health():
    return {
        "status": "ok"
    }

@app.get("/")
async def root():
    return {
        "message": "QOS Platform API is running",
        "status": "ok"
    }