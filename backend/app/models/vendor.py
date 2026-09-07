import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base


if TYPE_CHECKING:
    from app.models.service import Service


class KYCStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class VendorProfile(Base):
    __tablename__ = "vendor_profiles"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    business_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    business_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    gst_number: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    bank_account_number: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    bank_ifsc: Mapped[str | None] = mapped_column(
        String(15),
        nullable=True,
    )

    kyc_status: Mapped[KYCStatus] = mapped_column(
        Enum(KYCStatus),
        default=KYCStatus.PENDING,
        nullable=False,
    )

    kyc_document_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    kyc_document_reference: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    kyc_submitted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    services: Mapped[list["Service"]] = relationship(
        "Service",
        back_populates="vendor",
        cascade="all, delete-orphan",
    )