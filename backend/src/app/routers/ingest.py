from fastapi import APIRouter, UploadFile, HTTPException
import pandas as pd
from app.models.plaid_models import TransactionIn
from app.db import get_connection

router = APIRouter()

@router.post("/upload")
async def upload_transactions(file: UploadFile):
    try:
        df = pd.read_csv(file.file)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid CSV: {e}")

    required_cols = ["user_id", "posted_at", "amount", "currency", "merchant_name", "description"]
    if not all(col in df.columns for col in required_cols):
        raise HTTPException(status_code=400, detail=f"Missing required columns. Expected {required_cols}")

    # Validate with Pydantic
    transactions = []
    for _, row in df.iterrows():
        try:
            tx = TransactionIn(**row.to_dict())
            transactions.append(tx)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Validation error: {e}")

    # Insert into DB
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.executemany(
            """INSERT INTO transactions (user_id, posted_at, amount, currency, merchant_name, description)
            VALUES (?, ?, ?, ?, ?, ?)""",
            [(t.user_id, t.posted_at, t.amount, t.currency, t.merchant_name, t.description) for t in transactions]
        )
        conn.commit()
        return {"inserted": len(transactions), "status": "success"}