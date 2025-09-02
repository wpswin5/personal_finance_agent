from fastapi import APIRouter, UploadFile
import pandas as pd

router = APIRouter()

@router.post("/upload")
async def upload_transactions(file: UploadFile):
    df = pd.read_csv(file.file)
    # TODO: validate & insert into DB
    return {"rows": len(df), "status": "ingested"}