from sqlalchemy.orm import Session

from app.models.category import Category
from app.repositories import category as category_repository


def create_category(
    db: Session,
    name: str,
    description: str | None = None,
) -> Category:
    """
    Create a new service category.

    Category names must be unique.
    """

    name = name.strip()

    if not name:
        raise ValueError("Category name is required")

    existing = category_repository.get_category_by_name(
        db,
        name,
    )

    if existing is not None:
        raise ValueError(
            "Category with this name already exists"
        )

    return category_repository.create_category(
        db=db,
        name=name,
        description=description,
    )


def get_category(
    db: Session,
    category_id: int,
) -> Category:
    category = category_repository.get_category_by_id(
        db,
        category_id,
    )

    if category is None:
        raise LookupError("Category not found")

    return category


def list_categories(
    db: Session,
    include_inactive: bool = False,
) -> list[Category]:
    return category_repository.get_categories(
        db,
        include_inactive=include_inactive,
    )


def update_category(
    db: Session,
    category_id: int,
    name: str | None = None,
    description: str | None = None,
    is_active: bool | None = None,
) -> Category:
    """
    Update a category.

    Only supplied fields are changed.
    """

    category = category_repository.get_category_by_id(
        db,
        category_id,
    )

    if category is None:
        raise LookupError("Category not found")

    if name is not None:
        name = name.strip()

        if not name:
            raise ValueError(
                "Category name is required"
            )

        existing = category_repository.get_category_by_name(
            db,
            name,
        )

        if existing is not None and existing.id != category.id:
            raise ValueError(
                "Category with this name already exists"
            )

        category.name = name

    if description is not None:
        category.description = description

    if is_active is not None:
        category.is_active = is_active

    db.commit()
    db.refresh(category)

    return category


def deactivate_category(
    db: Session,
    category_id: int,
) -> Category:
    """
    Deactivate a category without physically deleting it.

    Existing services remain associated with the category,
    but new services cannot use an inactive category.
    """

    category = category_repository.get_category_by_id(
        db,
        category_id,
    )

    if category is None:
        raise LookupError("Category not found")

    category.is_active = False

    db.commit()
    db.refresh(category)

    return category