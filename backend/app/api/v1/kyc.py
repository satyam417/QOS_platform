from __future__ import annotations

import enum
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.services.storage import (
    KycDocumentType,
    build_object_key,
    generate_presigned_download_url,
    generate_presigned_upload_url,
    get_s3_client,
    validate_upload_metadata,
    verify_uploaded_object,
)

from app.core.database import get_db  # SQLAlchemy session dependency
from ..security import get_current_user, require_roles  # auth dependencies
from ..models import KycDocument, VendorProfile, User, Role  # ORM models

router = APIRouter(prefix="/api/v1", tags=["kyc"])


class DocumentStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class UploadUrlRequest(BaseModel):
    document_type: KycDocumentType
    content_type: str
    declared_size_bytes: int


class RejectRequest(BaseModel):
    reason: str


def authorize_document_access(db: Session, current_user: User, document: KycDocument) -> None:
    """Raises 404 (not 403) on denial, so an unauthorized caller can't use
    this endpoint to probe which document IDs exist for other vendors."""
    is_owner = (
        current_user.role == Role.VENDOR
        and document.vendor.user_id == current_user.id
    )
    is_staff = current_user.role in (Role.OPERATOR, Role.ADMIN)

    if not (is_owner or is_staff):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    # Operators are scoped to their assigned region — enforce that here too,
    # not just at the list-vendors endpoint, so a URL guessed or shared
    # outside an operator's region still gets denied.
    if current_user.role == Role.OPERATOR and document.vendor.region_id != current_user.operator_region_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")


def get_document_or_404(db: Session, doc_id: str) -> KycDocument:
    document = db.execute(
        select(KycDocument).where(KycDocument.id == doc_id)
    ).scalar_one_or_none()
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return document


@router.post("/vendors/me/kyc/documents")
def request_kyc_upload(
    body: UploadUrlRequest,
    current_user: User = Depends(require_roles(Role.VENDOR)),
    db: Session = Depends(get_db),
):
    validate_upload_metadata(body.content_type, body.declared_size_bytes)

    vendor = db.execute(
        select(VendorProfile).where(VendorProfile.user_id == current_user.id)
    ).scalar_one()

    object_key = build_object_key(
        str(vendor.id), body.document_type, body.content_type)

    document = KycDocument(
        vendor_id=vendor.id,
        document_type=body.document_type.value,
        object_key=object_key.as_key(),
        status=DocumentStatus.PENDING.value,
        uploaded_at=datetime.now(timezone.utc),
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    s3 = get_s3_client(endpoint_url="...", access_key="...",
                       secret_key="...")  # from settings
    presigned = generate_presigned_upload_url(s3, object_key)

    return {"document_id": str(document.id), **presigned}


@router.post("/vendors/me/kyc/documents/{doc_id}/confirm")
def confirm_kyc_upload(
    doc_id: str,
    current_user: User = Depends(require_roles(Role.VENDOR)),
    db: Session = Depends(get_db),
):

    document = get_document_or_404(db, doc_id)
    authorize_document_access(db, current_user, document)

    s3 = get_s3_client(endpoint_url="...", access_key="...", secret_key="...")
    verify_uploaded_object(s3, document.object_key)

    document.confirmed_at = datetime.now(timezone.utc)
    db.commit()
    return {"document_id": doc_id, "status": document.status}


@router.get("/vendors/me/kyc/documents")
def list_own_kyc_documents(
    current_user: User = Depends(require_roles(Role.VENDOR)),
    db: Session = Depends(get_db),
):
    vendor = db.execute(
        select(VendorProfile).where(VendorProfile.user_id == current_user.id)
    ).scalar_one()
    docs = db.execute(
        select(KycDocument).where(KycDocument.vendor_id == vendor.id)
    ).scalars().all()
    return [{"id": str(d.id), "document_type": d.document_type, "status": d.status} for d in docs]


@router.get("/kyc/documents/{doc_id}")
def get_kyc_document(
    doc_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    document = get_document_or_404(db, doc_id)
    authorize_document_access(db, current_user, document)

    s3 = get_s3_client(endpoint_url="...", access_key="...", secret_key="...")
    download_url = generate_presigned_download_url(s3, document.object_key)

    return {
        "id": str(document.id),
        "document_type": document.document_type,
        "status": document.status,
        "download_url": download_url,
    }


@router.post("/kyc/documents/{doc_id}/approve")
def approve_kyc_document(
    doc_id: str,
    current_user: User = Depends(require_roles(Role.OPERATOR, Role.ADMIN)),
    db: Session = Depends(get_db),
):
    document = get_document_or_404(db, doc_id)
    authorize_document_access(db, current_user, document)

    if document.status != DocumentStatus.PENDING.value:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot approve a document in '{document.status}' state.",
        )

    document.status = DocumentStatus.APPROVED.value
    document.reviewed_by = current_user.id
    document.reviewed_at = datetime.now(timezone.utc)
    db.add(_audit_entry(document, current_user, "approve"))
    db.commit()
    return {"document_id": doc_id, "status": document.status}


@router.post("/kyc/documents/{doc_id}/reject")
def reject_kyc_document(
    doc_id: str,
    body: RejectRequest,
    current_user: User = Depends(require_roles(Role.OPERATOR, Role.ADMIN)),
    db: Session = Depends(get_db),
):
    document = get_document_or_404(db, doc_id)
    authorize_document_access(db, current_user, document)

    if document.status != DocumentStatus.PENDING.value:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot reject a document in '{document.status}' state.",
        )

    document.status = DocumentStatus.REJECTED.value
    document.reviewed_by = current_user.id
    document.reviewed_at = datetime.now(timezone.utc)
    document.rejection_reason = body.reason
    db.add(_audit_entry(document, current_user, "reject", reason=body.reason))
    db.commit()
    return {"document_id": doc_id, "status": document.status, "reason": body.reason}


def _audit_entry(document: KycDocument, actor: User, action: str, reason: str | None = None):
    from ..models import KycAuditLog  # local import to avoid circular import

    return KycAuditLog(
        document_id=document.id,
        vendor_id=document.vendor_id,
        actor_id=actor.id,
        action=action,
        reason=reason,
        created_at=datetime.now(timezone.utc),
    )
