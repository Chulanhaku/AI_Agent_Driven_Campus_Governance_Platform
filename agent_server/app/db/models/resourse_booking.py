from datetime import datetime

from sqlalchemy import ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class Resource(Base, TimestampMixin):
    __tablename__ = "resources"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    resource_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    resource_name: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    location: Mapped[str | None] = mapped_column(String(200), nullable=True)
    capacity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="available", nullable=False, index=True)

    bookings = relationship(
        "ResourceBooking",
        back_populates="resource",
        cascade="all, delete-orphan",
        order_by="ResourceBooking.id.asc()",
    )


class ResourceBooking(Base, TimestampMixin):
    __tablename__ = "resource_bookings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    resource_id: Mapped[int] = mapped_column(
        ForeignKey("resources.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    booking_type: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    end_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    status: Mapped[str] = mapped_column(
        String(20),
        default="pending",
        nullable=False,
        index=True,
    )  # pending / confirmed / checked_in / completed / cancelled / expired / no_show
    check_in_deadline: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    checked_in_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    no_show_reason: Mapped[str | None] = mapped_column(String(200), nullable=True)

    user = relationship("User", back_populates="resource_bookings")
    resource = relationship("Resource", back_populates="bookings")


class IntegrityScoreRecord(Base, TimestampMixin):
    __tablename__ = "integrity_score_records"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    score_delta: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[str] = mapped_column(String(200), nullable=False)
    related_type: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    related_id: Mapped[int | None] = mapped_column(nullable=True, index=True)

    user = relationship("User", back_populates="integrity_score_records")