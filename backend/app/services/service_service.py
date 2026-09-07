from sqlalchemy.orm import Session

from app.repositories.service_repository import ServiceRepository


class ServiceService:
    def __init__(self, db: Session):
        self.repository = ServiceRepository(db)

    def get_all_services(self):
        return self.repository.get_all()

    def get_service_by_id(self, service_id: int):
        return self.repository.get_by_id(service_id)

    def get_services_by_vendor(self, vendor_id: int):
        return self.repository.get_by_vendor_id(vendor_id)

    def get_services_by_category(self, category_id: int):
        return self.repository.get_by_category_id(category_id)

    def search_services(self, search_query: str):
        return self.repository.search(search_query)