from app.db.models import ScheduleEntry
from app.db.repositories.schedule_repository import ScheduleRepository


class ScheduleService:
    def __init__(self, schedule_repository: ScheduleRepository) -> None:
        self.schedule_repository = schedule_repository

    def list_my_schedule(
        self,
        user_id: int,
        semester: str | None = None,
        weekday: int | None = None,
    ) -> list[ScheduleEntry]:
        return self.schedule_repository.list_by_user_id(
            user_id=user_id,
            semester=semester,
            weekday=weekday,
        )