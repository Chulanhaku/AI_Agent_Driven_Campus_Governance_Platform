from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db_dep
from app.db.models import User
from app.db.repositories.integrity_score_repository import IntegrityScoreRepository
from app.db.repositories.resource_booking_repository import ResourceBookingRepository
from app.services.resource_booking_service import ResourceBookingService

router = APIRouter(prefix="/resource-bookings", tags=["resource-bookings"])


def get_resource_booking_service(
    db: Session = Depends(get_db_dep),
) -> ResourceBookingService:
    resource_booking_repository = ResourceBookingRepository(db)
    integrity_score_repository = IntegrityScoreRepository(db)

    return ResourceBookingService(
        resource_booking_repository=resource_booking_repository,
        integrity_score_repository=integrity_score_repository,
    )


@router.post("/{booking_id}/check-in")
def check_in_booking(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    resource_booking_service: ResourceBookingService = Depends(get_resource_booking_service),
) -> dict:
    try:
        return resource_booking_service.mark_checked_in(
            booking_id=booking_id,
            user_id=current_user.id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.post("/expire-no-show")
def expire_no_show_bookings(
    resource_booking_service: ResourceBookingService = Depends(get_resource_booking_service),
) -> dict:
    # 这一版先给调试/本地手动触发用
    return resource_booking_service.expire_no_show_bookings(now=datetime.now())