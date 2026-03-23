from app.db.models import Resource
from app.db.session import SessionLocal


def seed_demo_resource_data() -> None:
    db = SessionLocal()
    try:
        exists = db.query(Resource).first()
        if exists:
            print("demo resource data already exists")
            return

        resources = [
            Resource(
                resource_code="LIB-A-001",
                resource_name="图书馆一层座位 A-001",
                resource_type="library_seat",
                location="图书馆一层 A 区",
                capacity=1,
                status="available",
            ),
            Resource(
                resource_code="LIB-A-002",
                resource_name="图书馆一层座位 A-002",
                resource_type="library_seat",
                location="图书馆一层 A 区",
                capacity=1,
                status="available",
            ),
            Resource(
                resource_code="SR-201",
                resource_name="第二自习室 201",
                resource_type="study_room",
                location="教学楼 2 层",
                capacity=8,
                status="available",
            ),
            Resource(
                resource_code="MR-301",
                resource_name="会议室 301",
                resource_type="meeting_room",
                location="行政楼 3 层",
                capacity=12,
                status="available",
            ),
            Resource(
                resource_code="LAB-105",
                resource_name="实验室 105",
                resource_type="lab_room",
                location="实验楼 1 层",
                capacity=30,
                status="available",
            ),
        ]

        db.add_all(resources)
        db.commit()
        print("seed demo resource data success")
    except Exception as exc:
        db.rollback()
        print(f"seed demo resource data failed: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_demo_resource_data()