import os
import json
import datetime as dt
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

import plaid
from plaid.api import plaid_api
from plaid.model.sandbox_public_token_create_request import SandboxPublicTokenCreateRequest
from plaid.model.sandbox_item_fire_webhook_request import SandboxItemFireWebhookRequest
from plaid.model.products import Products
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.transactions_sync_request import TransactionsSyncRequest
from plaid.model.accounts_get_request import AccountsGetRequest

PLAID_CLIENT_ID = os.getenv("PLAID_CLIENT_ID")
PLAID_SECRET = os.getenv("PLAID_SECRET")

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

def create_sandbox_transactions(access_token: str, count: int = 20):
    """
    Force-create fake transactions in the Plaid sandbox.
    """
    body = {
        "access_token": access_token,
        "count": count,
    }
    response = client.api_client.call_api(
        "/sandbox/transactions/create", "POST",
        body=body,
        response_type="object"
    )
    print("✨ Created sandbox transactions:", response[0])

def fetch_all_transactions(access_token: str, count: int = 500) -> list[dict]:
    """Use transactions_sync to retrieve all added transactions (paginated by cursor)."""
    txs: list[dict] = []
    cursor: str | None = None

    while True:
        if cursor:
            req = TransactionsSyncRequest(access_token=access_token, cursor=cursor, count=count)
        else:
            req = TransactionsSyncRequest(access_token=access_token, count=count)

        res = client.transactions_sync(req).to_dict()

        txs.extend(res.get("added", []))
        cursor = res.get("next_cursor")

        if not res.get("has_more"):
            break

    return txs

def main():
    access_token = create_access_token()
    accounts = fetch_accounts(access_token)
    create_sandbox_transactions(access_token, count=30)
    transactions = fetch_all_transactions(access_token)

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
