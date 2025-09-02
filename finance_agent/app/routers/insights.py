from fastapi import APIRouter

router = APIRouter()

@router.get("/monthly")
async def monthly_summary():
    # TODO: compute summary from DB
    return {"month": "2025-08", "total_spend": 1234.56}