from sqlalchemy.orm import Session

from app.db.models import User


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_username(self, username: str) -> User | None:
        return self.db.query(User).filter(User.username == username).first()
    def get_first_active_user_by_role_code(
        self,
        *,
        role_code: str,
    ):
        from app.db.models import Role, User

        return (
            self.db.query(User)
            .join(Role, User.role_id == Role.id)
            .filter(
                Role.code == role_code,
                User.status == "active",
            )
            .order_by(User.id.asc())
            .first()
        )