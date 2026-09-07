from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.service import Service, ServiceStatus
from app.models.service_pincode import ServicePincode


def create_service(
    db: Session,
    vendor_id: int,
    category_id: int,
    name: str,
    price,
    description: str | None = None,
    duration_minutes: int | None = None,
    pincodes: list[str] | None = None,
) -> Service:
    service = Service(
        vendor_id=vendor_id,
        category_id=category_id,
        name=name,
        description=description,
        price=price,
        duration_minutes=duration_minutes,
        status=ServiceStatus.ACTIVE,
    )

    if pincodes:
        service.pincodes = [
            ServicePincode(pincode=pincode)
            for pincode in pincodes
        ]

    db.add(service)
    db.commit()
    db.refresh(service)

    return service


def get_service_by_id(
    db: Session,
    service_id: int,
) -> Service | None:
    return db.scalar(
        select(Service).where(Service.id == service_id)
    )


def get_service_by_id_for_vendor(
    db: Session,
    service_id: int,
    vendor_id: int,
) -> Service | None:
    return db.scalar(
        select(Service).where(
            Service.id == service_id,
            Service.vendor_id == vendor_id,
        )
    )


def get_services_by_vendor(
    db: Session,
    vendor_id: int,
    include_inactive: bool = True,
) -> list[Service]:
    query = (
        select(Service)
        .where(Service.vendor_id == vendor_id)
        .order_by(Service.created_at.desc())
    )

    if not include_inactive:
        query = query.where(
            Service.status == ServiceStatus.ACTIVE
        )

    return list(db.scalars(query).all())


def get_services_by_category(
    db: Session,
    category_id: int,
    include_inactive: bool = False,
) -> list[Service]:
    query = (
        select(Service)
        .where(Service.category_id == category_id)
        .order_by(Service.created_at.desc())
    )

    if not include_inactive:
        query = query.where(
            Service.status == ServiceStatus.ACTIVE
        )

    return list(db.scalars(query).all())


def get_services_by_pincode(
    db: Session,
    pincode: str,
    include_inactive: bool = False,
) -> list[Service]:
    query = (
        select(Service)
        .join(ServicePincode)
        .where(ServicePincode.pincode == pincode)
        .order_by(Service.created_at.desc())
    )

    if not include_inactive:
        query = query.where(
            Service.status == ServiceStatus.ACTIVE
        )

    return list(db.scalars(query).unique().all())


def update_service(
    db: Session,
    service: Service,
    **fields,
) -> Service:
    for field, value in fields.items():
        setattr(service, field, value)

    db.commit()
    db.refresh(service)

    return service


def replace_service_pincodes(
    db: Session,
    service: Service,
    pincodes: list[str],
) -> Service:
    # Delete existing pincode mappings explicitly.
    db.execute(
        delete(ServicePincode).where(
            ServicePincode.service_id == service.id
        )
    )

    # Ensure the DELETE is executed before inserting
    # the replacement pincode mappings.
    db.flush()

    # Add the replacement mappings.
    service.pincodes = [
        ServicePincode(pincode=pincode)
        for pincode in pincodes
    ]

    # Do not commit here.
    # The business/service layer owns the transaction.
    return service


def disable_service(
    db: Session,
    service: Service,
) -> Service:
    service.status = ServiceStatus.INACTIVE

    db.commit()
    db.refresh(service)

    return service