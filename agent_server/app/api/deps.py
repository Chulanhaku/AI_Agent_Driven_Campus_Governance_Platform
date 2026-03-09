from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import User
from app.db.repositories.user_repository import UserRepository
from app.services.user_service import UserService


def get_db_dep(db: Session = Depends(get_db)) -> Session:
    return db


def get_user_service(db: Session = Depends(get_db_dep)) -> UserService:
    user_repository = UserRepository(db)
    return UserService(user_repository)


def get_current_user(
    user_service: UserService = Depends(get_user_service),
) -> User:
    # 临时方案：固定读取 id=1 的用户
    # 接 JWT 后会替换掉这里  maybe :/
    user = user_service.get_user_by_id(1)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current user not found. Please seed demo user first.",
        )

    return user