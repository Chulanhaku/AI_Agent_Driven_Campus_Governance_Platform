from datetime import date

from sqlalchemy.orm import Session

from app.db.models import LeaveRequest


class LeaveRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_leave_request(
        self,
        *,
        user_id: int,
        leave_type: str,
        start_date: date,
        end_date: date,
        reason: str,
        status: str = "pending",
        submitted_at: date | None = None,
    ) -> LeaveRequest:
        leave_request = LeaveRequest(
            user_id=user_id,
            leave_type=leave_type,
            start_date=start_date,
            end_date=end_date,
            reason=reason,
            status=status,
            submitted_at=submitted_at,
        )
        self.db.add(leave_request)
        self.db.flush()
        return leave_request

    def get_by_id_and_user_id(
        self,
        leave_request_id: int,
        user_id: int,
    ) -> LeaveRequest | None:
        return (
            self.db.query(LeaveRequest)
            .filter(
                LeaveRequest.id == leave_request_id,
                LeaveRequest.user_id == user_id,
            )
            .first()
        )

    def list_by_user_id(self, user_id: int) -> list[LeaveRequest]:
        return (
            self.db.query(LeaveRequest)
            .filter(LeaveRequest.user_id == user_id)
            .order_by(LeaveRequest.id.desc())
            .all()
        )

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()