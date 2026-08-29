from fastapi import APIRouter, Depends

from app.api.kyc_gate import require_kyc_approved
from app.models.user import User


router = APIRouter(
    prefix="/services",
    tags=["Services"],
)


@router.get("/")
async def list_services(
    current_user: User = Depends(require_kyc_approved),
):
    return {
        "services": [
            {
                "id": 1,
                "name": "Home Cleaning",
                "category_id": 1,
            },
            {
                "id": 2,
                "name": "Plumbing Repair",
                "category_id": 2,
            },
            {
                "id": 3,
                "name": "Electrical Repair",
                "category_id": 3,
            },
        ]
    }