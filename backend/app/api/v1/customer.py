from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.core.database import get_db
from app.models.user import User, UserRole


router = APIRouter(
    prefix="/api/v1/customers",
    tags=["Customers"],
)


CurrentCustomer = Annotated[
    User,
    Depends(require_roles(UserRole.CUSTOMER)),
]


@router.post("/profile")
def create_or_complete_profile(
    current_user: CurrentCustomer,
    db: Session = Depends(get_db),
):
    return {
        "message": "Customer profile created/completed",
        "user_id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "phone": current_user.phone,
    }


@router.get("/profile")
def get_customer_profile(
    current_user: CurrentCustomer,
):
    return {
        "user_id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "phone": current_user.phone,
        "role": current_user.role.value,
        "is_verified": current_user.is_verified,
    }


@router.put("/profile")
def update_customer_profile(
    current_user: CurrentCustomer,
    db: Session = Depends(get_db),
):
    return {
        "message": "Customer profile update endpoint",
        "user_id": current_user.id,
    }