from app.db.session import SessionLocal
from app.db.models import Permission


def seed_permissions() -> None:
    db = SessionLocal()
    try:
        permissions = [
            {"name": "Read Schedule", "code": "schedule.read", "description": "查看课表"},
            {"name": "Create Leave", "code": "leave.create", "description": "创建请假申请"},
            {"name": "Submit Leave", "code": "leave.submit", "description": "提交请假申请"},
            {"name": "Read Campus Card", "code": "campus_card.read", "description": "查看校园卡"},
            {"name": "Topup Campus Card", "code": "campus_card.topup", "description": "充值校园卡"},
            {"name": "Manage Users", "code": "user.manage", "description": "管理用户"},
        ]

        for permission_data in permissions:
            exists = db.query(Permission).filter(Permission.code == permission_data["code"]).first()
            if exists:
                continue
            db.add(Permission(**permission_data))

        db.commit()
        print("seed permissions success")
    except Exception as exc:
        db.rollback()
        print(f"seed permissions failed: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_permissions()