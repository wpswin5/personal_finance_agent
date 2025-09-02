from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def classify_example():
    # TODO: load model, classify transactions
    return {"example": "classification result"}