from datetime import datetime

from app.db.models import ToolExecutionLog
from app.db.repositories.tool_execution_log_repository import ToolExecutionLogRepository


class ToolExecutionLogService:
    def __init__(self, tool_execution_log_repository: ToolExecutionLogRepository) -> None:
        self.tool_execution_log_repository = tool_execution_log_repository

    def start_log(
        self,
        *,
        session_id: int,
        tool_name: str,
        input_json: dict | None = None,
    ) -> ToolExecutionLog:
        log = self.tool_execution_log_repository.create_log(
            session_id=session_id,
            tool_name=tool_name,
            input_json=input_json,
            status="running",
            started_at=datetime.utcnow(),
        )
        self.tool_execution_log_repository.commit()
        return log

    def finish_log(
        self,
        *,
        log: ToolExecutionLog,
        output_json: dict | None,
        status: str,
    ) -> ToolExecutionLog:
        updated_log = self.tool_execution_log_repository.update_log(
            log=log,
            output_json=output_json,
            status=status,
            finished_at=datetime.utcnow(),
        )
        self.tool_execution_log_repository.commit()
        return updated_log

    def list_by_session_id(self, session_id: int) -> list[ToolExecutionLog]:
        return self.tool_execution_log_repository.list_by_session_id(session_id)