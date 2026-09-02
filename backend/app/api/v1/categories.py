from fastapi import APIRouter


router = APIRouter(
    prefix="/categories",
    tags=["Categories"],
)


@router.get("/")
async def list_categories():
    return {
        "categories": [
            {
                "id": 1,
                "name": "Cleaning",
            },
            {
                "id": 2,
                "name": "Plumbing",
            },
            {
                "id": 3,
                "name": "Electrical",
            },
            {
                "id": 4,
                "name": "Painting",
            },
            {
                "id": 5,
                "name": "AC Repair",
            },
        ]
    }