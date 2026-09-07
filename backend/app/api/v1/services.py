from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.core.database import get_db
from app.models.service import Service, ServiceStatus
from app.models.user import User, UserRole
from app.schemas.service import (
    ServiceCreate,
    ServiceResponse,
    ServiceUpdate,
)
from app.services import service as service_service


router = APIRouter(
    prefix="/services",
    tags=["Services"],
)


def _to_response(service: Service) -> ServiceResponse:
    """
    Convert a SQLAlchemy Service model into the API response format.
    """
    return ServiceResponse(
        id=service.id,
        vendor_id=service.vendor_id,
        category_id=service.category_id,
        name=service.name,
        description=service.description,
        price=service.price,
        duration_minutes=service.duration_minutes,
        status=service.status,
        pincodes=[
            pincode.pincode
            for pincode in service.pincodes
        ],
        created_at=service.created_at,
        updated_at=service.updated_at,
    )


def _handle_service_error(error: Exception) -> None:
    """
    Convert business-layer exceptions into HTTP exceptions.
    """
    if isinstance(error, PermissionError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(error),
        )

    if isinstance(error, LookupError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )

    if isinstance(error, ValueError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )

    raise error


# =========================================================
# CREATE SERVICE
# =========================================================

@router.post(
    "",
    response_model=ServiceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_service(
    payload: ServiceCreate,
    current_user: Annotated[
        User,
        Depends(require_roles(UserRole.VENDOR)),
    ],
    db: Annotated[
        Session,
        Depends(get_db),
    ],
):
    try:
        service = service_service.create_service(
            db=db,
            user_id=current_user.id,
            category_id=payload.category_id,
            name=payload.name,
            price=payload.price,
            description=payload.description,
            duration_minutes=payload.duration_minutes,
            pincodes=payload.pincodes,
        )
    except Exception as error:
        _handle_service_error(error)

    return _to_response(service)


# =========================================================
# LIST SERVICES
# =========================================================

@router.get(
    "",
    response_model=list[ServiceResponse],
)
def list_services(
    category: int | None = Query(
        default=None,
        gt=0,
    ),
    pincode: str | None = Query(
        default=None,
    ),
    db: Annotated[
        Session,
        Depends(get_db),
    ] = None,
):
    # Category + pincode filter
    if category is not None and pincode is not None:
        try:
            services = service_service.list_services_by_category(
                db,
                category,
            )
        except Exception as error:
            _handle_service_error(error)

        return [
            _to_response(service)
            for service in services
            if any(
                area.pincode == pincode
                for area in service.pincodes
            )
        ]

    # Category filter
    if category is not None:
        try:
            services = service_service.list_services_by_category(
                db,
                category,
            )
        except Exception as error:
            _handle_service_error(error)

        return [
            _to_response(service)
            for service in services
        ]

    # Pincode filter
    if pincode is not None:
        try:
            services = service_service.list_services_by_pincode(
                db,
                pincode,
            )
        except Exception as error:
            _handle_service_error(error)

        return [
            _to_response(service)
            for service in services
        ]

    # No filters: return all active services.
    services = db.scalars(
        select(Service).where(
            Service.status == ServiceStatus.ACTIVE
        )
    ).unique().all()

    return [
        _to_response(service)
        for service in services
    ]


# =========================================================
# VENDOR: LIST MY SERVICES
# =========================================================

@router.get(
    "/vendor/me",
    response_model=list[ServiceResponse],
)
def list_my_services(
    current_user: Annotated[
        User,
        Depends(require_roles(UserRole.VENDOR)),
    ],
    db: Annotated[
        Session,
        Depends(get_db),
    ],
):
    try:
        services = service_service.list_vendor_services(
            db,
            current_user.id,
            include_inactive=True,
        )
    except Exception as error:
        _handle_service_error(error)

    return [
        _to_response(service)
        for service in services
    ]


# =========================================================
# VENDOR: GET MY SERVICE
# =========================================================

@router.get(
    "/vendor/me/{service_id}",
    response_model=ServiceResponse,
)
def get_my_service(
    service_id: int,
    current_user: Annotated[
        User,
        Depends(require_roles(UserRole.VENDOR)),
    ],
    db: Annotated[
        Session,
        Depends(get_db),
    ],
):
    try:
        service = service_service.get_vendor_service(
            db,
            current_user.id,
            service_id,
        )
    except Exception as error:
        _handle_service_error(error)

    return _to_response(service)


# =========================================================
# GET PUBLIC SERVICE BY ID
# =========================================================

@router.get(
    "/{service_id}",
    response_model=ServiceResponse,
)
def get_service(
    service_id: int,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
):
    try:
        service = service_service.get_service(
            db,
            service_id,
        )
    except Exception as error:
        _handle_service_error(error)

    if service.status != ServiceStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found",
        )

    return _to_response(service)


# =========================================================
# UPDATE SERVICE
# =========================================================

@router.put(
    "/{service_id}",
    response_model=ServiceResponse,
)
def update_service(
    service_id: int,
    payload: ServiceUpdate,
    current_user: Annotated[
        User,
        Depends(require_roles(UserRole.VENDOR)),
    ],
    db: Annotated[
        Session,
        Depends(get_db),
    ],
):
    update_data = payload.model_dump(
        exclude_unset=True,
    )

    try:
        service = service_service.update_service(
            db=db,
            user_id=current_user.id,
            service_id=service_id,
            category_id=update_data.get("category_id"),
            name=update_data.get("name"),
            description=update_data.get("description"),
            price=update_data.get("price"),
            duration_minutes=update_data.get(
                "duration_minutes"
            ),
            pincodes=update_data.get("pincodes"),
            service_status=update_data.get("status"),
        )
    except Exception as error:
        _handle_service_error(error)

    return _to_response(service)


# =========================================================
# DELETE / DISABLE SERVICE
# =========================================================

@router.delete(
    "/{service_id}",
    response_model=ServiceResponse,
)
def delete_service(
    service_id: int,
    current_user: Annotated[
        User,
        Depends(require_roles(UserRole.VENDOR)),
    ],
    db: Annotated[
        Session,
        Depends(get_db),
    ],
):
    try:
        service = service_service.disable_service(
            db=db,
            user_id=current_user.id,
            service_id=service_id,
        )
    except Exception as error:
        _handle_service_error(error)

    return _to_response(service)