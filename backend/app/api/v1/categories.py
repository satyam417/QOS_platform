from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.category_service import CategoryService


router = APIRouter(
    prefix="/categories",
    tags=["Categories"],
)


@router.get("/")
def list_categories(
    db: Session = Depends(get_db),
):
    service = CategoryService(db)

    return service.get_all_categories()


@router.get("/{category_id}")
def get_category(
    category_id: int,
    db: Session = Depends(get_db),
):
    service = CategoryService(db)

    category = service.get_category_by_id(category_id)

    if category is None:
        raise HTTPException(
            status_code=404,
            detail="Category not found",
        )

    return category