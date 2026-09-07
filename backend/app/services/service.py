from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.service import Service, ServiceStatus
from app.models.vendor import KYCStatus, VendorProfile
from app.repositories import service as service_repository


def _get_vendor_profile(
    db: Session,
    user_id: int,
) -> VendorProfile:
    profile = db.scalar(
        select(VendorProfile).where(
            VendorProfile.user_id == user_id
        )
    )

    if profile is None:
        raise ValueError("Vendor profile not found")

    return profile


def _require_approved_vendor(
    db: Session,
    user_id: int,
) -> VendorProfile:
    profile = _get_vendor_profile(db, user_id)

    if profile.kyc_status != KYCStatus.APPROVED:
        raise PermissionError("KYC approval is required")

    return profile


def _get_active_category(
    db: Session,
    category_id: int,
) -> Category:
    category = db.scalar(
        select(Category).where(
            Category.id == category_id,
            Category.is_active.is_(True),
        )
    )

    if category is None:
        raise LookupError("Category not found")

    return category


def create_service(
    db: Session,
    user_id: int,
    category_id: int,
    name: str,
    price: Decimal,
    description: str | None = None,
    duration_minutes: int | None = None,
    pincodes: list[str] | None = None,
) -> Service:
    vendor = _require_approved_vendor(db, user_id)

    _get_active_category(db, category_id)

    if not pincodes:
        raise ValueError("At least one pincode is required")

    return service_repository.create_service(
        db=db,
        vendor_id=vendor.id,
        category_id=category_id,
        name=name.strip(),
        price=price,
        description=description,
        duration_minutes=duration_minutes,
        pincodes=pincodes,
    )


def get_service(
    db: Session,
    service_id: int,
) -> Service:
    service = service_repository.get_service_by_id(
        db,
        service_id,
    )

    if service is None:
        raise LookupError("Service not found")

    return service


def get_vendor_service(
    db: Session,
    user_id: int,
    service_id: int,
) -> Service:
    vendor = _get_vendor_profile(db, user_id)

    service = service_repository.get_service_by_id_for_vendor(
        db,
        service_id,
        vendor.id,
    )

    if service is None:
        raise PermissionError(
            "You do not have access to this service"
        )

    return service


def update_service(
    db: Session,
    user_id: int,
    service_id: int,
    category_id: int | None = None,
    name: str | None = None,
    description: str | None = None,
    price: Decimal | None = None,
    duration_minutes: int | None = None,
    pincodes: list[str] | None = None,
    service_status: ServiceStatus | None = None,
) -> Service:
    vendor = _require_approved_vendor(db, user_id)

    service = service_repository.get_service_by_id_for_vendor(
        db,
        service_id,
        vendor.id,
    )

    if service is None:
        raise PermissionError(
            "You do not have access to this service"
        )

    if category_id is not None:
        _get_active_category(db, category_id)
        service.category_id = category_id

    if name is not None:
        service.name = name.strip()

    if description is not None:
        service.description = description

    if price is not None:
        if price <= 0:
            raise ValueError(
                "Price must be greater than 0"
            )
        service.price = price

    if duration_minutes is not None:
        if duration_minutes <= 0:
            raise ValueError(
                "Duration must be greater than 0"
            )
        service.duration_minutes = duration_minutes

    if service_status is not None:
        service.status = service_status

    if pincodes is not None:
        if not pincodes:
            raise ValueError(
                "At least one pincode is required"
            )

        service_repository.replace_service_pincodes(
            db,
            service,
            pincodes,
        )

    db.commit()
    db.refresh(service)

    return service


def disable_service(
    db: Session,
    user_id: int,
    service_id: int,
) -> Service:
    vendor = _require_approved_vendor(db, user_id)

    service = service_repository.get_service_by_id_for_vendor(
        db,
        service_id,
        vendor.id,
    )

    if service is None:
        raise PermissionError(
            "You do not have access to this service"
        )

    return service_repository.disable_service(
        db,
        service,
    )


def list_vendor_services(
    db: Session,
    user_id: int,
    include_inactive: bool = True,
) -> list[Service]:
    vendor = _get_vendor_profile(db, user_id)

    return service_repository.get_services_by_vendor(
        db,
        vendor.id,
        include_inactive=include_inactive,
    )


def list_services_by_category(
    db: Session,
    category_id: int,
) -> list[Service]:
    _get_active_category(db, category_id)

    return service_repository.get_services_by_category(
        db,
        category_id,
        include_inactive=False,
    )


def list_services_by_pincode(
    db: Session,
    pincode: str,
) -> list[Service]:
    if not pincode.isdigit() or len(pincode) != 6:
        raise ValueError(
            "Pincode must be exactly 6 digits"
        )

    return service_repository.get_services_by_pincode(
        db,
        pincode,
        include_inactive=False,
    )