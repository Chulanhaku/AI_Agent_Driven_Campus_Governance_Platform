from app.db.session import SessionLocal
from app.db.models import Role, User, TeacherProfile
from app.security.auth import hash_password


def seed_demo_teacher() -> None:
    db = SessionLocal()
    try:
        teacher_role = db.query(Role).filter(Role.code == "teacher").first()
        if teacher_role is None:
            raise RuntimeError("teacher role not found, please run seed_roles first")

        exists = db.query(User).filter(User.username == "teacher_demo").first()
        if exists:
            print("demo teacher already exists")
            return

        user = User(
            username="teacher_demo",
            password_hash=hash_password("123456"),
            full_name="演示教师",
            email="teacher_demo@example.com",
            role_id=teacher_role.id,
            status="active",
        )
        db.add(user)
        db.flush()

        profile = TeacherProfile(
            user_id=user.id,
            teacher_no="T20260001",
            department="Computer Science",
            title="Lecturer",
        )
        db.add(profile)

        db.commit()
        print("seed demo teacher success")
    except Exception as exc:
        db.rollback()
        print(f"seed demo teacher failed: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_demo_teacher()