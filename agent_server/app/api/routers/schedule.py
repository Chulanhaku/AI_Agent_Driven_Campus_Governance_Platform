from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db_dep
from app.api.schemas.schedule import ScheduleListResponseSchema
from app.db.models import User
from app.db.repositories.schedule_repository import ScheduleRepository
from app.services.schedule_service import ScheduleService

router = APIRouter(prefix="/schedule", tags=["schedule"])


def get_schedule_service(db: Session = Depends(get_db_dep)) -> ScheduleService:
    schedule_repository = ScheduleRepository(db)
    return ScheduleService(schedule_repository)


@router.get("/me", response_model=ScheduleListResponseSchema)
def get_my_schedule(
    semester: str | None = Query(default=None),
    weekday: int | None = Query(default=None, ge=1, le=7),
    current_user: User = Depends(get_current_user),
    schedule_service: ScheduleService = Depends(get_schedule_service),
) -> ScheduleListResponseSchema:
    items = schedule_service.list_my_schedule(
        user_id=current_user.id,
        semester=semester,
        weekday=weekday,
    )

    return ScheduleListResponseSchema(
        items=items,
        total=len(items),
    )