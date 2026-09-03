from fastapi import FastAPI

from sqlalchemy.exc import IntegrityError

from app.middlewares.request_id import add_request_id
from app.exceptions.handlers import integrity_error_handler

from app.api.v1.auth import router as auth_router
from app.api.v1.portal import router as portal_router
from app.api.v1.users import router as users_router
from app.api.v1.kyc import router as kyc_router
from app.api.v1.admin_users import router as admin_users_router
from app.api.v1.customer import router as customer_router
from app.api.v1.vendors import router as vendors_router
from app.api.v1.operators import router as operators_router
from app.api.v1.categories import router as categories_router
from app.api.v1.services import router as services_router


app = FastAPI(
    title="QOS Platform API",
    version="1.0.0",
)


# =========================================================
# API ROUTERS
# =========================================================

app.include_router(
    auth_router,
    prefix="/api/v1",
)

app.include_router(
    users_router,
    prefix="/api/v1",
)

app.include_router(
    admin_users_router,
    prefix="/api/v1",
)

app.include_router(
    portal_router,
    prefix="/api/v1",
)

app.include_router(
    kyc_router,
    prefix="/api/v1",
)

app.include_router(
    customer_router,
)

app.include_router(
    vendors_router,
    prefix="/api/v1",
)

app.include_router(
    operators_router,
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


# =========================================================
# MIDDLEWARE
# =========================================================

app.middleware("http")(add_request_id)


# =========================================================
# EXCEPTION HANDLERS
# =========================================================

app.add_exception_handler(
    IntegrityError,
    integrity_error_handler,
)


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/health")
async def health():
    return {
        "status": "ok",
    }


# =========================================================
# ROOT
# =========================================================

@app.get("/")
async def root():
    return {
        "message": "QOS Platform API is running",
        "status": "ok",
    }