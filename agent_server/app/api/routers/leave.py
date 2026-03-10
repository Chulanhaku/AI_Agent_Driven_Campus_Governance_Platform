from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db_dep
from app.db.models import User
from app.db.repositories.leave_repository import LeaveRepository
from app.services.leave_service import LeaveService

router = APIRouter(prefix="/leave", tags=["leave"])


def get_leave_service(db: Session = Depends(get_db_dep)) -> LeaveService:
    repository = LeaveRepository(db)
    return LeaveService(repository)


@router.get("/me")
def list_my_leave_requests(
    current_user: User = Depends(get_current_user),
    leave_service: LeaveService = Depends(get_leave_service),
) -> list[dict]:
    items = leave_service.list_my_leave_requests(user_id=current_user.id)

    results = []
    for item in items:
        results.append(
            {
                "leave_request_id": item.id,
                "leave_type": item.leave_type,
                "start_date": str(item.start_date),
                "end_date": str(item.end_date),
                "reason": item.reason,
                "status": item.status,
            }
        )
    return results