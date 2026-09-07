from sqlalchemy.orm import Session

from app.repositories.category_repository import CategoryRepository


class CategoryService:
    def __init__(self, db: Session):
        self.repository = CategoryRepository(db)

    def get_all_categories(self):
        return self.repository.get_all()

    def get_category_by_id(self, category_id: int):
        return self.repository.get_by_id(category_id)

    def get_category_by_name(self, name: str):
        return self.repository.get_by_name(name)