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

    def get_by_id(
        self,
        *,
        artifact_id: int,
    ) -> ToolSpecArtifact | None:
        return (
            self.db.query(ToolSpecArtifact)
            .filter(ToolSpecArtifact.id == artifact_id)
            .first()
        )

    def list_recent(
        self,
        *,
        limit: int = 100,
    ) -> list[ToolSpecArtifact]:
        return (
            self.db.query(ToolSpecArtifact)
            .order_by(ToolSpecArtifact.id.desc())
            .limit(limit)
            .all()
        )

    def update_review(
        self,
        *,
        item: ToolSpecArtifact,
        status: str,
        review_comment: str | None,
    ) -> ToolSpecArtifact:
        item.status = status
        item.review_comment = review_comment
        self.db.flush()
        return item

    def update_implemented(
        self,
        *,
        item: ToolSpecArtifact,
        implemented_tool_name: str,
        implemented_module_path: str,
        review_comment: str | None = None,
    ) -> ToolSpecArtifact:
        item.status = "implemented"
        item.implemented_tool_name = implemented_tool_name
        item.implemented_module_path = implemented_module_path
        if review_comment is not None:
            item.review_comment = review_comment
        self.db.flush()
        return item

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()