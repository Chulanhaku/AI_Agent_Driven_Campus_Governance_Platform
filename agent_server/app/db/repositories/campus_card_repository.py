from decimal import Decimal

from sqlalchemy.orm import Session

from app.db.models import CampusCardAccount, CampusCardTransaction


class CampusCardRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_account_by_user_id(self, user_id: int) -> CampusCardAccount | None:
        return (
            self.db.query(CampusCardAccount)
            .filter(CampusCardAccount.user_id == user_id)
            .first()
        )

    def create_account(
        self,
        *,
        user_id: int,
        card_no: str,
        balance: Decimal = Decimal("0.00"),
        status: str = "active",
    ) -> CampusCardAccount:
        account = CampusCardAccount(
            user_id=user_id,
            card_no=card_no,
            balance=balance,
            status=status,
        )
        self.db.add(account)
        self.db.flush()
        return account

    def update_balance(
        self,
        *,
        account: CampusCardAccount,
        new_balance: Decimal,
    ) -> CampusCardAccount:
        account.balance = new_balance
        self.db.flush()
        return account

    def create_transaction(
        self,
        *,
        account_id: int,
        txn_type: str,
        amount: Decimal,
        balance_after: Decimal,
        source: str | None = None,
        remark: str | None = None,
    ) -> CampusCardTransaction:
        transaction = CampusCardTransaction(
            account_id=account_id,
            txn_type=txn_type,
            amount=amount,
            balance_after=balance_after,
            source=source,
            remark=remark,
        )
        self.db.add(transaction)
        self.db.flush()
        return transaction

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()