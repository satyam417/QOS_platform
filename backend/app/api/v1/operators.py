from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.core.database import get_db
from app.models.user import User, UserRole
from app.models.vendor import VendorProfile, KYCStatus
from app.schemas.vendor import VendorProfileResponse

router = APIRouter(prefix="/operators", tags=["Operators"])


@router.get("/vendors", response_model=list[VendorProfileResponse])
def list_vendors(
    _admin: Annotated[User, Depends(require_roles(UserRole.ADMIN))],
    db: Annotated[Session, Depends(get_db)],
    status_filter: KYCStatus | None = None,
):
    query = select(VendorProfile)
    if status_filter:
        query = query.where(VendorProfile.kyc_status == status_filter)

    return db.scalars(query).all()