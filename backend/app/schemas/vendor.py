from datetime import datetime

from pydantic import BaseModel, Field


class VendorProfileCreate(BaseModel):
    business_name: str = Field(..., min_length=2, max_length=150)
    business_type: str | None = None
    gst_number: str | None = None
    bank_account_number: str | None = None
    bank_ifsc: str | None = None


class VendorProfileUpdate(BaseModel):
    business_name: str | None = Field(None, min_length=2, max_length=150)
    business_type: str | None = None
    gst_number: str | None = None
    bank_account_number: str | None = None
    bank_ifsc: str | None = None


class VendorProfileResponse(BaseModel):
    id: int
    user_id: int
    business_name: str
    business_type: str | None
    gst_number: str | None
    kyc_status: str
    created_at: datetime

    class Config:
        from_attributes = True