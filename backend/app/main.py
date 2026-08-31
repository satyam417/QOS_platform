from fastapi import FastAPI

from app.api.v1.auth import router as auth_router
from app.api.v1.vendors import router as vendors_router
from app.api.v1.operators import router as operators_router


app = FastAPI(
    title="MyApp API",
    version="1.0.0",
)


app.include_router(
    auth_router,
    prefix="/api/v1",
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
    return {
        "status": "ok"
    }

@app.get("/")
async def root():
    return {
        "message": "QOS Platform API is running",
        "status": "ok"
    }