from datetime import date, time

from sqlalchemy import Date, ForeignKey, Integer, String, Text, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class ShuttleStop(Base, TimestampMixin):
    __tablename__ = "shuttle_stops"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    stop_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    stop_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    campus: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    location_desc: Mapped[str | None] = mapped_column(String(200), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False, index=True)

    route_links = relationship(
        "ShuttleRouteStop",
        back_populates="stop",
        cascade="all, delete-orphan",
        order_by="ShuttleRouteStop.stop_order.asc()",
    )


class ShuttleRoute(Base, TimestampMixin):
    __tablename__ = "shuttle_routes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    route_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    route_name: Mapped[str] = mapped_column(String(100), nullable=False)
    direction: Mapped[str | None] = mapped_column(String(100), nullable=True)
    start_campus: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    end_campus: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False, index=True)
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)

    route_stops = relationship(
        "ShuttleRouteStop",
        back_populates="route",
        cascade="all, delete-orphan",
        order_by="ShuttleRouteStop.stop_order.asc()",
    )
    schedules = relationship(
        "ShuttleSchedule",
        back_populates="route",
        cascade="all, delete-orphan",
        order_by="ShuttleSchedule.service_date.asc(), ShuttleSchedule.depart_time.asc()",
    )


class ShuttleRouteStop(Base, TimestampMixin):
    __tablename__ = "shuttle_route_stops"
    __table_args__ = (
        UniqueConstraint("route_id", "stop_id", name="uq_shuttle_route_stops_route_id_stop_id"),
        UniqueConstraint("route_id", "stop_order", name="uq_shuttle_route_stops_route_id_stop_order"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    route_id: Mapped[int] = mapped_column(
        ForeignKey("shuttle_routes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    stop_id: Mapped[int] = mapped_column(
        ForeignKey("shuttle_stops.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    stop_order: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    travel_minutes_from_origin: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    route = relationship("ShuttleRoute", back_populates="route_stops")
    stop = relationship("ShuttleStop", back_populates="route_links")


class ShuttleSchedule(Base, TimestampMixin):
    __tablename__ = "shuttle_schedules"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    route_id: Mapped[int] = mapped_column(
        ForeignKey("shuttle_routes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    service_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    depart_time: Mapped[time] = mapped_column(Time, nullable=False, index=True)
    arrive_time: Mapped[time] = mapped_column(Time, nullable=False)
    service_day_type: Mapped[str] = mapped_column(String(20), default="weekday", nullable=False, index=True)
    vehicle_no: Mapped[str | None] = mapped_column(String(50), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="scheduled", nullable=False, index=True)
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)

    route = relationship("ShuttleRoute", back_populates="schedules")