import logging
from typing import Optional, List
import logging
from typing import Optional, List, Dict
import pyodbc
from app.db import get_connection
from app.database import get_db_session
from app.models.db_models import PlaidUser
from app.security.encryption import encryption_service
from app.models.db_models import Account, Transaction
from app.external_services.plaid_service import plaid_service
from datetime import datetime

logger = logging.getLogger(__name__)
from app.models.db_models import Account, Transaction
from plaid.model.transactions_sync_request import TransactionsSyncRequest
from datetime import datetime

logger = logging.getLogger(__name__)

class PlaidRepository:
    """Service for managing Plaid user data in the database."""
    
    def create_plaid_user(
        self, 
        user_id: int, 
        access_token: str, 
        item_id: str, 
        institution_name: Optional[str] = None
    ) -> int:
        """Create a new Plaid user record with encrypted access token."""
        try:
            # Encrypt the access token before storing
            encrypted_token = encryption_service.encrypt(access_token)
            
            with get_db_session() as db:
                new_plaid_user = PlaidUser(
                    user_id=user_id,
                    access_token=encrypted_token,
                    item_id=item_id,
                    institution_name=institution_name
                )
                db.add(new_plaid_user)
                db.commit()
                db.refresh(new_plaid_user)
                
                return new_plaid_user.id
        except pyodbc.Error as e:
            logger.error(f"Database error creating Plaid user: {e}")
            raise Exception(f"Failed to create Plaid user: {str(e)}")
    
    def get_plaid_user_by_user_id(self, user_id: int) -> Optional[PlaidUser]:
        """Get Plaid user by user ID."""
        try:
            with get_db_session() as db:
                plaid_user = db.query(PlaidUser).filter(PlaidUser.user_id == user_id).first()
                # Decrypt access_token immediately after DB retrieval so callers always get plaintext
                if plaid_user and hasattr(plaid_user, 'access_token') and plaid_user.access_token:
                    try:
                        plaid_user.access_token = encryption_service.decrypt(plaid_user.access_token)
                    except Exception:
                        # If decryption fails, leave the token as-is to surface the error later
                        logger.exception("Failed to decrypt access token for plaid_user (user_id=%s)", user_id)
                return plaid_user
        except pyodbc.Error as e:
            logger.error(f"Database error getting Plaid user by user ID: {e}")
            raise Exception(f"Failed to get Plaid user: {str(e)}")
    
    def get_plaid_user_by_item_id(self, item_id: str) -> Optional[PlaidUser]:
        """Get Plaid user by item ID."""
        try:
            with get_db_session() as db:
                plaid_user = db.query(PlaidUser).filter(PlaidUser.item_id == item_id).first()
                if plaid_user and hasattr(plaid_user, 'access_token'):
                    # Decrypt the access token before returning
                    plaid_user.access_token = encryption_service.decrypt(plaid_user.access_token)
                return plaid_user
        except pyodbc.Error as e:
            logger.error(f"Database error getting Plaid user by item ID: {e}")
            raise Exception(f"Failed to get Plaid user: {str(e)}")
    
    def get_all_plaid_users_for_user(self, user_id: int) -> List[PlaidUser]:
        """Get all Plaid connections for a user."""
        try:
            with get_db_session() as db:
                print("Getting all Plaid users for user id: ", user_id)
                plaid_users = db.query(PlaidUser).filter(PlaidUser.user_id == user_id).all()
                # Decrypt access_token on each record
                for pu in plaid_users:
                    if hasattr(pu, 'access_token') and pu.access_token:
                        try:
                            pu.access_token = encryption_service.decrypt(pu.access_token)
                        except Exception:
                            logger.exception("Failed to decrypt access token for plaid_user id=%s", getattr(pu, 'id', None))
                return plaid_users
        except pyodbc.Error as e:
            logger.error(f"Database error getting all Plaid users for user: {e}")
            raise Exception(f"Failed to get Plaid users: {str(e)}")
    
    def update_institution_name(self, plaid_user_id: int, institution_name: str) -> bool:
        """Update institution name for a Plaid user."""
        try:
            with get_db_session() as db:
                plaid_user = db.query(PlaidUser).filter(PlaidUser.id == plaid_user_id).first()
                if plaid_user:
                    plaid_user.institution_name = institution_name
                    db.commit()
                    db.refresh(plaid_user)
                    return True
                return False
        except pyodbc.Error as e:
            logger.error(f"Database error updating institution name: {e}")
            raise Exception(f"Failed to update institution name: {str(e)}")
    
    def delete_plaid_user(self, plaid_user_id: int) -> bool:
        """Delete a Plaid user record."""
        try:
            with get_db_session() as db:
                print("Deleting plaid user id - repo: ", plaid_user_id)
                plaid_user = db.query(PlaidUser).filter(PlaidUser.id == plaid_user_id).first()
                if plaid_user:
                    db.delete(plaid_user)
                    db.commit()
                    return True
                return False
        except pyodbc.Error as e:
            logger.error(f"Database error deleting Plaid user: {e}")
            raise Exception(f"Failed to delete Plaid user: {str(e)}")

    # -----------------------------
    # Upsert helpers and sync
    # -----------------------------
    def upsert_accounts(self, item_id: str, accounts: List[Dict]) -> int:
        """Insert or update accounts for a given item_id. Returns number processed."""
        count = 0
        try:
            with get_db_session() as db:
                plaid_user = db.query(PlaidUser).filter(PlaidUser.item_id == item_id).first()
                if not plaid_user:
                    raise Exception("Plaid user not found")

                for acct in accounts:
                    acc = db.query(Account).filter(Account.account_id == acct.get('account_id')).first()
                    if acc:
                        acc.name = acct.get('name')
                        acc.type = acct.get('type')
                        acc.subtype = acct.get('subtype')
                        acc.balance_current = acct.get('balance')
                        acc.currency = acct.get('currency')
                    else:
                        acc = Account(
                            plaid_user_id=plaid_user.id,
                            account_id=acct.get('account_id'),
                            name=acct.get('name'),
                            type=acct.get('type'),
                            subtype=acct.get('subtype'),
                            balance_current=acct.get('balance'),
                            currency=acct.get('currency')
                        )
                        db.add(acc)

                    count += 1

                db.commit()
            return count
        except Exception as e:
            logger.error(f"Error upserting accounts: {e}")
            raise

    def upsert_transactions(self, item_id: str, transactions: List[Dict]) -> int:
        """Insert or update transactions. Resolve account via Account.account_id."""
        count = 0
        try:
            with get_db_session() as db:
                for tx in transactions:
                    account = db.query(Account).filter(Account.account_id == tx.get('account_id')).first()
                    if not account:
                        logger.warning(f"Skipping tx for unknown account_id={tx.get('account_id')}")
                        continue

                    existing = db.query(Transaction).filter(Transaction.transaction_id == tx.get('transaction_id')).first()

                    # normalize date
                    posted = tx.get('date')
                    if isinstance(posted, str):
                        try:
                            posted_dt = datetime.fromisoformat(posted)
                        except Exception:
                            posted_dt = datetime.strptime(posted, "%Y-%m-%d")
                    else:
                        posted_dt = posted

                    if existing:
                        existing.amount = tx.get('amount')
                        existing.date_posted = posted_dt
                        existing.merchant_name = tx.get('merchant_name')
                        existing.description = tx.get('name')
                        existing.is_pending = 1 if tx.get('pending') else 0
                        existing.category = ','.join(tx.get('category')) if isinstance(tx.get('category'), list) else (tx.get('category') or None)
                    else:
                        new_tx = Transaction(
                            account_id=account.id,
                            transaction_id=tx.get('transaction_id'),
                            amount=tx.get('amount'),
                            date_posted=posted_dt,
                            merchant_name=tx.get('merchant_name'),
                            description=tx.get('name'),
                            iso_currency_code=tx.get('iso_currency_code') if tx.get('iso_currency_code') else None,
                            category=','.join(tx.get('category')) if isinstance(tx.get('category'), list) else (tx.get('category') or None),
                            is_pending=1 if tx.get('pending') else 0,
                        )
                        db.add(new_tx)

                    count += 1

                db.commit()
            return count
        except Exception as e:
            logger.error(f"Error upserting transactions: {e}")
            raise

    def sync_item_transactions(self, item_id: str) -> dict:
        """Sync accounts + transactions for an item using Plaid's transactions/sync incremental flow.

        Returns dict with counts {accounts_synced, transactions_synced}
        """
        # fetch PlaidUser
        pu = self.get_plaid_user_by_item_id(item_id)
        if not pu:
            raise Exception("Plaid user not found")

        # Use PlaidService.sync_transactions in incremental mode to fetch all added transactions and final cursor
        try:
            resp = plaid_service.sync_transactions(
                access_token=pu.access_token,
                account_ids=None,
                cursor=pu.cursor
            )
        except Exception as e:
            logger.error(f"Error calling plaid_service.sync_transactions: {e}")
            raise

        # resp should be {"transactions": List[PlaidTransaction], "cursor": str}
        transactions = resp.get('transactions', []) if isinstance(resp, dict) else []
        new_cursor = resp.get('cursor') if isinstance(resp, dict) else None

        # prepare dicts for upsert
        tx_dicts = []
        for t in transactions:
            tx_dicts.append({
                'transaction_id': t.transaction_id,
                'account_id': t.account_id,
                'amount': t.amount,
                'date': t.date,
                'merchant_name': t.merchant_name,
                'name': t.name,
                'pending': t.pending,
                'category': t.category,
                'iso_currency_code': None,
            })

        transactions_synced = 0
        if tx_dicts:
            transactions_synced = self.upsert_transactions(item_id, tx_dicts)

        # persist cursor
        try:
            with get_db_session() as db:
                record = db.query(PlaidUser).filter(PlaidUser.item_id == item_id).first()
                if record:
                    record.cursor = new_cursor
                    db.commit()
        except Exception as e:
            logger.warning(f"Failed to persist cursor: {e}")

        return {"accounts_synced": 0, "transactions_synced": transactions_synced}

    # -----------------------------
    # Sync helpers using SQLAlchemy
    # -----------------------------
    def upsert_accounts(self, item_id: str, accounts: List[dict]) -> int:
        """Upsert accounts into DB using SQLAlchemy. Returns number of accounts upserted."""
        count = 0
        try:
            with get_db_session() as db:
                # lookup plaid_user id
                plaid_user = db.query(PlaidUser).filter(PlaidUser.item_id == item_id).first()
                if not plaid_user:
                    raise Exception("Plaid user not found")

                for acct in accounts:
                    existing = db.query(Account).filter(Account.account_id == acct.get('account_id')).first()
                    if existing:
                        existing.name = acct.get('name')
                        existing.type = acct.get('type')
                        existing.subtype = acct.get('subtype')
                        existing.balance_current = acct.get('balance')
                        existing.currency = acct.get('currency')
                        existing.nickname = acct.get('nickname') or existing.nickname
                    else:
                        new_acc = Account(
                            plaid_user_id=plaid_user.id,
                            account_id=acct.get('account_id'),
                            name=acct.get('name'),
                            type=acct.get('type'),
                            subtype=acct.get('subtype'),
                            balance_current=acct.get('balance'),
                            currency=acct.get('currency'),
                            nickname=acct.get('nickname') if acct.get('nickname') else None,
                        )
                        db.add(new_acc)
                    count += 1

                db.commit()
            return count
        except Exception as e:
            logger.error(f"Error upserting accounts: {e}")
            raise

    def upsert_transactions(self, item_id: str, transactions: List[dict]) -> int:
        """Upsert transactions. Resolve account via Account.account_id. Returns number inserted/updated count."""
        count = 0
        try:
            with get_db_session() as db:
                for tx in transactions:
                    # resolve account local id
                    account = db.query(Account).filter(Account.account_id == tx.get('account_id')).first()
                    if not account:
                        # skip transactions for unknown accounts
                        logger.warning(f"Account not found for transaction account_id={tx.get('account_id')}")
                        continue

                    existing = db.query(Transaction).filter(Transaction.transaction_id == tx.get('transaction_id')).first()
                    posted_at = tx.get('date')
                    # Normalize posted_at into a timezone-aware datetime (UTC).
                    # Accepts: datetime, date, ISO strings (with Z or timezone), and
                    # strings with >6 fractional second digits (truncates to microseconds).
                    def _to_datetime(val):
                        if val is None:
                            return None
                        # already a datetime
                        if isinstance(val, datetime):
                            if val.tzinfo is None:
                                return val.replace(tzinfo=timezone.utc)
                            return val
                        # plain date -> convert to midnight UTC
                        if isinstance(val, date):
                            return datetime.combine(val, datetime.min.time()).replace(tzinfo=timezone.utc)
                        # parse strings
                        if isinstance(val, str):
                            s = val
                            # normalize Z suffix
                            if s.endswith('Z'):
                                s = s[:-1] + '+00:00'

                            # handle long fractional seconds: ensure at most 6 digits
                            if '.' in s:
                                # split fractional and timezone parts
                                main, frac_tz = s.split('.', 1)
                                # frac_tz may contain timezone (+/-) or nothing
                                tz_idx = None
                                for idx, ch in enumerate(frac_tz):
                                    if ch in ['+', '-']:
                                        tz_idx = idx
                                        break
                                if tz_idx is not None:
                                    frac = frac_tz[:tz_idx]
                                    tz = frac_tz[tz_idx:]
                                else:
                                    # no explicit tz in frac_tz
                                    frac = frac_tz
                                    tz = ''
                                # remove any trailing Z
                                if frac.endswith('Z'):
                                    frac = frac[:-1]
                                if len(frac) > 6:
                                    frac = frac[:6]
                                s = main + '.' + frac + tz

                            try:
                                dt = datetime.fromisoformat(s)
                                if dt.tzinfo is None:
                                    dt = dt.replace(tzinfo=timezone.utc)
                                return dt
                            except Exception:
                                # fallback to date-only
                                try:
                                    dt = datetime.strptime(s, '%Y-%m-%d')
                                    return dt.replace(tzinfo=timezone.utc)
                                except Exception:
                                    raise

                        # unknown type - return as-is
                        return val

                    # imports used by helper
                    from datetime import timezone, date

                    posted_at = _to_datetime(posted_at)

                    if existing:
                        existing.amount = tx.get('amount')
                        existing.date_posted = posted_at
                        existing.merchant_name = tx.get('merchant_name')
                        existing.description = tx.get('name')
                        existing.is_pending = 1 if tx.get('pending') else 0
                        existing.category = ','.join(tx.get('category')) if tx.get('category') and isinstance(tx.get('category'), list) else (tx.get('category') or None)
                    else:
                        new_tx = Transaction(
                            account_id=account.account_id,
                            transaction_id=tx.get('transaction_id'),
                            amount=tx.get('amount'),
                            date_posted=posted_at,
                            merchant_name=tx.get('merchant_name'),
                            description=tx.get('name'),
                            iso_currency_code=tx.get('iso_currency_code') if tx.get('iso_currency_code') else None,
                            category=','.join(tx.get('category')) if tx.get('category') and isinstance(tx.get('category'), list) else (tx.get('category') or None),
                            is_pending=1 if tx.get('pending') else 0,
                        )
                        db.add(new_tx)
                    count += 1

                db.commit()
            return count
        except Exception as e:
            logger.error(f"Error upserting transactions: {e}")
            raise

    def sync_item_transactions(self, item_id: str) -> dict:
        """Run Plaid transactions/sync for the given item_id and persist results.

        Uses Plaid's incremental sync cursor loop. Returns counts.
        """
        # get plaid user record
        plaid_user = self.get_plaid_user_by_item_id(item_id)
        if not plaid_user:
            raise Exception("Plaid user not found")

        # Accounts - use service to get accounts and upsert
        accounts = plaid_service.get_accounts(plaid_user.access_token)
        acct_dicts = []
        for a in accounts:
            acct_dicts.append({
                'account_id': a.account_id,
                'name': a.name,
                'type': a.type,
                'subtype': a.subtype,
                'balance': a.balance,
                'currency': a.currency,
            })

        accounts_synced = self.upsert_accounts(item_id, acct_dicts)

        # Transactions sync (cursor loop)
        cursor = plaid_user.cursor if hasattr(plaid_user, 'cursor') else None
        total_tx_synced = 0

        while True:
            # build request — `get_plaid_user_by_item_id` decrypts the token at the DB boundary, so use it directly
            req = TransactionsSyncRequest(access_token=plaid_user.access_token)
            if cursor:
                req.cursor = cursor

            # call Plaid
            resp = plaid_service.client.transactions_sync(req).to_dict()

            added = resp.get('added', [])
            txs_to_upsert = []
            for t in added:
                # map category
                cat = None
                if t.get('personal_finance_category'):
                    cat = [t['personal_finance_category'].get('primary')]
                elif t.get('category'):
                    cat = t.get('category')

                txs_to_upsert.append({
                    'transaction_id': t.get('transaction_id'),
                    'account_id': t.get('account_id'),
                    'amount': t.get('amount'),
                    'date': t.get('date'),
                    'merchant_name': t.get('merchant_name'),
                    'name': t.get('name'),
                    'pending': t.get('pending', False),
                    'category': cat,
                    'iso_currency_code': t.get('iso_currency_code')
                })

            if txs_to_upsert:
                count = self.upsert_transactions(item_id, txs_to_upsert)
                total_tx_synced += count

            # handle cursor and has_more
            has_more = resp.get('has_more', False)
            new_cursor = resp.get('next_cursor') or resp.get('cursor')

            # persist new cursor on PlaidUser
            try:
                with get_db_session() as db:
                    pu = db.query(PlaidUser).filter(PlaidUser.item_id == item_id).first()
                    if pu:
                        pu.cursor = new_cursor
                        db.commit()
            except Exception as e:
                logger.warning(f"Unable to persist cursor for item {item_id}: {e}")

            if not has_more:
                break

            cursor = new_cursor

        return {"accounts_synced": accounts_synced, "transactions_synced": total_tx_synced}

# Global instance
plaid_repository = PlaidRepository()