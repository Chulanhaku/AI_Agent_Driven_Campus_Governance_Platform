from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db_dep
from app.db.models import User
from app.db.repositories.notification_repository import NotificationRepository
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["notifications"])


def get_notification_service(
    db: Session = Depends(get_db_dep),
) -> NotificationService:
    repository = NotificationRepository(db)
    return NotificationService(repository)


@router.get("/me")
def list_my_notifications(
    unread_only: bool = Query(default=False),
    limit: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    notification_service: NotificationService = Depends(get_notification_service),
) -> list[dict]:
    return notification_service.list_my_notifications(
        user_id=current_user.id,
        unread_only=unread_only,
        limit=limit,
    )


@router.post("/{notification_id}/read")
def mark_notification_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    notification_service: NotificationService = Depends(get_notification_service),
) -> dict:
    try:
        return notification_service.mark_my_notification_as_read(
            notification_id=notification_id,
            user_id=current_user.id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc