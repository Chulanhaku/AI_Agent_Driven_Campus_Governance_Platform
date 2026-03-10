from datetime import datetime

from sqlalchemy.orm import Session

from app.db.models import ToolExecutionLog


class ToolExecutionLogRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_log(
        self,
        *,
        session_id: int,
        tool_name: str,
        input_json: dict | None = None,
        output_json: dict | None = None,
        status: str = "running",
        started_at: datetime | None = None,
        finished_at: datetime | None = None,
    ) -> ToolExecutionLog:
        log = ToolExecutionLog(
            session_id=session_id,
            tool_name=tool_name,
            input_json=input_json,
            output_json=output_json,
            status=status,
            started_at=started_at,
            finished_at=finished_at,
        )
        self.db.add(log)
        self.db.flush()
        return log

    def update_log(
        self,
        *,
        log: ToolExecutionLog,
        output_json: dict | None = None,
        status: str | None = None,
        finished_at: datetime | None = None,
    ) -> ToolExecutionLog:
        if output_json is not None:
            log.output_json = output_json
        if status is not None:
            log.status = status
        if finished_at is not None:
            log.finished_at = finished_at
        self.db.flush()
        return log

    def list_by_session_id(self, session_id: int) -> list[ToolExecutionLog]:
        return (
            self.db.query(ToolExecutionLog)
            .filter(ToolExecutionLog.session_id == session_id)
            .order_by(ToolExecutionLog.id.asc())
            .all()
        )

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()