from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db_dep
from app.api.schemas.campus_card import CampusCardBalanceResponseSchema
from app.db.models import User
from app.db.repositories.campus_card_repository import CampusCardRepository
from app.services.campus_card_service import CampusCardService

router = APIRouter(prefix="/campus-card", tags=["campus-card"])


def get_campus_card_service(db: Session = Depends(get_db_dep)) -> CampusCardService:
    repository = CampusCardRepository(db)
    return CampusCardService(repository)


@router.get("/balance", response_model=CampusCardBalanceResponseSchema)
def get_balance(
    current_user: User = Depends(get_current_user),
    campus_card_service: CampusCardService = Depends(get_campus_card_service),
) -> CampusCardBalanceResponseSchema:
    data = campus_card_service.get_balance(user_id=current_user.id)
    return CampusCardBalanceResponseSchema(**data)