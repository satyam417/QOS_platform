from __future__ import annotations

import mimetypes
import uuid
from dataclasses import dataclass
from datetime import timedelta
from enum import Enum

import boto3
from botocore.client import Config as BotoConfig
from fastapi import HTTPException, UploadFile, status


# ---------------------------------------------------------------------------
# Contract constants
# ---------------------------------------------------------------------------

KYC_BUCKET = "tfud-kyc-documents"

UPLOAD_URL_EXPIRY = timedelta(minutes=10)
DOWNLOAD_URL_EXPIRY = timedelta(minutes=5)

MAX_UPLOAD_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB per document

ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
}

_EXT_BY_CONTENT_TYPE = {
    "application/pdf": "pdf",
    "image/jpeg": "jpg",
    "image/png": "png",
}


class KycDocumentType(str, Enum):
    PAN_CARD = "pan_card"
    AADHAAR = "aadhaar"
    GST_CERTIFICATE = "gst_certificate"
    BANK_PROOF = "bank_proof"
    BUSINESS_LICENSE = "business_license"


@dataclass(frozen=True)
class ObjectKey:
    vendor_id: str
    document_type: KycDocumentType
    document_id: str
    content_type: str

    def as_key(self) -> str:
        ext = _EXT_BY_CONTENT_TYPE[self.content_type]
        return f"kyc/{self.vendor_id}/{self.document_type.value}/{self.document_id}.{ext}"


def build_object_key(vendor_id: str, document_type: KycDocumentType, content_type: str) -> ObjectKey:
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported content type '{content_type}'. Allowed: {sorted(ALLOWED_CONTENT_TYPES)}",
        )
    return ObjectKey(
        vendor_id=vendor_id,
        document_type=document_type,
        document_id=str(uuid.uuid4()),
        content_type=content_type,
    )


def validate_upload_metadata(content_type: str, declared_size_bytes: int) -> None:
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported content type '{content_type}'.",
        )
    if declared_size_bytes <= 0 or declared_size_bytes > MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size must be between 1 byte and {MAX_UPLOAD_SIZE_BYTES} bytes.",
        )


def validate_upload_file(file: UploadFile) -> None:
    guessed_type = file.content_type or mimetypes.guess_type(file.filename or "")[
        0]
    if guessed_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported content type '{guessed_type}'.",
        )


def get_s3_client(endpoint_url: str, access_key: str, secret_key: str, region: str = "us-east-1"):
    return boto3.client(
        "s3",
        endpoint_url=endpoint_url,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region,
        config=BotoConfig(signature_version="s3v4", s3={
                          "addressing_style": "path"}),
    )


def generate_presigned_upload_url(s3_client, key: ObjectKey) -> dict:
    url = s3_client.generate_presigned_url(
        ClientMethod="put_object",
        Params={
            "Bucket": KYC_BUCKET,
            "Key": key.as_key(),
            "ContentType": key.content_type,
        },
        ExpiresIn=int(UPLOAD_URL_EXPIRY.total_seconds()),
    )
    return {
        "upload_url": url,
        "key": key.as_key(),
        "expires_in_seconds": int(UPLOAD_URL_EXPIRY.total_seconds())
    }


def generate_presigned_download_url(s3_client, object_key: str) -> str:
    return s3_client.generate_presigned_url(
        ClientMethod="get_object",
        Params={"Bucket": KYC_BUCKET, "Key": object_key},
        ExpiresIn=int(DOWNLOAD_URL_EXPIRY.total_seconds()),
    )


def verify_uploaded_object(s3_client, object_key: str) -> None:
    head = s3_client.head_object(Bucket=KYC_BUCKET, Key=object_key)
    size = head["ContentLength"]
    content_type = head.get("ContentType", "")

    if size > MAX_UPLOAD_SIZE_BYTES:
        s3_client.delete_object(Bucket=KYC_BUCKET, Key=object_key)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file exceeds the size limit and was rejected.",
        )
    if content_type not in ALLOWED_CONTENT_TYPES:
        s3_client.delete_object(Bucket=KYC_BUCKET, Key=object_key)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file's actual content type is not allowed and was rejected.",
        )
