from fastapi import FastAPI

from app.api.v1.auth import router as auth_router
from app.api.v1.portal import router as portal_router
from app.api.v1.users import router as users_router
from app.api.v1.kyc import router as kyc_router


app = FastAPI(
    title="MyApp API",
    version="1.0.0",
)


app.include_router(
    auth_router,
    prefix="/api/v1",
)

app.include_router(
    portal_router,
    prefix="/api/v1",
)

app.include_router(
    users_router,
    prefix="/api/v1",
)

app.include_router(
    kyc_router,
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