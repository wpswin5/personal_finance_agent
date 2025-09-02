from fastapi import APIRouter

router = APIRouter()

@router.post("/")
async def chat_query(query: str):
    # TODO: connect to LLM + SQL
    return {"query": query, "response": "This is a placeholder response."}