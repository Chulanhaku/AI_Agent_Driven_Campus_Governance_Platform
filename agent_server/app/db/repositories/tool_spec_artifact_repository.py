from sqlalchemy.orm import Session

from app.db.models import ToolSpecArtifact


class ToolSpecArtifactRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_artifact(
        self,
        *,
        proposal_id: int,
        capability_name: str,
        tool_name: str,
        file_path: str,
        artifact_type: str,
        content_json: dict | None,
        code_text: str,
        status: str = "generated",
    ) -> ToolSpecArtifact:
        item = ToolSpecArtifact(
            proposal_id=proposal_id,
            capability_name=capability_name,
            tool_name=tool_name,
            file_path=file_path,
            artifact_type=artifact_type,
            content_json=content_json,
            code_text=code_text,
            status=status,
        )
        self.db.add(item)
        self.db.flush()
        return item

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()