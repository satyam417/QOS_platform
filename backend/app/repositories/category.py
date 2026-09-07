from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.category import Category


def create_category(
    db: Session,
    name: str,
    description: str | None = None,
) -> Category:
    category = Category(
        name=name,
        description=description,
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    return category


def get_category_by_id(
    db: Session,
    category_id: int,
) -> Category | None:
    return db.scalar(
        select(Category).where(Category.id == category_id)
    )


def get_category_by_name(
    db: Session,
    name: str,
) -> Category | None:
    return db.scalar(
        select(Category).where(Category.name == name)
    )


def get_categories(
    db: Session,
    include_inactive: bool = False,
) -> list[Category]:
    query = select(Category).order_by(Category.name)

    if not include_inactive:
        query = query.where(Category.is_active.is_(True))

    return list(db.scalars(query).all())


def update_category(
    db: Session,
    category: Category,
    **fields,
) -> Category:
    for field, value in fields.items():
        setattr(category, field, value)

    db.commit()
    db.refresh(category)

    return category


def delete_category(
    db: Session,
    category: Category,
) -> None:
    db.delete(category)
    db.commit()