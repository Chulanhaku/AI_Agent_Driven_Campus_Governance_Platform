from sqlalchemy.orm import Session

from app.db.models import IntegrityScoreRecord


class IntegrityScoreRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_record(
        self,
        *,
        user_id: int,
        score_delta: int,
        reason: str,
        related_type: str | None = None,
        related_id: int | None = None,
    ) -> IntegrityScoreRecord:
        record = IntegrityScoreRecord(
            user_id=user_id,
            score_delta=score_delta,
            reason=reason,
            related_type=related_type,
            related_id=related_id,
        )
        self.db.add(record)
        self.db.flush()
        return record

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()