from datetime import datetime, timedelta, timezone
import hashlib
import secrets

from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.services.otp import OTPService


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def hash_refresh_token(token: str) -> str:
    """
    Hash the refresh token before storing it in the database.
    """
    return hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()


def generate_refresh_token() -> str:
    """
    Generate a secure random refresh token.
    """
    return secrets.token_urlsafe(64)


# =========================================================
# AUTHENTICATE USER
# =========================================================

def authenticate_user(
    identifier: str,
    password: str,
    db: Session,
):
    """
    Authenticate a user using email or phone.
    """

    identifier = identifier.strip()

    # Try email first
    user = db.scalar(
        select(User).where(
            User.email == identifier.lower()
        )
    )

    # If email is not found, try phone
    if user is None:
        user = db.scalar(
            select(User).where(
                User.phone == identifier
            )
        )

    # User doesn't exist
    if user is None:
        return None

    # Check password
    if not verify_password(
        password,
        user.password_hash,
    ):
        return None

    return user


# =========================================================
# CREATE TOKENS
# =========================================================

def create_tokens(
    user: User,
    db: Session,
):
    """
    Create access token and refresh token.
    """

    # Get role value
    role = (
        user.role.value
        if hasattr(user.role, "value")
        else str(user.role)
    )

    # Create access token
    access_token = create_access_token(
        user_id=user.id,
        role=role,
    )

    # Generate refresh token
    refresh_token = generate_refresh_token()

    # Hash refresh token
    token_hash = hash_refresh_token(
        refresh_token
    )

    # Calculate expiration
    now = datetime.now(timezone.utc)

    expires_at = (
        now
        + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
    )

    # Save refresh token
    stored_token = RefreshToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=expires_at,
        revoked_at=None,
    )

    db.add(stored_token)
    db.commit()
    db.refresh(stored_token)

    return access_token, refresh_token


# =========================================================
# REFRESH ACCESS TOKEN
# =========================================================

def refresh_access_token(
    refresh_token: str,
    db: Session,
):
    """
    Validate refresh token and create a new token pair.
    """

    token_hash = hash_refresh_token(
        refresh_token
    )

    # Find stored refresh token
    stored_token = db.scalar(
        select(RefreshToken).where(
            RefreshToken.token_hash == token_hash
        )
    )

    if stored_token is None:
        return None

    # Check if revoked
    if stored_token.revoked_at is not None:
        return None

    # Current UTC time
    now = datetime.now(timezone.utc)

    expires_at = stored_token.expires_at

    # SQLite may return naive datetime
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(
            tzinfo=timezone.utc
        )

    # Check expiration
    if expires_at <= now:

        stored_token.revoked_at = now

        db.commit()

        return None

    # Find user
    user = db.scalar(
        select(User).where(
            User.id == stored_token.user_id
        )
    )

    if user is None:
        return None

    # Check account status
    if not user.is_active:
        return None

    # Revoke old refresh token
    stored_token.revoked_at = now

    db.commit()

    # Generate new token pair
    new_access_token, new_refresh_token = create_tokens(
        user,
        db,
    )

    return (
        new_access_token,
        new_refresh_token,
    )


# =========================================================
# LOGOUT
# =========================================================

def logout(
    refresh_token: str,
    user_id: int,
    db: Session,
):
    """
    Revoke one refresh token.
    """

    token_hash = hash_refresh_token(
        refresh_token
    )

    stored_token = db.scalar(
        select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.user_id == user_id,
        )
    )

    if stored_token is None:
        return False

    if stored_token.revoked_at is not None:
        return False

    stored_token.revoked_at = (
        datetime.now(timezone.utc)
    )

    db.commit()

    return True


# =========================================================
# LOGOUT ALL DEVICES
# =========================================================

def logout_all(
    user_id: int,
    db: Session,
):
    """
    Revoke all refresh tokens belonging to a user.
    """

    tokens = db.scalars(
        select(RefreshToken).where(
            RefreshToken.user_id == user_id,
            RefreshToken.revoked_at.is_(None),
        )
    ).all()

    if not tokens:
        return 0

    now = datetime.now(timezone.utc)

    count = 0

    for token in tokens:
        token.revoked_at = now
        count += 1

    db.commit()

    return count


# =========================================================
# START PASSWORD RESET
# =========================================================

async def start_password_reset(
    db: Session,
    redis: Redis,
    email: str,
):
    """
    Generate and store a password-reset OTP.

    For security, this function does not reveal whether
    the email exists.
    """

    email = email.lower().strip()

    # Find user
    user = db.scalar(
        select(User).where(
            User.email == email
        )
    )

    # If user doesn't exist, simply return.
    # The API will still return a generic message.
    if user is None:
        return

    # Create OTP service
    otp_service = OTPService(redis)

    # Generate/store OTP
    await otp_service.send_otp(email)

    return


# =========================================================
# RESET PASSWORD
# =========================================================

async def reset_password(
    db: Session,
    redis: Redis,
    email: str,
    otp: str,
    new_password: str,
):
    """
    Verify password-reset OTP and update password.
    """

    email = email.lower().strip()

    # Find user
    user = db.scalar(
        select(User).where(
            User.email == email
        )
    )

    if user is None:
        raise ValueError(
            "Invalid email or OTP"
        )

    # Verify OTP
    otp_service = OTPService(redis)

    valid = await otp_service.verify_otp(
        email,
        otp,
    )

    if not valid:
        raise ValueError(
            "Invalid or expired OTP"
        )

    # Hash new password
    user.password_hash = hash_password(
        new_password
    )

    db.commit()

    return True