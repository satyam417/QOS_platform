from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User, UserRole


security = HTTPBearer()

redis_client = Redis.from_url(
    settings.REDIS_URL,
    decode_responses=True,
)


def get_redis() -> Redis:
    return redis_client


def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials,
        Depends(security),
    ],
    db: Annotated[
        Session,
        Depends(get_db),
    ],
) -> User:

    try:
        payload = decode_access_token(
            credentials.credentials
        )

        user_id = payload.get("sub")

        if not user_id:
            raise ValueError()

    except (ValueError, TypeError):

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    user = db.scalar(
        select(User).where(
            User.id == int(user_id)
        )
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    return user


def require_roles(*roles: UserRole):

    def role_checker(
        current_user: Annotated[
            User,
            Depends(get_current_user),
        ],
    ) -> User:

        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )

        return current_user

    return role_checker