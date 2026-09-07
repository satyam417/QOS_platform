from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.core.database import get_db
from app.models.user import User, UserRole
from app.models.vendor import VendorProfile, KYCStatus
from app.schemas.vendor import VendorProfileCreate, VendorProfileUpdate, VendorProfileResponse
from app.schemas.kyc import KYCSubmission, KYCResponse

router = APIRouter(prefix="/vendors", tags=["Vendors"])


@router.post("/profile", response_model=VendorProfileResponse, status_code=status.HTTP_201_CREATED)
def create_vendor_profile(
    payload: VendorProfileCreate,
    current_user: Annotated[User, Depends(require_roles(UserRole.VENDOR))],
    db: Annotated[Session, Depends(get_db)],
):
    existing = db.scalar(select(VendorProfile).where(
        VendorProfile.user_id == current_user.id))
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Vendor profile already exists")

    profile = VendorProfile(
        user_id=current_user.id,
        business_name=payload.business_name,
        business_type=payload.business_type,
        gst_number=payload.gst_number,
        bank_account_number=payload.bank_account_number,
        bank_ifsc=payload.bank_ifsc,
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@router.get("/me", response_model=VendorProfileResponse)
def get_own_vendor_profile(
    current_user: Annotated[User, Depends(require_roles(UserRole.VENDOR))],
    db: Annotated[Session, Depends(get_db)],
):
    profile = db.scalar(select(VendorProfile).where(
        VendorProfile.user_id == current_user.id))
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Vendor profile not found")
    return profile


@router.put("/me", response_model=VendorProfileResponse)
def update_own_vendor_profile(
    payload: VendorProfileUpdate,
    current_user: Annotated[User, Depends(require_roles(UserRole.VENDOR))],
    db: Annotated[Session, Depends(get_db)],
):
    profile = db.scalar(select(VendorProfile).where(
        VendorProfile.user_id == current_user.id))
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Vendor profile not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)
    return profile


@router.get("/{vendor_id}", response_model=VendorProfileResponse)
def get_vendor_by_id(
    vendor_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    profile = db.scalar(select(VendorProfile).where(
        VendorProfile.id == vendor_id))
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found")

    is_self = profile.user_id == current_user.id
    is_privileged = current_user.role.value == "admin"
    if not (is_self or is_privileged):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")

    return profile


@router.post("/me/kyc", response_model=KYCResponse)
def submit_kyc(
    payload: KYCSubmission,
    current_user: Annotated[User, Depends(require_roles(UserRole.VENDOR))],
    db: Annotated[Session, Depends(get_db)],
):
    profile = db.scalar(select(VendorProfile).where(
        VendorProfile.user_id == current_user.id))
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Vendor profile not found")

    if profile.kyc_status.value == "approved":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="KYC already approved")

    profile.kyc_document_type = payload.document_type
    profile.kyc_document_reference = payload.document_reference
    profile.kyc_submitted_at = datetime.now(timezone.utc)
    profile.kyc_status = KYCStatus.PENDING

    db.commit()
    db.refresh(profile)

    return {
        "vendor_id": profile.id,
        "kyc_status": profile.kyc_status.value,
        "document_type": profile.kyc_document_type,
        "document_reference": profile.kyc_document_reference,
        "submitted_at": profile.kyc_submitted_at,
    }
