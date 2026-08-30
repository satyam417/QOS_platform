from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError


async def integrity_error_handler(
    request: Request,
    exc: IntegrityError
):
    return JSONResponse(
        status_code=409,
        content={
            "error": "Database constraint violation",
            "message": "The email may already be registered."
        }
    )
