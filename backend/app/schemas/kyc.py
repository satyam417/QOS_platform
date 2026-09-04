from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class KYCStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class KYCSubmission(BaseModel):
    document_type: str
    document_reference: str


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
