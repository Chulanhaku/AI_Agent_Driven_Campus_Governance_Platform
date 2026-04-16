from app.db.repositories.capability_proposal_repository import CapabilityProposalRepository
from app.db.repositories.tool_spec_artifact_repository import ToolSpecArtifactRepository
from app.self_iteration.tool_spec_codegen import ToolSpecCodegen


class ToolSpecService:
    def __init__(
        self,
        capability_proposal_repository: CapabilityProposalRepository,
        tool_spec_artifact_repository: ToolSpecArtifactRepository,
        tool_spec_codegen: ToolSpecCodegen,
    ) -> None:
        self.capability_proposal_repository = capability_proposal_repository
        self.tool_spec_artifact_repository = tool_spec_artifact_repository
        self.tool_spec_codegen = tool_spec_codegen

    def generate_stub_from_tool_spec(
        self,
        *,
        proposal_id: int,
    ) -> dict:
        proposal_item = self.capability_proposal_repository.get_by_id(
            proposal_id=proposal_id,
        )
        if proposal_item is None:
            raise ValueError("Capability proposal not found")

        if proposal_item.proposal_type != "tool_spec":
            raise ValueError("Only tool_spec proposal can generate tool stub")

        try:
            artifact = self.tool_spec_codegen.generate_stub(
                proposal_id=proposal_item.id,
                proposal=proposal_item.proposal_json,
            )

            db_item = self.tool_spec_artifact_repository.create_artifact(
                proposal_id=proposal_item.id,
                capability_name=artifact["capability_name"],
                tool_name=artifact["tool_name"],
                file_path=artifact["file_path"],
                artifact_type=artifact["artifact_type"],
                content_json=artifact["content_json"],
                code_text=artifact["code_text"],
                status="generated",
            )
            self.tool_spec_artifact_repository.commit()

            return {
                "success": True,
                "artifact_id": db_item.id,
                "proposal_id": proposal_item.id,
                "capability_name": db_item.capability_name,
                "tool_name": db_item.tool_name,
                "file_path": db_item.file_path,
                "status": db_item.status,
            }
        except Exception:
            self.tool_spec_artifact_repository.rollback()
            raise

    def list_artifacts(
        self,
        *,
        limit: int = 100,
    ) -> list[dict]:
        items = self.tool_spec_artifact_repository.list_recent(limit=limit)
        return [
            {
                "id": item.id,
                "proposal_id": item.proposal_id,
                "capability_name": item.capability_name,
                "tool_name": item.tool_name,
                "file_path": item.file_path,
                "artifact_type": item.artifact_type,
                "status": item.status,
                "review_comment": item.review_comment,
                "implemented_tool_name": item.implemented_tool_name,
                "implemented_module_path": item.implemented_module_path,
                "created_at": item.created_at.isoformat() if item.created_at else None,
            }
            for item in items
        ]

    def review_artifact(
        self,
        *,
        artifact_id: int,
        approved: bool,
        review_comment: str | None = None,
    ) -> dict:
        item = self.tool_spec_artifact_repository.get_by_id(artifact_id=artifact_id)
        if item is None:
            raise ValueError("Tool spec artifact not found")

        if item.status not in {"generated", "reviewed"}:
            raise ValueError("Only generated/reviewed artifact can be reviewed")

        new_status = "reviewed" if approved else "rejected"

        try:
            self.tool_spec_artifact_repository.update_review(
                item=item,
                status=new_status,
                review_comment=review_comment,
            )
            self.tool_spec_artifact_repository.commit()

            return {
                "success": True,
                "artifact_id": item.id,
                "status": item.status,
                "review_comment": item.review_comment,
            }
        except Exception:
            self.tool_spec_artifact_repository.rollback()
            raise

    def mark_artifact_as_implemented(
        self,
        *,
        artifact_id: int,
        implemented_tool_name: str,
        implemented_module_path: str,
        review_comment: str | None = None,
    ) -> dict:
        item = self.tool_spec_artifact_repository.get_by_id(artifact_id=artifact_id)
        if item is None:
            raise ValueError("Tool spec artifact not found")

        if item.status not in {"generated", "reviewed"}:
            raise ValueError("Only generated/reviewed artifact can be marked as implemented")

        try:
            self.tool_spec_artifact_repository.update_implemented(
                item=item,
                implemented_tool_name=implemented_tool_name,
                implemented_module_path=implemented_module_path,
                review_comment=review_comment,
            )
            self.tool_spec_artifact_repository.commit()

            return {
                "success": True,
                "artifact_id": item.id,
                "status": item.status,
                "implemented_tool_name": item.implemented_tool_name,
                "implemented_module_path": item.implemented_module_path,
            }
        except Exception:
            self.tool_spec_artifact_repository.rollback()
            raise