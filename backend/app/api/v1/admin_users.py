from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.core.database import get_db
from app.core.security import hash_password
from app.models.user import User, UserRole
from app.schemas.user import AdminUserCreate, UserOut, UserStatusUpdate

router = APIRouter(prefix="/admin/users", tags=["Admin Users"])


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_internal_user(
    payload: AdminUserCreate,
    db: Annotated[Session, Depends(get_db)],
    _admin: Annotated[User, Depends(require_roles(UserRole.ADMIN))],
):
    try:
        role = UserRole(payload.role)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="role must be one of: customer, vendor, admin",
        )

    existing = db.scalar(select(User).where(User.email == payload.email))
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = User(
        name=payload.name.strip(),
        email=payload.email.lower().strip(),
        phone=payload.phone,
        password_hash=hash_password(payload.password),
        role=role,
        is_active=True,
        is_verified=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.patch("/{user_id}/status", response_model=UserOut)
def update_user_status(
    user_id: int,
    payload: UserStatusUpdate,
    db: Annotated[Session, Depends(get_db)],
    admin: Annotated[User, Depends(require_roles(UserRole.ADMIN))],
):
    if user_id == admin.id and payload.is_active is False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account",
        )

    user = db.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.is_active = payload.is_active
    db.commit()
    db.refresh(user)
    return user