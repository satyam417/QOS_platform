from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator

from app.models.service import ServiceStatus


class ServiceCreate(BaseModel):
    category_id: int = Field(..., gt=0)
    name: str = Field(..., min_length=1, max_length=150)
    description: str | None = None
    price: Decimal = Field(
        ...,
        gt=0,
        max_digits=10,
        decimal_places=2,
    )
    duration_minutes: int | None = Field(
        default=None,
        gt=0,
    )
    pincodes: list[str] = Field(
        ...,
        min_length=1,
    )

    @field_validator("pincodes")
    @classmethod
    def validate_pincodes(
        cls,
        value: list[str],
    ) -> list[str]:
        cleaned = [pincode.strip() for pincode in value]

        if not cleaned:
            raise ValueError(
                "At least one pincode is required"
            )

        for pincode in cleaned:
            if not pincode.isdigit() or len(pincode) != 6:
                raise ValueError(
                    "Each pincode must be exactly 6 digits"
                )

        return list(dict.fromkeys(cleaned))


class ServiceUpdate(BaseModel):
    category_id: int | None = Field(
        default=None,
        gt=0,
    )
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=150,
    )
    description: str | None = None
    price: Decimal | None = Field(
        default=None,
        gt=0,
        max_digits=10,
        decimal_places=2,
    )
    duration_minutes: int | None = Field(
        default=None,
        gt=0,
    )
    pincodes: list[str] | None = None
    status: ServiceStatus | None = None

    @field_validator("pincodes")
    @classmethod
    def validate_pincodes(
        cls,
        value: list[str] | None,
    ) -> list[str] | None:
        if value is None:
            return None

        cleaned = [pincode.strip() for pincode in value]

        if not cleaned:
            raise ValueError(
                "At least one pincode is required"
            )

        for pincode in cleaned:
            if not pincode.isdigit() or len(pincode) != 6:
                raise ValueError(
                    "Each pincode must be exactly 6 digits"
                )

        return list(dict.fromkeys(cleaned))


class ServiceResponse(BaseModel):
    id: int
    vendor_id: int
    category_id: int
    name: str
    description: str | None
    price: Decimal
    duration_minutes: int | None
    status: ServiceStatus
    pincodes: list[str]
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }