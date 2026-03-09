from app.db.session import SessionLocal
from app.db.models import Role, User, StudentProfile


def seed_demo_user() -> None:
    db = SessionLocal()
    try:
        student_role = db.query(Role).filter(Role.code == "student").first()
        if student_role is None:
            raise RuntimeError("student role not found, please run seed_roles first")

        exists = db.query(User).filter(User.username == "student_demo").first()
        if exists:
            print("demo user already exists")
            return

        user = User(
            username="student_demo",
            password_hash="demo_hash",
            full_name="演示学生",
            email="student_demo@example.com",
            role_id=student_role.id,
            status="active",
        )
        db.add(user)
        db.flush()

        profile = StudentProfile(
            user_id=user.id,
            student_no="20260001",
            department="Computer Science",
            major="Software Engineering",
            class_name="SE-01",
            grade="2026",
        )
        db.add(profile)
        db.commit()
        print("seed demo user success")
    except Exception as exc:
        db.rollback()
        print(f"seed demo user failed: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_demo_user()