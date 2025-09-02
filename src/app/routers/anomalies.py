from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def anomaly_example():
    # TODO: run anomaly detection
    return {"example": "anomaly result"}