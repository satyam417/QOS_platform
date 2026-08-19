from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_refresh_token

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)
from app.models.refresh_token import RefreshToken
from app.models.user import User


def create_tokens(
    user: User,
    db: Session,
) -> tuple[str, str]:

    access_token = create_access_token(
        user_id=user.id,
        role=user.role.value,
    )

    refresh_token = create_refresh_token()

    refresh_token_record = RefreshToken(
        user_id=user.id,
        token_hash=hash_refresh_token(
            refresh_token
        ),
        expires_at=(
            datetime.now(timezone.utc)
            + timedelta(
                days=settings.REFRESH_TOKEN_EXPIRE_DAYS
            )
        ),
    )

    db.add(refresh_token_record)
    db.commit()

    return access_token, refresh_token


def authenticate_user(
    identifier: str,
    password: str,
    db: Session,
) -> User | None:

    identifier = identifier.strip().lower()

    user = db.scalar(
        select(User).where(
            (User.email == identifier)
            | (User.phone == identifier)
        )
    )

    if not user:
        return None

    if not verify_password(
        password,
        user.password_hash,
    ):
        return None

    return user


def refresh_access_token(
    refresh_token: str,
    db: Session,
) -> tuple[str, str] | None:

    token_hash = hash_refresh_token(
        refresh_token
    )

    stored_token = db.scalar(
        select(RefreshToken).where(
            RefreshToken.token_hash == token_hash
        )
    )

    if not stored_token:
        return None

    now = datetime.now(timezone.utc)

    # Token has already been revoked.
    if stored_token.revoked_at is not None:
        return None

    # Token has expired.
    if stored_token.expires_at <= now:

        stored_token.revoked_at = now
        db.commit()

        return None

    user = db.get(
        User,
        stored_token.user_id,
    )

    if not user:
        return None

    if not user.is_active:
        return None

    if not user.is_verified:
        return None

    # Rotate old refresh token.
    stored_token.revoked_at = now

    # Create new tokens.
    new_access_token = create_access_token(
        user_id=user.id,
        role=user.role.value,
    )

    new_refresh_token = create_refresh_token()

    new_refresh_token_record = RefreshToken(
        user_id=user.id,
        token_hash=hash_refresh_token(
            new_refresh_token
        ),
        expires_at=(
            now
            + timedelta(
                days=settings.REFRESH_TOKEN_EXPIRE_DAYS
            )
        ),
    )

    db.add(new_refresh_token_record)
    db.commit()

    return (
        new_access_token,
        new_refresh_token,
    )

def logout(
    refresh_token: str,
    user_id: int,
    db: Session,
) -> bool:

    token_hash = hash_refresh_token(
        refresh_token
    )

    stored_token = db.scalar(
        select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.user_id == user_id,
        )
    )

    if not stored_token:
        return False

    if stored_token.revoked_at is not None:
        return False

    stored_token.revoked_at = datetime.now(
        timezone.utc
    )

    db.commit()

    return True

def logout_all(
    user_id: int,
    db: Session,
) -> int:

    tokens = db.scalars(
        select(RefreshToken).where(
            RefreshToken.user_id == user_id,
            RefreshToken.revoked_at.is_(None),
        )
    ).all()

    now = datetime.now(timezone.utc)

    for token in tokens:
        token.revoked_at = now

    db.commit()

    return len(tokens)