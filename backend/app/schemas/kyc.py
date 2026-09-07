from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class KYCStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class KYCSubmission(BaseModel):
    document_type: str = Field(
        ...,
        description="e.g. 'gst_certificate', 'pan_card', 'business_license'",
    )
    document_reference: str = Field(
        ...,
        description="File name or reference — actual storage TBD pending S3/MinIO contract",
    )


class KYCStatusResponse(BaseModel):
    vendor_id: int
    kyc_status: KYCStatus
    document_type: str
    document_reference: str
    submitted_at: datetime | None = None


class KYCResponse(BaseModel):
    id: int
    vendor_id: int
    document_type: str
    document_path: str
    status: KYCStatus
    rejection_reason: str | None = None

    model_config = {
        "from_attributes": True
    }


class KYCReviewRequest(BaseModel):
    status: KYCStatus
    rejection_reason: str | None = None