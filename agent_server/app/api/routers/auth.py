from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db_dep, get_current_user
from app.api.schemas.auth import (
    CurrentUserResponseSchema,
    LoginRequestSchema,
    LoginResponseSchema,
)
from app.db.models import User
from app.db.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


def get_auth_service(db: Session = Depends(get_db_dep)) -> AuthService:
    user_repository = UserRepository(db)
    return AuthService(user_repository)


@router.post("/login", response_model=LoginResponseSchema)
def login(
    request: LoginRequestSchema,
    auth_service: AuthService = Depends(get_auth_service),
) -> LoginResponseSchema:
    access_token = auth_service.login(
        username=request.username,
        password=request.password,
    )

    if access_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    return LoginResponseSchema(access_token=access_token)


@router.get("/me", response_model=CurrentUserResponseSchema)
def get_me(current_user: User = Depends(get_current_user)) -> CurrentUserResponseSchema:
    return CurrentUserResponseSchema(
        id=current_user.id,
        username=current_user.username,
        full_name=current_user.full_name,
        role_id=current_user.role_id,
        status=current_user.status,
    )