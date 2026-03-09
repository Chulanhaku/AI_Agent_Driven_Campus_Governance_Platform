from app.db.session import SessionLocal
from app.db.models import Role


def seed_roles() -> None:
    db = SessionLocal()
    try:
        roles = [
            {"name": "Student", "code": "student", "description": "学生"},
            {"name": "Teacher", "code": "teacher", "description": "教师"},
            {"name": "Admin", "code": "admin", "description": "管理员"},
            {"name": "Worker", "code": "worker", "description": "校务工作人员"},
        ]

        for role_data in roles:
            exists = db.query(Role).filter(Role.code == role_data["code"]).first()
            if exists:
                continue
            db.add(Role(**role_data))

        db.commit()
        print("seed roles success")
    except Exception as exc:
        db.rollback()
        print(f"seed roles failed: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_roles()