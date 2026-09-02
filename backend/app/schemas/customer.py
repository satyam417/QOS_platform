from pydantic import BaseModel, Field


class CustomerProfileUpdate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: str | None = None
    phone: str | None = None


class CustomerProfileResponse(BaseModel):
    user_id: int
    name: str
    email: str | None
    phone: str | None
    role: str
    is_verified: bool


class AddressCreate(BaseModel):
    address_line1: str = Field(..., min_length=1, max_length=255)
    address_line2: str | None = Field(None, max_length=255)
    city: str = Field(..., max_length=100)
    state: str = Field(..., max_length=100)
    postal_code: str = Field(..., max_length=20)
    country: str = Field(default="India", max_length=100)
    is_default: bool = False


class AddressResponse(BaseModel):
    id: int
    user_id: int
    address_line1: str
    address_line2: str | None
    city: str
    state: str
    postal_code: str
    country: str
    is_default: bool

    class Config:
        from_attributes = True