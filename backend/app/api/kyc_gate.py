from fastapi import Depends, HTTPException, status

from app.api.deps import get_current_user
from app.models.user import User


async def require_kyc_approved(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Temporary KYC authorization gate.

    The dedicated KYC approval status is not available yet.
    Until the KYC module is merged, account verification is
    used as a temporary placeholder.

    Replace this check with the actual KYC approval status
    when the KYC APIs/model are integrated.
    """

    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="KYC approval is required",
        )

    return current_user