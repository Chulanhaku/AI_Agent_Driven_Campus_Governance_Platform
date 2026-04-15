from datetime import date
from decimal import Decimal

from sqlalchemy import Boolean, Date, ForeignKey, Integer, JSON, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class Canteen(Base, TimestampMixin):
    __tablename__ = "canteens"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    canteen_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    canteen_name: Mapped[str] = mapped_column(String(100), nullable=False)
    campus: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    location: Mapped[str | None] = mapped_column(String(200), nullable=True)
    open_hours: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False, index=True)

    stalls = relationship(
        "CanteenStall",
        back_populates="canteen",
        cascade="all, delete-orphan",
        order_by="CanteenStall.id.asc()",
    )


class CanteenStall(Base, TimestampMixin):
    __tablename__ = "canteen_stalls"
    __table_args__ = (
        UniqueConstraint("canteen_id", "stall_code", name="uq_canteen_stalls_canteen_id_stall_code"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    canteen_id: Mapped[int] = mapped_column(
        ForeignKey("canteens.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    stall_code: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    stall_name: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    floor_no: Mapped[int | None] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False, index=True)

    canteen = relationship("Canteen", back_populates="stalls")
    menu_items = relationship(
        "CanteenMenuItem",
        back_populates="stall",
        cascade="all, delete-orphan",
        order_by="CanteenMenuItem.id.asc()",
    )


class CanteenMenuItem(Base, TimestampMixin):
    __tablename__ = "canteen_menu_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    stall_id: Mapped[int] = mapped_column(
        ForeignKey("canteen_stalls.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    item_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    meal_time: Mapped[str] = mapped_column(String(20), default="all_day", nullable=False, index=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    spicy_level: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    tags_json: Mapped[list] = mapped_column(JSON, nullable=True, default=list)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    available_from: Mapped[date | None] = mapped_column(Date, nullable=True)
    available_to: Mapped[date | None] = mapped_column(Date, nullable=True)

    stall = relationship("CanteenStall", back_populates="menu_items")