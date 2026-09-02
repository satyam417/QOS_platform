from typing import Annotated
from pathlib import Path
from uuid import uuid4

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.kyc import KYC, KYCStatus
from app.models.user import User, UserRole
from app.schemas.kyc import (
    KYCResponse,
    KYCReviewRequest,
)


router = APIRouter(
    prefix="/kyc",
    tags=["KYC"],
)


# ============================================================
# 1. VENDOR - UPLOAD KYC DOCUMENT
# ============================================================

@router.post(
    "/upload",
    response_model=KYCResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_kyc(
    document_type: str,
    document: UploadFile = File(...),
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ] = None,
    db: Annotated[
        Session,
        Depends(get_db),
    ] = None,
):

    # Only vendors can upload KYC
    if current_user.role != UserRole.VENDOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only vendors can upload KYC documents",
        )

    # Allowed file types
    allowed_types = {
        "application/pdf",
        "image/jpeg",
        "image/png",
    }

    if document.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF, JPG, and PNG files are allowed",
        )

    # Create upload directory
    upload_dir = Path("uploads") / "kyc"

    upload_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Get original filename
    original_filename = document.filename or "document"

    # Get file extension
    extension = Path(original_filename).suffix.lower()

    # Generate unique filename
    unique_filename = f"{uuid4()}{extension}"

    # Final file path
    file_path = upload_dir / unique_filename

    # Save uploaded file
    with open(file_path, "wb") as buffer:

        while True:

            chunk = await document.read(1024 * 1024)

            if not chunk:
                break

            buffer.write(chunk)

    # Create KYC database record
    kyc = KYC(
        vendor_id=current_user.id,
        document_type=document_type,
        document_path=str(file_path),
        status=KYCStatus.PENDING,
    )

    db.add(kyc)

    db.commit()

    db.refresh(kyc)

    return kyc


# ============================================================
# 2. VENDOR - VIEW MY KYC DOCUMENTS
# ============================================================

@router.get(
    "/my",
    response_model=list[KYCResponse],
)
def get_my_kyc(
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    db: Annotated[
        Session,
        Depends(get_db),
    ],
):

    # Only vendors can view their KYC
    if current_user.role != UserRole.VENDOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only vendors can view their KYC documents",
        )

    # Get KYC records belonging to current vendor
    kycs = (
        db.query(KYC)
        .filter(
            KYC.vendor_id == current_user.id
        )
        .order_by(
            KYC.id.desc()
        )
        .all()
    )

    return kycs


# ============================================================
# 3. OPERATOR - VIEW ALL KYC DOCUMENTS
# ============================================================

@router.get(
    "/all",
    response_model=list[KYCResponse],
)
def get_all_kyc(
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    db: Annotated[
        Session,
        Depends(get_db),
    ],
):

    # Only operators can view all KYC
    if current_user.role != UserRole.OPERATOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only operators can view all KYC documents",
        )

    # Get all KYC records
    kycs = (
        db.query(KYC)
        .order_by(
            KYC.id.desc()
        )
        .all()
    )

    return kycs


# ============================================================
# 4. OPERATOR - APPROVE OR REJECT KYC
# ============================================================

@router.patch(
    "/{kyc_id}/review",
    response_model=KYCResponse,
)
def review_kyc(
    kyc_id: int,
    review: KYCReviewRequest,
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    db: Annotated[
        Session,
        Depends(get_db),
    ],
):

    # Only operators can review KYC
    if current_user.role != UserRole.OPERATOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only operators can review KYC documents",
        )

    # Find KYC record
    kyc = (
        db.query(KYC)
        .filter(
            KYC.id == kyc_id
        )
        .first()
    )

    # KYC not found
    if kyc is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="KYC record not found",
        )

    # If rejecting, rejection reason is required
    if (
        review.status == KYCStatus.REJECTED
        and not review.rejection_reason
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rejection reason is required",
        )

    # If approved, remove rejection reason
    if review.status == KYCStatus.APPROVED:

        kyc.rejection_reason = None

    # If rejected, save rejection reason
    else:

        kyc.rejection_reason = (
            review.rejection_reason
        )

    # Update KYC status
    kyc.status = review.status

    # Save changes
    db.commit()

    db.refresh(kyc)

    return kyc