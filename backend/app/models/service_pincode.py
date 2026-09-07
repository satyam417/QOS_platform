from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base


if TYPE_CHECKING:
    from app.models.service import Service


class ServicePincode(Base):
    __tablename__ = "service_pincodes"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    service_id: Mapped[int] = mapped_column(
        ForeignKey("services.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    pincode: Mapped[str] = mapped_column(
        String(6),
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    service: Mapped["Service"] = relationship(
        "Service",
        back_populates="pincodes",
    )

    __table_args__ = (
        UniqueConstraint(
            "service_id",
            "pincode",
            name="uq_service_pincode",
        ),
    )