from pydantic import BaseModel


class CampusCardBalanceResponseSchema(BaseModel):
    account_id: int
    card_no: str
    balance: str
    status: str