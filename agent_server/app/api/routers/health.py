from sqlalchemy import text
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends

from app.api.deps import get_db_dep

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def health_check() -> dict:
    return {
        "status": "ok",
        "message": "agent server is running",
    }


@router.get("/db")
def health_check_db(db: Session = Depends(get_db_dep)) -> dict:
    db.execute(text("SELECT 1"))

    return {
        "status": "ok",
        "message": "database connection is healthy",
    }
    # try:
    #     db.execute(text("SELECT 1"))
    #     return {
    #         "status": "ok",
    #         "message": "database connection is healthy",
    #     }
    # except OperationalError as e:
    #     return {
    #         "status": "error",
    #         "message": f"Database unreachable: {str(e)}",
    #     }