from datetime import date
from decimal import Decimal

from app.db.session import SessionLocal
from app.db.models import Canteen, CanteenStall, CanteenMenuItem


def seed_canteens() -> None:
    db = SessionLocal()
    try:
        east_canteen = db.query(Canteen).filter(Canteen.canteen_code == "east_canteen").first()
        if east_canteen is None:
            east_canteen = Canteen(
                canteen_code="east_canteen",
                canteen_name="东区食堂",
                campus="main_campus",
                location="东区生活广场1层",
                open_hours="06:30-20:30",
                status="active",
            )
            db.add(east_canteen)
            db.flush()

        north_canteen = db.query(Canteen).filter(Canteen.canteen_code == "north_canteen").first()
        if north_canteen is None:
            north_canteen = Canteen(
                canteen_code="north_canteen",
                canteen_name="北区食堂",
                campus="main_campus",
                location="北区宿舍旁",
                open_hours="07:00-21:00",
                status="active",
            )
            db.add(north_canteen)
            db.flush()

        stall_specs = [
            (east_canteen.id, "chuancai", "川湘风味", "chinese", 1),
            (east_canteen.id, "light_food", "轻食窗口", "light_meal", 1),
            (north_canteen.id, "noodle_house", "面食窗口", "noodle", 1),
        ]

        stall_map: dict[str, CanteenStall] = {}
        for canteen_id, stall_code, stall_name, category, floor_no in stall_specs:
            stall = (
                db.query(CanteenStall)
                .filter(
                    CanteenStall.canteen_id == canteen_id,
                    CanteenStall.stall_code == stall_code,
                )
                .first()
            )
            if stall is None:
                stall = CanteenStall(
                    canteen_id=canteen_id,
                    stall_code=stall_code,
                    stall_name=stall_name,
                    category=category,
                    floor_no=floor_no,
                    status="active",
                )
                db.add(stall)
                db.flush()

            stall_map[stall_code] = stall

        menu_specs = [
            ("chuancai", "宫保鸡丁套餐", "lunch", Decimal("12.50"), True, 2, ["rice", "hot"]),
            ("chuancai", "小炒黄牛肉", "dinner", Decimal("16.00"), True, 3, ["beef", "hot"]),
            ("light_food", "鸡胸肉能量沙拉", "all_day", Decimal("14.00"), True, 0, ["healthy", "low_fat"]),
            ("light_food", "金枪鱼三明治", "breakfast", Decimal("9.50"), True, 0, ["breakfast", "light"]),
            ("noodle_house", "红烧牛肉面", "all_day", Decimal("13.00"), True, 1, ["noodle", "soup"]),
            ("noodle_house", "番茄鸡蛋面", "all_day", Decimal("10.00"), True, 0, ["noodle", "tomato"]),
        ]

        for stall_code, item_name, meal_time, price, is_available, spicy_level, tags_json in menu_specs:
            stall = stall_map[stall_code]
            exists = (
                db.query(CanteenMenuItem)
                .filter(
                    CanteenMenuItem.stall_id == stall.id,
                    CanteenMenuItem.item_name == item_name,
                )
                .first()
            )
            if exists is None:
                db.add(
                    CanteenMenuItem(
                        stall_id=stall.id,
                        item_name=item_name,
                        meal_time=meal_time,
                        price=price,
                        is_available=is_available,
                        spicy_level=spicy_level,
                        tags_json=tags_json,
                        description=f"{item_name} 示例菜品",
                        available_from=date.today(),
                    )
                )

        db.commit()
        print("seed canteens success")
    except Exception as exc:
        db.rollback()
        print(f"seed canteens failed: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_canteens()