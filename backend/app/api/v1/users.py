from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


# =========================================================
# GET MY PROFILE
# =========================================================

@router.get("/me")
def get_my_profile(
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "phone": current_user.phone,
        "role": (
            current_user.role.value
            if hasattr(current_user.role, "value")
            else str(current_user.role)
        ),
        "is_active": current_user.is_active,
        "is_verified": current_user.is_verified,
    }


# =========================================================
# GET USER BY ID
# =========================================================

@router.get("/{user_id}")
def get_user_by_id(
    user_id: int,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
):

    user = db.scalar(
        select(User).where(
            User.id == user_id
        )
    )

    if user is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "phone": user.phone,
        "role": (
            user.role.value
            if hasattr(user.role, "value")
            else str(user.role)
        ),
        "is_active": user.is_active,
        "is_verified": user.is_verified,
    }