from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.core.database import get_db
from app.models.address import Address
from app.models.user import User, UserRole
from app.schemas.customer import (
    AddressCreate,
    AddressResponse,
    CustomerProfileResponse,
    CustomerProfileUpdate,
)


router = APIRouter(
    prefix="/api/v1/customers",
    tags=["Customers"],
)


CurrentCustomer = Annotated[
    User,
    Depends(require_roles(UserRole.CUSTOMER)),
]


# --------------------------------------------------
# CUSTOMER PROFILE
# --------------------------------------------------


@router.post(
    "/profile",
    response_model=CustomerProfileResponse,
)
def create_or_complete_profile(
    profile: CustomerProfileUpdate,
    current_user: CurrentCustomer,
    db: Session = Depends(get_db),
):
    current_user.name = profile.name
    current_user.email = profile.email
    current_user.phone = profile.phone

    db.commit()
    db.refresh(current_user)

    return {
        "user_id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "phone": current_user.phone,
        "role": current_user.role.value,
        "is_verified": current_user.is_verified,
    }


@router.get(
    "/profile",
    response_model=CustomerProfileResponse,
)
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


@router.put(
    "/profile",
    response_model=CustomerProfileResponse,
)
def update_customer_profile(
    profile: CustomerProfileUpdate,
    current_user: CurrentCustomer,
    db: Session = Depends(get_db),
):
    current_user.name = profile.name
    current_user.email = profile.email
    current_user.phone = profile.phone

    db.commit()
    db.refresh(current_user)

    return {
        "user_id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "phone": current_user.phone,
        "role": current_user.role.value,
        "is_verified": current_user.is_verified,
    }


# --------------------------------------------------
# CUSTOMER ADDRESSES
# --------------------------------------------------


@router.post(
    "/addresses",
    response_model=AddressResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_address(
    address_data: AddressCreate,
    current_user: CurrentCustomer,
    db: Session = Depends(get_db),
):
    if address_data.is_default:
        existing_addresses = db.scalars(
            select(Address).where(
                Address.user_id == current_user.id
            )
        ).all()

        for address in existing_addresses:
            address.is_default = False

    address = Address(
        user_id=current_user.id,
        address_line1=address_data.address_line1,
        address_line2=address_data.address_line2,
        city=address_data.city,
        state=address_data.state,
        postal_code=address_data.postal_code,
        country=address_data.country,
        is_default=address_data.is_default,
    )

    db.add(address)
    db.commit()
    db.refresh(address)

    return address


@router.get(
    "/addresses",
    response_model=list[AddressResponse],
)
def get_addresses(
    current_user: CurrentCustomer,
    db: Session = Depends(get_db),
):
    addresses = db.scalars(
        select(Address)
        .where(Address.user_id == current_user.id)
        .order_by(Address.is_default.desc(), Address.id.desc())
    ).all()

    return addresses


@router.get(
    "/addresses/{address_id}",
    response_model=AddressResponse,
)
def get_address(
    address_id: int,
    current_user: CurrentCustomer,
    db: Session = Depends(get_db),
):
    address = db.scalar(
        select(Address).where(
            Address.id == address_id,
            Address.user_id == current_user.id,
        )
    )

    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found",
        )

    return address


@router.put(
    "/addresses/{address_id}",
    response_model=AddressResponse,
)
def update_address(
    address_id: int,
    address_data: AddressCreate,
    current_user: CurrentCustomer,
    db: Session = Depends(get_db),
):
    address = db.scalar(
        select(Address).where(
            Address.id == address_id,
            Address.user_id == current_user.id,
        )
    )

    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found",
        )

    if address_data.is_default:
        existing_addresses = db.scalars(
            select(Address).where(
                Address.user_id == current_user.id,
                Address.id != address_id,
            )
        ).all()

        for existing_address in existing_addresses:
            existing_address.is_default = False

    address.address_line1 = address_data.address_line1
    address.address_line2 = address_data.address_line2
    address.city = address_data.city
    address.state = address_data.state
    address.postal_code = address_data.postal_code
    address.country = address_data.country
    address.is_default = address_data.is_default

    db.commit()
    db.refresh(address)

    return address


@router.delete(
    "/addresses/{address_id}",
)
def delete_address(
    address_id: int,
    current_user: CurrentCustomer,
    db: Session = Depends(get_db),
):
    address = db.scalar(
        select(Address).where(
            Address.id == address_id,
            Address.user_id == current_user.id,
        )
    )

    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found",
        )

    db.delete(address)
    db.commit()

    return {
        "message": "Address deleted successfully",
        "address_id": address_id,
    }