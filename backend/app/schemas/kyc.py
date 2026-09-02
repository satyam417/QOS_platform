from datetime import datetime

from pydantic import BaseModel, Field


class KYCSubmission(BaseModel):
    document_type: str = Field(..., description="e.g. 'gst_certificate', 'pan_card', 'business_license'")
    document_reference: str = Field(..., description="File name or reference — actual storage TBD pending S3/MinIO contract")


class KYCStatusResponse(BaseModel):
    vendor_id: int
    kyc_status: str
    document_type: str | None
    document_reference: str | None
    submitted_at: datetime | None

    class Config:
        from_attributes = True