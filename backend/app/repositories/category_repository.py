from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.category import Category


class CategoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[Category]:
        statement = (
            select(Category)
            .where(Category.is_active.is_(True))
            .order_by(Category.name)
        )

        return list(self.db.scalars(statement).all())

    def get_by_id(self, category_id: int) -> Category | None:
        statement = select(Category).where(
            Category.id == category_id,
            Category.is_active.is_(True),
        )

        return self.db.scalar(statement)

    def get_by_name(self, name: str) -> Category | None:
        statement = select(Category).where(
            Category.name == name,
            Category.is_active.is_(True),
        )

        return self.db.scalar(statement)