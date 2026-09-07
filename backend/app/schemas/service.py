from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ServiceCreate(BaseModel):
    vendor_id: int
    category_id: int
    name: str
    description: str | None = None
    price: int
    is_enabled: bool = True


class ServiceResponse(BaseModel):
    id: int
    vendor_id: int
    category_id: int
    name: str
    description: str | None
    price: int
    is_enabled: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)