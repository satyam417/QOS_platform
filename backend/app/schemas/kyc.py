from enum import Enum

from pydantic import BaseModel


class KYCStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


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