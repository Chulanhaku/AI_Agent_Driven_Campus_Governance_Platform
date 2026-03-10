from datetime import date, timedelta

from app.db.repositories.leave_repository import LeaveRepository


class LeaveService:
    def __init__(self, leave_repository: LeaveRepository) -> None:
        self.leave_repository = leave_repository

    def create_leave_request(
        self,
        *,
        user_id: int,
        days: int,
        reason: str,
        leave_type: str = "sick",
    ) -> dict:
        if days <= 0:
            raise ValueError("Leave days must be greater than 0")

        if not reason.strip():
            raise ValueError("Leave reason cannot be empty")

        today = date.today()
        start_date = today
        end_date = today + timedelta(days=days - 1)

        try:
            leave_request = self.leave_repository.create_leave_request(
                user_id=user_id,
                leave_type=leave_type,
                start_date=start_date,
                end_date=end_date,
                reason=reason.strip(),
                status="pending",
                submitted_at=today,
            )
            self.leave_repository.commit()

            return {
                "leave_request_id": leave_request.id,
                "leave_type": leave_request.leave_type,
                "start_date": str(leave_request.start_date),
                "end_date": str(leave_request.end_date),
                "reason": leave_request.reason,
                "status": leave_request.status,
            }
        except Exception:
            self.leave_repository.rollback()
            raise

    def list_my_leave_requests(self, user_id: int) -> list:
        return self.leave_repository.list_by_user_id(user_id)