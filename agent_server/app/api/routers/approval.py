from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db_dep
from app.db.models import User
from app.db.repositories.approval_request_repository import ApprovalRequestRepository
from app.db.repositories.approval_template_repository import ApprovalTemplateRepository
from app.db.repositories.notification_repository import NotificationRepository
from app.db.repositories.user_repository import UserRepository
from app.services.notification_service import NotificationService
from app.services.zero_form_approval_service import ZeroFormApprovalService

router = APIRouter(prefix="/approvals", tags=["approvals"])


def get_zero_form_approval_service(
    db: Session = Depends(get_db_dep),
) -> ZeroFormApprovalService:
    approval_template_repository = ApprovalTemplateRepository(db)
    approval_request_repository = ApprovalRequestRepository(db)
    user_repository = UserRepository(db)
    notification_repository = NotificationRepository(db)
    notification_service = NotificationService(notification_repository)

    return ZeroFormApprovalService(
        approval_template_repository=approval_template_repository,
        approval_request_repository=approval_request_repository,
        user_repository=user_repository,
        notification_service=notification_service,
    )


@router.get("/pending/me")
def list_my_pending_approvals(
    limit: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    zero_form_approval_service: ZeroFormApprovalService = Depends(get_zero_form_approval_service),
) -> list[dict]:
    return zero_form_approval_service.list_pending_for_approver(
        approver_user_id=current_user.id,
        limit=limit,
    )


@router.post("/{request_id}/approve")
def approve_request(
    request_id: int,
    current_user: User = Depends(get_current_user),
    zero_form_approval_service: ZeroFormApprovalService = Depends(get_zero_form_approval_service),
) -> dict:
    try:
        return zero_form_approval_service.approve_request(
            request_id=request_id,
            approver_user_id=current_user.id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.post("/{request_id}/reject")
def reject_request(
    request_id: int,
    current_user: User = Depends(get_current_user),
    zero_form_approval_service: ZeroFormApprovalService = Depends(get_zero_form_approval_service),
) -> dict:
    try:
        return zero_form_approval_service.reject_request(
            request_id=request_id,
            approver_user_id=current_user.id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc