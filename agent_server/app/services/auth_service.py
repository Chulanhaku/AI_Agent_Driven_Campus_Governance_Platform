from app.db.models import User
from app.db.repositories.user_repository import UserRepository
from app.security.auth import verify_password
from app.security.jwt_handler import create_access_token


class AuthService:
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    def authenticate_user(self, username: str, password: str) -> User | None:
        user = self.user_repository.get_by_username(username)
        if user is None:
            return None

        if not verify_password(password, user.password_hash):
            return None

        return user

    def login(self, username: str, password: str) -> str | None:
        user = self.authenticate_user(username, password)
        if user is None:
            return None

        return create_access_token(subject=user.username)