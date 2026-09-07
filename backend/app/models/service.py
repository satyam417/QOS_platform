import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base


if TYPE_CHECKING:
    from app.models.category import Category
    from app.models.service_pincode import ServicePincode
    from app.models.vendor import VendorProfile


class ServiceStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class Service(Base):
    __tablename__ = "services"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    vendor_id: Mapped[int] = mapped_column(
        ForeignKey("vendor_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    price: Mapped[float] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    duration_minutes: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    status: Mapped[ServiceStatus] = mapped_column(
        Enum(ServiceStatus),
        default=ServiceStatus.ACTIVE,
        nullable=False,
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

    vendor: Mapped["VendorProfile"] = relationship(
        "VendorProfile",
        back_populates="services",
    )

    category: Mapped["Category"] = relationship(
        "Category",
        back_populates="services",
    )

    pincodes: Mapped[list["ServicePincode"]] = relationship(
        "ServicePincode",
        back_populates="service",
        cascade="all, delete-orphan",
    )