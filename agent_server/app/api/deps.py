from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.app_container import AppContainer
from app.db.session import get_db
from app.db.models import User
from app.db.repositories.user_repository import UserRepository
from app.llm.base import BaseLlmProvider
from app.rag.rag_service import RagService
from app.rag.retriever import Retriever
from app.security.jwt_handler import decode_access_token
from app.services.user_service import UserService


bearer_scheme = HTTPBearer(auto_error=False)


def get_db_dep(db: Session = Depends(get_db)) -> Session:
    return db


def get_user_service(db: Session = Depends(get_db_dep)) -> UserService:
    user_repository = UserRepository(db)
    return UserService(user_repository)


def get_app_container(request: Request) -> AppContainer:
    container = getattr(request.app.state, "container", None)
    if container is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Application container is not initialized",
        )
    return container


def get_llm_provider(
    container: AppContainer = Depends(get_app_container),
) -> BaseLlmProvider:
    return container.llm_provider


def get_rag_service(
    container: AppContainer = Depends(get_app_container),
) -> RagService:
    return container.rag_service


def get_retriever(
    rag_service: RagService = Depends(get_rag_service),
) -> Retriever:
    return rag_service.get_retriever()


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    user_service: UserService = Depends(get_user_service),
) -> User:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    token = credentials.credentials

    try:
        payload = decode_access_token(token)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc

    username = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token payload missing subject",
        )

    user = user_service.get_user_by_username(username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not active",
        )

    return user