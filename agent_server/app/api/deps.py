from sqlalchemy.orm import Session
from fastapi import Depends

from db.session import get_db


def get_db_dep(db: Session = Depends(get_db)) -> Session:
    return db