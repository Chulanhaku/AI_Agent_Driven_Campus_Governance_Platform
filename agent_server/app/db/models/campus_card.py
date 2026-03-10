from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class CampusCardAccount(Base, TimestampMixin):
    __tablename__ = "campus_card_accounts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    card_no: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    balance: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False, index=True)

    user = relationship("User", back_populates="campus_card_account")
    transactions = relationship(
        "CampusCardTransaction",
        back_populates="account",
        cascade="all, delete-orphan",
        order_by="CampusCardTransaction.id.asc()",
    )


class CampusCardTransaction(Base, TimestampMixin):
    __tablename__ = "campus_card_transactions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    account_id: Mapped[int] = mapped_column(
        ForeignKey("campus_card_accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    txn_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    balance_after: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    source: Mapped[str | None] = mapped_column(String(50), nullable=True)
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)

    account = relationship("CampusCardAccount", back_populates="transactions")