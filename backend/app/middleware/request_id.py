import uuid
from fastapi import Request


async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())

    response = await call_next(request)

    response.headers["X-Request-ID"] = request_id

    return response
