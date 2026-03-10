from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class CampusCardAccountSchema(BaseModel):
    """对应 CampusCardAccount Model —— 展示当前用户的校园卡信息"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    card_no: str
    balance: Decimal
    status: str


class CampusCardTransactionSchema(BaseModel):
    """对应 CampusCardTransaction Model —— 单条交易流水"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    txn_type: str
    amount: Decimal
    balance_after: Decimal
    source: str | None
    remark: str | None
    created_at: datetime


class CampusCardTransactionListResponseSchema(BaseModel):
    
    items: list[CampusCardTransactionSchema]
    total: int

