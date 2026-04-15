from datetime import date

from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class DormBuilding(Base, TimestampMixin):
    __tablename__ = "dorm_buildings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    building_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    building_name: Mapped[str] = mapped_column(String(100), nullable=False)
    campus: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    gender_rule: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)
    manager_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    contact_phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False, index=True)

    rooms = relationship(
        "DormRoom",
        back_populates="building",
        cascade="all, delete-orphan",
        order_by="DormRoom.id.asc()",
    )


class DormRoom(Base, TimestampMixin):
    __tablename__ = "dorm_rooms"
    __table_args__ = (
        UniqueConstraint("building_id", "room_no", name="uq_dorm_rooms_building_id_room_no"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    building_id: Mapped[int] = mapped_column(
        ForeignKey("dorm_buildings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    room_no: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    floor_no: Mapped[int | None] = mapped_column(nullable=True)
    bed_count: Mapped[int] = mapped_column(Integer, default=4, nullable=False)
    occupied_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="available", nullable=False, index=True)

    building = relationship("DormBuilding", back_populates="rooms")
    assignments = relationship(
        "DormAssignment",
        back_populates="room",
        cascade="all, delete-orphan",
        order_by="DormAssignment.id.asc()",
    )
    utility_accounts = relationship(
        "DormUtilityAccount",
        back_populates="room",
        cascade="all, delete-orphan",
        order_by="DormUtilityAccount.id.asc()",
    )


class DormAssignment(Base, TimestampMixin):
    __tablename__ = "dorm_assignments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    room_id: Mapped[int] = mapped_column(
        ForeignKey("dorm_rooms.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    bed_no: Mapped[str | None] = mapped_column(String(20), nullable=True)
    check_in_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    check_out_date: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False, index=True)

    user = relationship("User")
    room = relationship("DormRoom", back_populates="assignments")


class DormUtilityAccount(Base, TimestampMixin):
    __tablename__ = "dorm_utility_accounts"
    __table_args__ = (
        UniqueConstraint("room_id", "utility_type", name="uq_dorm_utility_accounts_room_id_utility_type"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    room_id: Mapped[int] = mapped_column(
        ForeignKey("dorm_rooms.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    utility_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)  # electricity / water
    account_no: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    current_balance: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False, index=True)

    room = relationship("DormRoom", back_populates="utility_accounts")
    usage_records = relationship(
        "DormUtilityUsageRecord",
        back_populates="account",
        cascade="all, delete-orphan",
        order_by="DormUtilityUsageRecord.id.asc()",
    )


class DormUtilityUsageRecord(Base, TimestampMixin):
    __tablename__ = "dorm_utility_usage_records"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    account_id: Mapped[int] = mapped_column(
        ForeignKey("dorm_utility_accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    reading_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    usage_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    amount_delta: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    balance_after: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)

    account = relationship("DormUtilityAccount", back_populates="usage_records")