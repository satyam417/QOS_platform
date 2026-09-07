from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.core.database import get_db
from app.models.user import User, UserRole
from app.schemas.category import (
    CategoryCreate,
    CategoryResponse,
    CategoryUpdate,
)
from app.services import category as category_service


router = APIRouter(
    prefix="/categories",
    tags=["Categories"],
)


AdminUser = Annotated[
    User,
    Depends(require_roles(UserRole.ADMIN)),
]


def _handle_category_error(error: Exception) -> None:
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


@router.post(
    "",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_category(
    payload: CategoryCreate,
    _admin: AdminUser,
    db: Session = Depends(get_db),
):
    try:
        return category_service.create_category(
            db=db,
            name=payload.name,
            description=payload.description,
        )
    except Exception as error:
        _handle_category_error(error)


@router.get(
    "",
    response_model=list[CategoryResponse],
)
def list_categories(
    include_inactive: bool = Query(False),
    db: Session = Depends(get_db),
):
    return category_service.list_categories(
        db=db,
        include_inactive=include_inactive,
    )


@router.get(
    "/{category_id}",
    response_model=CategoryResponse,
)
def get_category(
    category_id: int,
    db: Session = Depends(get_db),
):
    try:
        return category_service.get_category(
            db=db,
            category_id=category_id,
        )
    except Exception as error:
        _handle_category_error(error)


@router.put(
    "/{category_id}",
    response_model=CategoryResponse,
)
def update_category(
    category_id: int,
    payload: CategoryUpdate,
    _admin: AdminUser,
    db: Session = Depends(get_db),
):
    update_data = payload.model_dump(exclude_unset=True)

    try:
        return category_service.update_category(
            db=db,
            category_id=category_id,
            name=update_data.get("name"),
            description=update_data.get("description"),
            is_active=update_data.get("is_active"),
        )
    except Exception as error:
        _handle_category_error(error)


@router.delete(
    "/{category_id}",
    response_model=CategoryResponse,
)
def delete_category(
    category_id: int,
    _admin: AdminUser,
    db: Session = Depends(get_db),
):
    try:
        return category_service.deactivate_category(
            db=db,
            category_id=category_id,
        )
    except Exception as error:
        _handle_category_error(error)
