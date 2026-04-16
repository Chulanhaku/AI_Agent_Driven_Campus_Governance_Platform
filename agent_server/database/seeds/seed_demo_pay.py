from datetime import date
from decimal import Decimal

from app.db.session import SessionLocal
from app.db.models import (
    User,
    DormBuilding,
    DormRoom,
    DormAssignment,
    DormUtilityAccount,
    DormUtilityUsageRecord,
)


def seed_dormitory_data() -> None:
    db = SessionLocal()
    try:
        student = db.query(User).filter(User.username == "student_demo").first()
        if student is None:
            raise RuntimeError("student_demo not found, please run seed_demo_user first")

        building = db.query(DormBuilding).filter(DormBuilding.building_code == "dorm_1").first()
        if building is None:
            building = DormBuilding(
                building_code="dorm_1",
                building_name="一号宿舍楼",
                campus="main_campus",
                gender_rule="mixed",
                manager_name="王阿姨",
                contact_phone="13800000001",
                status="active",
            )
            db.add(building)
            db.flush()

        room = (
            db.query(DormRoom)
            .filter(
                DormRoom.building_id == building.id,
                DormRoom.room_no == "301",
            )
            .first()
        )
        if room is None:
            room = DormRoom(
                building_id=building.id,
                room_no="301",
                floor_no=3,
                bed_count=4,
                occupied_count=1,
                status="available",
            )
            db.add(room)
            db.flush()

        assignment = (
            db.query(DormAssignment)
            .filter(
                DormAssignment.user_id == student.id,
                DormAssignment.status == "active",
            )
            .first()
        )
        if assignment is None:
            db.add(
                DormAssignment(
                    user_id=student.id,
                    room_id=room.id,
                    bed_no="1",
                    check_in_date=date(2026, 2, 20),
                    check_out_date=None,
                    status="active",
                )
            )

        electricity_account = (
            db.query(DormUtilityAccount)
            .filter(
                DormUtilityAccount.room_id == room.id,
                DormUtilityAccount.utility_type == "electricity",
            )
            .first()
        )
        if electricity_account is None:
            electricity_account = DormUtilityAccount(
                room_id=room.id,
                utility_type="electricity",
                account_no="elec_dorm1_301",
                current_balance=Decimal("86.50"),
                unit_price=Decimal("0.65"),
                status="active",
            )
            db.add(electricity_account)
            db.flush()

        water_account = (
            db.query(DormUtilityAccount)
            .filter(
                DormUtilityAccount.room_id == room.id,
                DormUtilityAccount.utility_type == "water",
            )
            .first()
        )
        if water_account is None:
            water_account = DormUtilityAccount(
                room_id=room.id,
                utility_type="water",
                account_no="water_dorm1_301",
                current_balance=Decimal("42.00"),
                unit_price=Decimal("3.20"),
                status="active",
            )
            db.add(water_account)
            db.flush()

        usage_specs = [
            (
                electricity_account.id,
                date(2026, 4, 1),
                Decimal("12.00"),
                Decimal("-7.80"),
                Decimal("94.30"),
                "4月上旬电费扣减",
            ),
            (
                electricity_account.id,
                date(2026, 4, 10),
                Decimal("12.00"),
                Decimal("-7.80"),
                Decimal("86.50"),
                "4月中旬电费扣减",
            ),
            (
                water_account.id,
                date(2026, 4, 5),
                Decimal("3.00"),
                Decimal("-9.60"),
                Decimal("42.00"),
                "4月用水结算",
            ),
        ]

        for account_id, reading_date, usage_amount, amount_delta, balance_after, remark in usage_specs:
            exists = (
                db.query(DormUtilityUsageRecord)
                .filter(
                    DormUtilityUsageRecord.account_id == account_id,
                    DormUtilityUsageRecord.reading_date == reading_date,
                    DormUtilityUsageRecord.remark == remark,
                )
                .first()
            )
            if exists is None:
                db.add(
                    DormUtilityUsageRecord(
                        account_id=account_id,
                        reading_date=reading_date,
                        usage_amount=usage_amount,
                        amount_delta=amount_delta,
                        balance_after=balance_after,
                        remark=remark,
                    )
                )

        db.commit()
        print("seed dormitory data success")
    except Exception as exc:
        db.rollback()
        print(f"seed dormitory data failed: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_dormitory_data()