from datetime import date, time, timedelta

from app.db.session import SessionLocal
from app.db.models import ShuttleStop, ShuttleRoute, ShuttleRouteStop, ShuttleSchedule


def seed_shuttle_bus() -> None:
    db = SessionLocal()
    try:
        stop_specs = [
            ("main_gate", "主校区南门", "main_campus", "南门公交站旁"),
            ("library", "图书馆站", "main_campus", "图书馆东侧"),
            ("stadium", "体育馆站", "main_campus", "体育馆西侧"),
            ("east_dorm", "东区宿舍站", "main_campus", "东区3号楼前"),
            ("south_campus_gate", "南校区北门", "south_campus", "北门安保亭旁"),
        ]

        stop_map: dict[str, ShuttleStop] = {}
        for stop_code, stop_name, campus, location_desc in stop_specs:
            stop = db.query(ShuttleStop).filter(ShuttleStop.stop_code == stop_code).first()
            if stop is None:
                stop = ShuttleStop(
                    stop_code=stop_code,
                    stop_name=stop_name,
                    campus=campus,
                    location_desc=location_desc,
                    status="active",
                )
                db.add(stop)
                db.flush()
            stop_map[stop_code] = stop

        route = db.query(ShuttleRoute).filter(ShuttleRoute.route_code == "route_a").first()
        if route is None:
            route = ShuttleRoute(
                route_code="route_a",
                route_name="主校区环线A",
                direction="主校区南门 -> 图书馆 -> 体育馆 -> 东区宿舍",
                start_campus="main_campus",
                end_campus="main_campus",
                status="active",
                remark="工作日高峰20分钟一班",
            )
            db.add(route)
            db.flush()

        route_stop_specs = [
            ("main_gate", 1, 0),
            ("library", 2, 6),
            ("stadium", 3, 12),
            ("east_dorm", 4, 18),
        ]

        for stop_code, stop_order, travel_minutes_from_origin in route_stop_specs:
            exists = (
                db.query(ShuttleRouteStop)
                .filter(
                    ShuttleRouteStop.route_id == route.id,
                    ShuttleRouteStop.stop_id == stop_map[stop_code].id,
                )
                .first()
            )
            if exists is None:
                db.add(
                    ShuttleRouteStop(
                        route_id=route.id,
                        stop_id=stop_map[stop_code].id,
                        stop_order=stop_order,
                        travel_minutes_from_origin=travel_minutes_from_origin,
                    )
                )

        today = date.today()
        schedule_specs = [
            (today, time(8, 0), time(8, 18), "weekday", "bus_a01"),
            (today, time(8, 30), time(8, 48), "weekday", "bus_a02"),
            (today, time(12, 10), time(12, 28), "weekday", "bus_a03"),
            (today + timedelta(days=1), time(8, 0), time(8, 18), "weekday", "bus_a04"),
            (today + timedelta(days=1), time(18, 0), time(18, 18), "weekday", "bus_a05"),
        ]

        for service_date, depart_time, arrive_time, service_day_type, vehicle_no in schedule_specs:
            exists = (
                db.query(ShuttleSchedule)
                .filter(
                    ShuttleSchedule.route_id == route.id,
                    ShuttleSchedule.service_date == service_date,
                    ShuttleSchedule.depart_time == depart_time,
                )
                .first()
            )
            if exists is None:
                db.add(
                    ShuttleSchedule(
                        route_id=route.id,
                        service_date=service_date,
                        depart_time=depart_time,
                        arrive_time=arrive_time,
                        service_day_type=service_day_type,
                        vehicle_no=vehicle_no,
                        status="scheduled",
                    )
                )

        db.commit()
        print("seed shuttle bus success")
    except Exception as exc:
        db.rollback()
        print(f"seed shuttle bus failed: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_shuttle_bus()