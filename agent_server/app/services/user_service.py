from app.db.models import User
from app.db.repositories.user_repository import UserRepository


class UserService:
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    def get_user_by_id(self, user_id: int) -> User | None:
        return self.user_repository.get_by_id(user_id)

    def get_user_by_username(self, username: str) -> User | None:
        return self.user_repository.get_by_username(username)