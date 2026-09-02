from enum import Enum

from pydantic import BaseModel, EmailStr, Field


class RegisterRole(str, Enum):
    CUSTOMER = "customer"
    VENDOR = "vendor"
    OPERATOR = "operator"
    ADMIN = "admin"

class RegisterRequest(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=100,
    )

    email: EmailStr | None = None

    phone: str | None = Field(
        default=None,
        min_length=7,
        max_length=20,
    )

    password: str = Field(
        min_length=8,
        max_length=128,
    )

    role: RegisterRole = RegisterRole.CUSTOMER


class RegisterResponse(BaseModel):
    id: int
    name: str
    email: EmailStr | None
    phone: str | None
    role: RegisterRole
    is_verified: bool

    model_config = {
        "from_attributes": True
    }


class OTPSendRequest(BaseModel):
    email: EmailStr | None = None

    phone: str | None = Field(
        default=None,
        min_length=7,
        max_length=20,
    )


class OTPVerifyRequest(BaseModel):
    email: EmailStr | None = None

    phone: str | None = None

    otp: str = Field(
        min_length=6,
        max_length=6,
        pattern=r"^\d{6}$",
    )


class LoginRequest(BaseModel):
    identifier: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(
        min_length=20
    )

class LogoutRequest(BaseModel):
    refresh_token: str = Field(
        min_length=20
    )


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    otp: str = Field(min_length=6, max_length=6)
    new_password: str = Field(min_length=8, max_length=128)