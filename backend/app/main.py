from fastapi import FastAPI

from app.api.v1.auth import router as auth_router

from app.api.v1.customer import router as customer_router

from app.models.address import Address

app = FastAPI(
    title="MyApp API",
    version="1.0.0",
)


app.include_router(
    auth_router,
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

# customer Registeration and OTP verification service

app = FastAPI(
    title="QOS Platform API",
)


app.include_router(auth_router)

app.include_router(customer_router)

@app.get("/")
def root():
    return {
        "message": "QOS Platform API is running"
    }