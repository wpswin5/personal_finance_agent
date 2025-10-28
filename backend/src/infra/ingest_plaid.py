import os
import pyodbc
import json
import datetime as dt
import time
from typing import List, Dict
from app.config import get_settings

settings = get_settings()

import plaid
from plaid.api import plaid_api
from plaid.model.sandbox_public_token_create_request import SandboxPublicTokenCreateRequest
from plaid.model.sandbox_item_fire_webhook_request import SandboxItemFireWebhookRequest
from plaid.model.products import Products
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.transactions_sync_request import TransactionsSyncRequest
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.model.sandbox_transactions_create_request import SandboxTransactionsCreateRequest


from transaction_generator import generate_fake_transactions

PLAID_CLIENT_ID = settings.PLAID_CLIENT_ID
PLAID_SECRET = settings.PLAID_SECRET

if not PLAID_CLIENT_ID or not PLAID_SECRET:
    raise RuntimeError("Set PLAID_CLIENT_ID and PLAID_SECRET in your environment.")

# --- Create client (current SDK pattern) ---
configuration = plaid.Configuration(
    host=plaid.Environment.Sandbox,
    api_key={"clientId": PLAID_CLIENT_ID, "secret": PLAID_SECRET},
)
api_client = plaid.ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)

def create_access_token(institution_id: str = "ins_109508") -> str:
    """Create a sandbox Item and exchange for an access_token."""
    pt_req = SandboxPublicTokenCreateRequest(
        institution_id=institution_id,
        initial_products=[Products("transactions")],
    )
    pt_res = client.sandbox_public_token_create(pt_req)
    public_token = pt_res.to_dict()["public_token"]

    ex_req = ItemPublicTokenExchangeRequest(public_token=public_token)
    ex_res = client.item_public_token_exchange(ex_req)
    return ex_res.to_dict()["access_token"]

def fetch_accounts(access_token: str) -> List[Dict]:
    ag_req = AccountsGetRequest(access_token=access_token)
    ag_res = client.accounts_get(ag_req)
    return ag_res.to_dict()["accounts"]

def create_sandbox_transactions(access_token: str, txs: list[dict]):
    request = SandboxTransactionsCreateRequest(
        access_token=access_token,
        transactions=txs
    )

    try:
        response = client.sandbox_transactions_create(request)
        print(f"✨ Created {len(txs)} sandbox transactions")
        return response.to_dict()
    except Exception as e:
        print("❌ Error creating sandbox transactions:", e)
        raise

# -------------------------------
# Step 3. Fetch All Transactions
# -------------------------------
def fetch_all_transactions(access_token: str, count: int = 100):
    cursor = ""
    all_transactions = []

    while True:
        req = TransactionsSyncRequest(
            access_token=access_token,
            cursor=cursor,
            count=count,
        )
        res = client.transactions_sync(req).to_dict()

        txs = res.get("added", [])
        all_transactions.extend(txs)

        cursor = res.get("next_cursor")
        if not res.get("has_more"):
            break

    print(f"📥 Fetched {len(all_transactions)} transactions from Plaid")
    return all_transactions

def insert_transactions_sql(transactions: list[dict]):
    print("Trying to connect to SQL Server")
    with pyodbc.connect(settings.AZURE_SQL_CONN) as conn:
        print("Connected to SQL server")
        cursor = conn.cursor()
        print(len(transactions))
        for tx in transactions:
            merchant = tx.get("merchant_name") or tx.get("name")
            pf_category = tx.get("personal_finance_category", {})
            category_pred = pf_category.get("primary")
            confidence_level = pf_category.get("confidence_level")
            plaid_tx_id = tx.get("transaction_id")
            category_conf = 1.0 if confidence_level == "VERY_HIGH" else 0.5

            cursor.execute("""
                IF NOT EXISTS (SELECT 1 FROM transactions WHERE plaid_transaction_id = ?)
                BEGIN
                    INSERT INTO transactions
                    (user_id, posted_at, amount, currency, merchant_name, description,
                    category_id, category_pred, category_conf, source, plaid_transaction_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                END
            """, (
                plaid_tx_id,
                "sandbox_user",
                tx.get("date"),
                tx.get("amount"),
                tx.get("iso_currency_code"),
                merchant,
                tx.get("name"),
                None,
                category_pred,
                category_conf,
                "plaid",
                plaid_tx_id,
            ))


        conn.commit()
        print(f"✅ Inserted {len(transactions)} transactions into Azure SQL")

def main():
    access_token = create_access_token()
    fake_txs = generate_fake_transactions(10)
    create_sandbox_transactions(access_token, fake_txs)
    accounts = fetch_accounts(access_token)
    time.sleep(5)
    transactions = fetch_all_transactions(access_token)
    insert_transactions_sql(transactions)


    # Minimal preview to confirm it’s working
    preview = {
        "accounts": [
            {
                "account_id": a["account_id"],
                "name": a.get("name"),
                "subtype": a.get("subtype"),
                "mask": a.get("mask"),
                "balances": a.get("balances", {}),
            }
            for a in accounts
        ],
        "transactions_sample": [
            {
                "transaction_id": t["transaction_id"],
                "date": t.get("date"),
                "name": t.get("name"),
                "amount": t.get("amount"),
                "merchant_name": t.get("merchant_name"),
                "category": (t.get("personal_finance_category") or {}).get("primary")
                             or (t.get("category") or [None])[0],
                "iso_currency_code": t.get("iso_currency_code") or t.get("unofficial_currency_code"),
                "account_id": t.get("account_id"),
                "pending": t.get("pending"),
            }
            for t in transactions[:10]
        ],
        "total_transactions": len(transactions),
    }
    print(json.dumps(preview, indent=2, default=str))

if __name__ == "__main__":
    main()
