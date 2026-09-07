from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.service_service import ServiceService


router = APIRouter(
    prefix="/services",
    tags=["Services"],
)


@router.get("/")
def list_services(
    db: Session = Depends(get_db),
):
    service = ServiceService(db)

    return service.get_all_services()


@router.get("/search")
def search_services(
    q: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
):
    service = ServiceService(db)

    return service.search_services(q)


@router.get("/{service_id}")
def get_service(
    service_id: int,
    db: Session = Depends(get_db),
):
    service = ServiceService(db)

    result = service.get_service_by_id(service_id)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Service not found",
        )

    return result


@router.get("/vendor/{vendor_id}")
def get_services_by_vendor(
    vendor_id: int,
    db: Session = Depends(get_db),
):
    service = ServiceService(db)

    return service.get_services_by_vendor(vendor_id)


@router.get("/category/{category_id}")
def get_services_by_category(
    category_id: int,
    db: Session = Depends(get_db),
):
    service = ServiceService(db)

    return service.get_services_by_category(category_id)