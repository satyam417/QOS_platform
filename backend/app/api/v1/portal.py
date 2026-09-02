from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import require_roles
from app.models.user import User, UserRole


router = APIRouter(
    prefix="/portal",
    tags=["Portal"],
)


@router.get("/vendor")
def vendor_portal(
    current_user: Annotated[
        User,
        Depends(require_roles(UserRole.VENDOR)),
    ],
):
    return {
        "message": "Welcome to Vendor Portal",
        "user": current_user.name,
        "role": current_user.role.value,
    }


@router.get("/operator")
def operator_portal(
    current_user: Annotated[
        User,
        Depends(require_roles(UserRole.OPERATOR)),
    ],
):
    return {
        "message": "Welcome to Operator Portal",
        "user": current_user.name,
        "role": current_user.role.value,
    }


@router.get("/admin")
def admin_portal(
    current_user: Annotated[
        User,
        Depends(require_roles(UserRole.ADMIN)),
    ],
):
    return {
        "message": "Welcome to Admin Portal",
        "user": current_user.name,
        "role": current_user.role.value,
    }