from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db_dep
from app.api.schemas.campus_card import (
    CampusCardAccountSchema,
    CampusCardTransactionListResponseSchema,
)
from app.db.models import User
from app.db.repositories.campus_card_repository import CampusCardRepository
from app.services.campus_card_service import CampusCardService

router = APIRouter(prefix="/campus-card", tags=["campus-card"])


def get_campus_card_service(db: Session = Depends(get_db_dep)) -> CampusCardService:
    campus_card_repository = CampusCardRepository(db)
    return CampusCardService(campus_card_repository)


@router.get("/me", response_model=CampusCardAccountSchema)
def get_my_card(
    current_user: User = Depends(get_current_user),
    campus_card_service: CampusCardService = Depends(get_campus_card_service),
) -> CampusCardAccountSchema:
    return campus_card_service.get_account_by_user_id(current_user.id)


@router.get("/me/transactions", response_model=CampusCardTransactionListResponseSchema)
def get_my_transactions(
    txn_type: str | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    campus_card_service: CampusCardService = Depends(get_campus_card_service),
) -> CampusCardTransactionListResponseSchema:
    items = campus_card_service.list_transactions(
        user_id=current_user.id,
        txn_type=txn_type,
    )

    return CampusCardTransactionListResponseSchema(
        items=items,
        total=len(items),
    )
