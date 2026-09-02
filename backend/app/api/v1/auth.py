from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import (
    get_current_user,
    get_redis,
)
from app.core.database import get_db
from app.core.security import hash_password

from app.models.user import User, UserRole

from app.schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    LogoutRequest,
    OTPVerifyRequest,
    OTPSendRequest,
    RefreshTokenRequest,
    RegisterRequest,
    RegisterResponse,
    ResetPasswordRequest,
    TokenResponse,
)

from app.services.auth import (
    authenticate_user,
    create_tokens,
    logout,
    logout_all,
    refresh_access_token,
    start_password_reset,
    reset_password,
)

from app.services.otp import OTPService


# =========================================================
# ROUTER
# =========================================================

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


# =========================================================
# REFRESH TOKEN
# =========================================================

@router.post(
    "/refresh",
    response_model=TokenResponse,
)
def refresh_token(
    request: RefreshTokenRequest,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
):
    result = refresh_access_token(
        request.refresh_token,
        db,
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    # refresh_access_token returns a tuple
    access_token, refresh_token_value = result

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token_value,
    )


# =========================================================
# REGISTER
# =========================================================

@router.post(
    "/register",
    response_model=RegisterResponse,
)
def register(
    request: RegisterRequest,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
):
    email = (
        request.email.lower().strip()
        if request.email
        else None
    )

    phone = (
        request.phone.strip()
        if request.phone
        else None
    )

    if not email and not phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or phone is required",
        )

    # Supported roles:
    # customer, vendor, operator, admin
    role = UserRole(request.role.value)

    # -----------------------------------------------------
    # Check email
    # -----------------------------------------------------

    if email:
        existing = db.scalar(
            select(User).where(
                User.email == email
            )
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email is already registered",
            )

    # -----------------------------------------------------
    # Check phone
    # -----------------------------------------------------

    if phone:
        existing = db.scalar(
            select(User).where(
                User.phone == phone
            )
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Phone is already registered",
            )

    # -----------------------------------------------------
    # Create user
    # -----------------------------------------------------

    user = User(
        name=request.name.strip(),
        email=email,
        phone=phone,
        password_hash=hash_password(
            request.password
        ),
        role=role.value,
        is_active=True,
        is_verified=False,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


# =========================================================
# SEND OTP
# =========================================================

@router.post(
    "/otp/send",
)
async def send_otp(
    request: OTPSendRequest,
    redis: Redis = Depends(get_redis),
):
    identifier = (
        request.email.lower().strip()
        if request.email
        else (
            request.phone.strip()
            if request.phone
            else None
        )
    )

    if not identifier:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or phone is required",
        )

    otp_service = OTPService(redis)

    await otp_service.send_otp(identifier)

    return {
        "message": "OTP sent successfully"
    }


# =========================================================
# VERIFY OTP
# =========================================================

@router.post(
    "/otp/verify",
    response_model=TokenResponse,
)
async def verify_otp(
    request: OTPVerifyRequest,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    redis: Redis = Depends(get_redis),
):
    identifier = (
        request.email.lower().strip()
        if request.email
        else (
            request.phone.strip()
            if request.phone
            else None
        )
    )

    if not identifier:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or phone is required",
        )

    otp_service = OTPService(redis)

    valid = await otp_service.verify_otp(
        identifier,
        request.otp,
    )

    if not valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP",
        )

    # -----------------------------------------------------
    # Find user
    # -----------------------------------------------------

    user = db.scalar(
        select(User).where(
            (User.email == identifier)
            | (User.phone == identifier)
        )
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # -----------------------------------------------------
    # Verify account
    # -----------------------------------------------------

    user.is_verified = True

    db.commit()

    # -----------------------------------------------------
    # Create tokens
    # -----------------------------------------------------

    access_token, refresh_token_value = create_tokens(
        user,
        db,
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token_value,
    )


# =========================================================
# LOGIN
# =========================================================

@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    request: LoginRequest,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
):
    # IMPORTANT:
    # authenticate_user expects:
    # identifier, password, db
    #
    # Do NOT pass db as the first argument.

    authenticated_user = authenticate_user(
        request.identifier,
        request.password,
        db,
    )

    if not authenticated_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    if not authenticated_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive",
        )

    if not authenticated_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is not verified",
        )

    access_token, refresh_token_value = create_tokens(
        authenticated_user,
        db,
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token_value,
    )


# =========================================================
# LOGOUT
# =========================================================

@router.post(
    "/logout",
)
def logout_user(
    request: LogoutRequest,
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    db: Annotated[
        Session,
        Depends(get_db),
    ],
):
    logout(
        refresh_token=request.refresh_token,
        user_id=current_user.id,
        db=db,
    )

    return {
        "message": "Logged out successfully"
    }


# =========================================================
# LOGOUT ALL DEVICES
# =========================================================

@router.post(
    "/logout-all",
)
def logout_all_devices(
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    db: Annotated[
        Session,
        Depends(get_db),
    ],
):
    revoked_count = logout_all(
        user_id=current_user.id,
        db=db,
    )

    return {
        "message": "Logged out from all devices",
        "sessions_revoked": revoked_count,
    }


# =========================================================
# FORGOT PASSWORD
# =========================================================

@router.post(
    "/password/forgot",
    status_code=status.HTTP_202_ACCEPTED,
)
async def forgot_password(
    payload: ForgotPasswordRequest,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    redis: Redis = Depends(get_redis),
):
    await start_password_reset(
        db=db,
        redis=redis,
        email=payload.email,
    )

    return {
        "message": (
            "If an account exists, "
            "a password reset OTP has been sent."
        )
    }


# =========================================================
# RESET PASSWORD
# =========================================================

@router.post(
    "/password/reset",
    status_code=status.HTTP_200_OK,
)
async def password_reset(
    payload: ResetPasswordRequest,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    redis: Redis = Depends(get_redis),
):
    try:
        await reset_password(
            db=db,
            redis=redis,
            email=payload.email,
            otp=payload.otp,
            new_password=payload.new_password,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    return {
        "message": "Password reset successfully."
    }