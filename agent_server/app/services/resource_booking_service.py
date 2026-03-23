from datetime import datetime, timedelta

from app.db.repositories.integrity_score_repository import IntegrityScoreRepository
from app.db.repositories.resource_booking_repository import ResourceBookingRepository


class ResourceBookingService:
    def __init__(
        self,
        resource_booking_repository: ResourceBookingRepository,
        integrity_score_repository: IntegrityScoreRepository,
    ) -> None:
        self.resource_booking_repository = resource_booking_repository
        self.integrity_score_repository = integrity_score_repository

    def create_booking(
        self,
        *,
        user_id: int,
        resource_id: int,
        booking_type: str,
        start_time: datetime,
        end_time: datetime,
    ) -> dict:
        try:
            check_in_deadline = start_time + timedelta(minutes=15)

            booking = self.resource_booking_repository.create_booking(
                user_id=user_id,
                resource_id=resource_id,
                booking_type=booking_type,
                start_time=start_time,
                end_time=end_time,
                status="confirmed",
                check_in_deadline=check_in_deadline,
            )
            self.resource_booking_repository.commit()

            return {
                "success": True,
                "booking_id": booking.id,
                "resource_id": booking.resource_id,
                "booking_type": booking.booking_type,
                "start_time": booking.start_time.isoformat(),
                "end_time": booking.end_time.isoformat(),
                "check_in_deadline": booking.check_in_deadline.isoformat() if booking.check_in_deadline else None,
                "status": booking.status,
            }
        except Exception:
            self.resource_booking_repository.rollback()
            raise

    def mark_checked_in(
        self,
        *,
        booking_id: int,
        user_id: int,
    ) -> dict:
        booking = self.resource_booking_repository.get_by_id_and_user_id(
            booking_id=booking_id,
            user_id=user_id,
        )
        if booking is None:
            raise ValueError("Booking not found")

        if booking.status not in {"confirmed", "checked_in"}:
            raise ValueError("Booking is not available for check-in")

        if booking.status == "checked_in":
            return {
                "success": True,
                "booking_id": booking.id,
                "status": booking.status,
                "checked_in_at": booking.checked_in_at.isoformat() if booking.checked_in_at else None,
                "message": "Booking already checked in",
            }

        try:
            self.resource_booking_repository.update_status(
                booking=booking,
                status="checked_in",
                checked_in_at=datetime.now(),
            )
            self.resource_booking_repository.commit()

            return {
                "success": True,
                "booking_id": booking.id,
                "status": booking.status,
                "checked_in_at": booking.checked_in_at.isoformat() if booking.checked_in_at else None,
            }
        except Exception:
            self.resource_booking_repository.rollback()
            raise

    def mark_completed_if_finished(
        self,
        *,
        now: datetime | None = None,
    ) -> dict:
        current_time = now or datetime.now()
        return {
            "success": True,
            "completed_count": 0,
            "checked_at": current_time.isoformat(),
        }

    def expire_no_show_bookings(
        self,
        *,
        now: datetime | None = None,
    ) -> dict:
        current_time = now or datetime.now()
        bookings = self.resource_booking_repository.list_expired_unchecked_bookings(now=current_time)

        expired_count = 0
        integrity_penalty_count = 0

        for booking in bookings:
            self.resource_booking_repository.update_status(
                booking=booking,
                status="no_show",
                no_show_reason="未按时签到，系统自动释放资源",
            )
            expired_count += 1

            self.integrity_score_repository.create_record(
                user_id=booking.user_id,
                score_delta=-5,
                reason="预约资源后未按时签到",
                related_type="resource_booking",
                related_id=booking.id,
            )
            integrity_penalty_count += 1

        if bookings:
            self.resource_booking_repository.commit()
            self.integrity_score_repository.commit()

        return {
            "success": True,
            "expired_count": expired_count,
            "integrity_penalty_count": integrity_penalty_count,
            "checked_at": current_time.isoformat(),
        }