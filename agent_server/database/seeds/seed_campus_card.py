from decimal import Decimal

from app.db.models import CampusCardAccount, User
from app.db.session import SessionLocal


def seed_demo_campus_card() -> None:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == "student_demo").first()
        if user is None:
            raise RuntimeError("demo user not found")

        exists = db.query(CampusCardAccount).filter(CampusCardAccount.user_id == user.id).first()
        if exists:
            print("demo campus card already exists")
            return

        account = CampusCardAccount(
            user_id=user.id,
            card_no=f"CARD-{user.id:06d}",
            balance=Decimal("25.00"),
            status="active",
        )
        db.add(account)
        db.commit()
        print("seed demo campus card success")
    except Exception as exc:
        db.rollback()
        print(f"seed demo campus card failed: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_demo_campus_card()