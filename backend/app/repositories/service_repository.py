from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.service import Service


class ServiceRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[Service]:
        statement = (
            select(Service)
            .where(Service.is_enabled.is_(True))
            .order_by(Service.name)
        )

        return list(self.db.scalars(statement).all())

    def get_by_id(self, service_id: int) -> Service | None:
        statement = select(Service).where(
            Service.id == service_id,
            Service.is_enabled.is_(True),
        )

        return self.db.scalar(statement)

    def get_by_vendor_id(self, vendor_id: int) -> list[Service]:
        statement = (
            select(Service)
            .where(
                Service.vendor_id == vendor_id,
                Service.is_enabled.is_(True),
            )
            .order_by(Service.name)
        )

        return list(self.db.scalars(statement).all())

    def get_by_category_id(self, category_id: int) -> list[Service]:
        statement = (
            select(Service)
            .where(
                Service.category_id == category_id,
                Service.is_enabled.is_(True),
            )
            .order_by(Service.name)
        )

        return list(self.db.scalars(statement).all())

    def search(
        self,
        search_query: str,
    ) -> list[Service]:
        search_text = f"%{search_query.strip()}%"

        statement = (
            select(Service)
            .where(
                Service.is_enabled.is_(True),
                Service.name.ilike(search_text),
            )
            .order_by(Service.name)
        )

        return list(self.db.scalars(statement).all())