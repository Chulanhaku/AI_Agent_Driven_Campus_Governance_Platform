from datetime import datetime

from sqlalchemy.orm import Session, joinedload

from app.db.models import ResourceBooking


class ResourceBookingRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_booking(
        self,
        *,
        user_id: int,
        resource_id: int,
        booking_type: str,
        start_time: datetime,
        end_time: datetime,
        status: str = "confirmed",
        check_in_deadline: datetime | None = None,
    ) -> ResourceBooking:
        booking = ResourceBooking(
            user_id=user_id,
            resource_id=resource_id,
            booking_type=booking_type,
            start_time=start_time,
            end_time=end_time,
            status=status,
            check_in_deadline=check_in_deadline,
        )
        self.db.add(booking)
        self.db.flush()
        return booking

    def get_by_id_and_user_id(
        self,
        *,
        booking_id: int,
        user_id: int,
    ) -> ResourceBooking | None:
        return (
            self.db.query(ResourceBooking)
            .options(joinedload(ResourceBooking.resource))
            .filter(
                ResourceBooking.id == booking_id,
                ResourceBooking.user_id == user_id,
            )
            .first()
        )

    def list_expired_unchecked_bookings(
        self,
        *,
        now: datetime,
    ) -> list[ResourceBooking]:
        return (
            self.db.query(ResourceBooking)
            .options(joinedload(ResourceBooking.resource))
            .filter(
                ResourceBooking.status == "confirmed",
                ResourceBooking.check_in_deadline.is_not(None),
                ResourceBooking.check_in_deadline < now,
                ResourceBooking.checked_in_at.is_(None),
            )
            .all()
        )

    def update_status(
        self,
        *,
        booking: ResourceBooking,
        status: str,
        checked_in_at: datetime | None = None,
        no_show_reason: str | None = None,
    ) -> ResourceBooking:
        booking.status = status
        if checked_in_at is not None:
            booking.checked_in_at = checked_in_at
        if no_show_reason is not None:
            booking.no_show_reason = no_show_reason
        self.db.flush()
        return booking

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()