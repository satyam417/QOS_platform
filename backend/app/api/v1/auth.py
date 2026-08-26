from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_redis
from app.core.database import get_db
from app.core.security import hash_password
from app.models.user import User, UserRole
from app.schemas.auth import (
    LoginRequest,
    OTPVerifyRequest,
    OTPSendRequest,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
)
from app.services.auth import (
    authenticate_user,
    create_tokens,
)
from app.services.otp import OTPService
from app.schemas.auth import (
    LoginRequest,
    OTPVerifyRequest,
    OTPSendRequest,
    RefreshTokenRequest,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
)
from app.services.auth import (
    authenticate_user,
    create_tokens,
    logout,
    logout_all,
    refresh_access_token,
)
from app.api.deps import get_current_user, get_redis
from app.schemas.auth import (
    LoginRequest,
    LogoutRequest,
    OTPVerifyRequest,
    OTPSendRequest,
    RefreshTokenRequest,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
)

from fastapi import APIRouter, Depends, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.auth import (
    ForgotPasswordRequest,
    ResetPasswordRequest,
)
from app.services.auth import (
    start_password_reset,
    reset_password,
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

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
        refresh_token=request.refresh_token,
        db=db,
    )

    if not result:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    access_token, new_refresh_token = result

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
    )


#Register

@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
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

    # Never allow public registration as admin.
    role = UserRole(request.role.value)

    if role == UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin registration is not allowed",
        )

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

    user = User(
        name=request.name.strip(),
        email=email,
        phone=phone,
        password_hash=hash_password(
            request.password
        ),
        role=role,
        is_active=True,
        is_verified=False,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user

#Send OTP
@router.post(
    "/otp/send",
)
async def send_otp(
    request: OTPSendRequest,
    redis=Depends(get_redis),
):

    identifier = (
        request.email.lower().strip()
        if request.email
        else request.phone
    )

    if not identifier:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or phone is required",
        )

    otp_service = OTPService(redis)

    await otp_service.send_otp(
        identifier
    )

    return {
        "message": "OTP sent successfully"
    }

#Verify OPT

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
    redis=Depends(get_redis),
):

    identifier = (
        request.email.lower().strip()
        if request.email
        else request.phone
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

    user.is_verified = True

    db.commit()

    access_token, refresh_token = create_tokens(
        user,
        db,
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )

#Login

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

    user = authenticate_user(
        identifier=request.identifier,
        password=request.password,
        db=db,
    )

    if not user:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    if not user.is_active:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive",
        )

    if not user.is_verified:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is not verified",
        )

    access_token, refresh_token = create_tokens(
        user,
        db,
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )

#Logout
@router.post("/logout")
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

    success = logout(
        refresh_token=request.refresh_token,
        user_id=current_user.id,
        db=db,
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or already revoked refresh token",
        )

    return {
        "message": "Logged out successfully"
    }

#Logout All 
@router.post("/logout-all")
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

@router.post(
    "/password/forgot",
    status_code=status.HTTP_202_ACCEPTED,
)
async def forgot_password(
    payload: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    await start_password_reset(
        db=db,
        redis=redis,
        email=payload.email,
    )

    return {
        "message": "If an account exists, a password reset OTP has been sent."
    }

@router.post(
    "/password/reset",
    status_code=status.HTTP_200_OK,
)
async def password_reset(
    payload: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    await reset_password(
        db=db,
        redis=redis,
        email=payload.email,
        otp=payload.otp,
        new_password=payload.new_password,
    )

    return {
        "message": "Password reset successfully."
    }

# Customer registration and OTP verification service

from app.core.database import get_db
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    OTPRequest,
    OTPVerifyRequest,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
)
from app.services.otp import (
    create_otp,
    verify_otp,
)


router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentication"],
)


# --------------------------------------------------
# REGISTER
# --------------------------------------------------

@router.post(
    "/register",
    response_model=RegisterResponse,
)
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db),
):
    existing_email = (
        db.query(User)
        .filter(User.email == request.email)
        .first()
    )

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    existing_phone = (
        db.query(User)
        .filter(User.phone == request.phone)
        .first()
    )

    if existing_phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number already registered",
        )

    user = User(
        name=request.name,
        email=request.email,
        phone=request.phone,
        password_hash=hash_password(request.password),
        is_verified=False,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # Generate OTP
    create_otp(request.email)

    return RegisterResponse(
        message="Registration successful. OTP sent.",
        user_id=user.id,
        otp_required=True,
    )


# --------------------------------------------------
# SEND OTP
# --------------------------------------------------

@router.post("/otp/send")
def send_otp(
    request: OTPRequest,
):
    create_otp(request.contact)

    return {
        "message": "OTP sent successfully"
    }


# --------------------------------------------------
# VERIFY OTP
# --------------------------------------------------

@router.post("/otp/verify")
def verify_customer_otp(
    request: OTPVerifyRequest,
    db: Session = Depends(get_db),
):

    if not verify_otp(
        request.contact,
        request.otp,
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP",
        )

    user = (
        db.query(User)
        .filter(User.email == request.contact)
        .first()
    )

    if not user:
        user = (
            db.query(User)
            .filter(User.phone == request.contact)
            .first()
        )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    user.is_verified = True

    db.commit()

    return {
        "message": "OTP verified successfully",
        "user_id": user.id,
    }


# --------------------------------------------------
# LOGIN
# --------------------------------------------------

@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db),
):

    user = (
        db.query(User)
        .filter(User.email == request.email)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not verify_password(
        request.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your OTP first",
        )

    # Change this to your actual secret key/config.
    secret_key = "CHANGE_THIS_TO_YOUR_SECRET_KEY"

    access_token = create_access_token(
        user.id,
        secret_key,
    )

    refresh_token = create_refresh_token(
        user.id,
        secret_key,
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )