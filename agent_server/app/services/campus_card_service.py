from decimal import Decimal, InvalidOperation

from app.db.models import CampusCardAccount
from app.db.repositories.campus_card_repository import CampusCardRepository


class CampusCardService:
    def __init__(self, campus_card_repository: CampusCardRepository) -> None:
        self.campus_card_repository = campus_card_repository

    def get_or_create_account(self, user_id: int) -> CampusCardAccount:
        account = self.campus_card_repository.get_account_by_user_id(user_id)
        if account is not None:
            return account

        card_no = f"CARD-{user_id:06d}"
        return self.campus_card_repository.create_account(
            user_id=user_id,
            card_no=card_no,
            balance=Decimal("0.00"),
            status="active",
        )

    def get_balance(self, user_id: int) -> dict:
        account = self.get_or_create_account(user_id)
        self.campus_card_repository.commit()

        return {
            "account_id": account.id,
            "card_no": account.card_no,
            "balance": str(account.balance),
            "status": account.status,
        }

    def topup(self, *, user_id: int, amount: str, source: str = "agent") -> dict:
        try:
            decimal_amount = Decimal(amount)
        except InvalidOperation as exc:
            raise ValueError("Invalid amount format") from exc

        if decimal_amount <= 0:
            raise ValueError("Topup amount must be greater than 0")

        account = self.get_or_create_account(user_id)

        if account.status != "active":
            raise ValueError("Campus card account is not active")

        new_balance = Decimal(account.balance) + decimal_amount

        try:
            self.campus_card_repository.update_balance(
                account=account,
                new_balance=new_balance,
            )

            transaction = self.campus_card_repository.create_transaction(
                account_id=account.id,
                txn_type="topup",
                amount=decimal_amount,
                balance_after=new_balance,
                source=source,
                remark="Topup via AI agent",
            )

            self.campus_card_repository.commit()

            return {
                "account_id": account.id,
                "card_no": account.card_no,
                "txn_id": transaction.id,
                "amount": str(decimal_amount),
                "balance_after": str(new_balance),
                "status": account.status,
            }
        except Exception:
            self.campus_card_repository.rollback()
            raise