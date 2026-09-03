from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError


async def integrity_error_handler(
    request: Request,
    exc: IntegrityError,
):
    print("INTEGRITY ERROR:", exc)

    return JSONResponse(
        status_code=409,
        content={
            "error": "Database constraint violation",
            "message": str(exc.orig),
        },
    )