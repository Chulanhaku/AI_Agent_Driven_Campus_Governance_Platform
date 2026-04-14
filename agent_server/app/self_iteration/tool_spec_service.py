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