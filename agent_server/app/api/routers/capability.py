from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_capability_registry, get_db_dep
from app.db.repositories.capability_proposal_repository import CapabilityProposalRepository
from app.self_iteration.capability_bootstrap import CapabilityBootstrap
from app.self_iteration.capability_loader import CapabilityLoader
from app.self_iteration.capability_registry import CapabilityRegistry
from app.self_iteration.capability_detector import CapabilityDetector
from app.self_iteration.capability_designer import CapabilityDesigner
from app.self_iteration.capability_researcher import CapabilityResearcher
from app.self_iteration.capability_validator import CapabilityValidator
from app.self_iteration.capability_policy import CapabilityPolicy
from app.self_iteration.capability_service import CapabilityService
from app.api.deps import get_app_container
from app.tools.web_research_tool import WebResearchTool
from app.tools.db_schema_search_tool import DbSchemaSearchTool
from app.tools.db_data_search_tool import DbDataSearchTool
from app.db.repositories.tool_spec_artifact_repository import ToolSpecArtifactRepository
from app.self_iteration.tool_spec_codegen import ToolSpecCodegen
from app.self_iteration.tool_spec_service import ToolSpecService
from app.db.repositories.dynamic_tool_definition_repository import DynamicToolDefinitionRepository
from app.db.repositories.dynamic_plan_definition_repository import DynamicPlanDefinitionRepository
from app.self_iteration.dynamic_definition_factory import DynamicDefinitionFactory
from app.self_iteration.dynamic_definition_service import DynamicDefinitionService
from app.self_iteration.dynamic_capability_bootstrap import DynamicCapabilityBootstrap
from app.api.deps import get_dynamic_tool_registry, get_dynamic_plan_registry
from app.self_iteration.dynamic_tool_registry import DynamicToolRegistry
from app.self_iteration.dynamic_plan_registry import DynamicPlanRegistry

router = APIRouter(prefix="/capabilities", tags=["capabilities"])


def get_capability_service(
    db: Session = Depends(get_db_dep),
    capability_registry: CapabilityRegistry = Depends(get_capability_registry),
    container = Depends(get_app_container),
) -> CapabilityService:
    web_research_tool = WebResearchTool()
    db_schema_search_tool = DbSchemaSearchTool(db)
    db_data_search_tool = DbDataSearchTool(db)

    capability_proposal_repository = CapabilityProposalRepository(db)
    capability_detector = CapabilityDetector()
    capability_researcher = CapabilityResearcher(
        web_research_tool=web_research_tool,
        db_schema_search_tool=db_schema_search_tool,
        db_data_search_tool=db_data_search_tool,
    )
    capability_designer = CapabilityDesigner(container.llm_provider)
    capability_validator = CapabilityValidator()
    capability_loader = CapabilityLoader(capability_registry)
    capability_policy = CapabilityPolicy()

    return CapabilityService(
        capability_proposal_repository=capability_proposal_repository,
        capability_detector=capability_detector,
        capability_researcher=capability_researcher,
        capability_designer=capability_designer,
        capability_validator=capability_validator,
        capability_loader=capability_loader,
        capability_policy=capability_policy,
    )

def get_tool_spec_service(
    db: Session = Depends(get_db_dep),
) -> ToolSpecService:
    capability_proposal_repository = CapabilityProposalRepository(db)
    tool_spec_artifact_repository = ToolSpecArtifactRepository(db)
    tool_spec_codegen = ToolSpecCodegen()

    return ToolSpecService(
        capability_proposal_repository=capability_proposal_repository,
        tool_spec_artifact_repository=tool_spec_artifact_repository,
        tool_spec_codegen=tool_spec_codegen,
    )

def get_dynamic_definition_service(
    db: Session = Depends(get_db_dep),
    dynamic_tool_registry: DynamicToolRegistry = Depends(get_dynamic_tool_registry),
    dynamic_plan_registry: DynamicPlanRegistry = Depends(get_dynamic_plan_registry),
) -> DynamicDefinitionService:
    capability_proposal_repository = CapabilityProposalRepository(db)
    dynamic_tool_definition_repository = DynamicToolDefinitionRepository(db)
    dynamic_plan_definition_repository = DynamicPlanDefinitionRepository(db)

    dynamic_definition_factory = DynamicDefinitionFactory()
    dynamic_capability_bootstrap = DynamicCapabilityBootstrap(
        dynamic_tool_definition_repository=dynamic_tool_definition_repository,
        dynamic_plan_definition_repository=dynamic_plan_definition_repository,
        dynamic_tool_registry=dynamic_tool_registry,
        dynamic_plan_registry=dynamic_plan_registry,
    )

    return DynamicDefinitionService(
        capability_proposal_repository=capability_proposal_repository,
        dynamic_tool_definition_repository=dynamic_tool_definition_repository,
        dynamic_plan_definition_repository=dynamic_plan_definition_repository,
        dynamic_definition_factory=dynamic_definition_factory,
        dynamic_capability_bootstrap=dynamic_capability_bootstrap,
    )

@router.post("/{proposal_id}/generate-tool-stub")
def generate_tool_stub_from_proposal(
    proposal_id: int,
    tool_spec_service: ToolSpecService = Depends(get_tool_spec_service),
) -> dict:
    try:
        return tool_spec_service.generate_stub_from_tool_spec(
            proposal_id=proposal_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

@router.get("/registry")
def get_capability_registry_snapshot(
    capability_registry: CapabilityRegistry = Depends(get_capability_registry),
) -> dict:
    return capability_registry.snapshot()


@router.get("/proposals")
def list_capability_proposals(
    db: Session = Depends(get_db_dep),
) -> list[dict]:
    repository = CapabilityProposalRepository(db)
    items = repository.list_recent(limit=50)

    return [
        {
            "id": item.id,
            "session_id": item.session_id,
            "user_id": item.user_id,
            "trigger_message": item.trigger_message,
            "proposal_type": item.proposal_type,
            "capability_name": item.capability_name,
            "research_summary_json": item.research_summary_json,
            "proposal_json": item.proposal_json,
            "confidence_score": item.confidence_score,
            "risk_level": item.risk_level,
            "activation_policy": item.activation_policy,
            "validation_reason": item.validation_reason,
            "status": item.status,
            "created_at": item.created_at.isoformat() if item.created_at else None,
        }
        for item in items
    ]

@router.post("/reload")
def reload_activated_capabilities(
    db: Session = Depends(get_db_dep),
    capability_registry: CapabilityRegistry = Depends(get_capability_registry),
) -> dict:
    repository = CapabilityProposalRepository(db)
    loader = CapabilityLoader(capability_registry)
    bootstrap = CapabilityBootstrap(
        capability_proposal_repository=repository,
        capability_loader=loader,
    )
    return bootstrap.reload_activated_proposals()


@router.get("/validated")
def list_validated_capability_proposals(
    limit: int = Query(default=100, ge=1, le=500),
    capability_service: CapabilityService = Depends(get_capability_service),
) -> list[dict]:
    return capability_service.list_validated_proposals(limit=limit)


@router.post("/{proposal_id}/approve")
def approve_validated_capability_proposal(
    proposal_id: int,
    capability_service: CapabilityService = Depends(get_capability_service),
    dynamic_definition_service: DynamicDefinitionService = Depends(get_dynamic_definition_service),
) -> dict:
    try:
        approval_result = capability_service.approve_validated_proposal(
            proposal_id=proposal_id,
        )

        dynamic_registration_result = None
        if approval_result.get("proposal_type") == "tool_spec":
            dynamic_registration_result = dynamic_definition_service.register_from_tool_spec_proposal(
                proposal_id=proposal_id,
            )

        return {
            "success": True,
            "approval_result": approval_result,
            "dynamic_registration_result": dynamic_registration_result,
        }
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.post("/{proposal_id}/reject")
def reject_validated_capability_proposal(
    proposal_id: int,
    capability_service: CapabilityService = Depends(get_capability_service),
) -> dict:
    try:
        return capability_service.reject_validated_proposal(
            proposal_id=proposal_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    

@router.get("/artifacts")
def list_tool_spec_artifacts(
    limit: int = Query(default=100, ge=1, le=500),
    tool_spec_service: ToolSpecService = Depends(get_tool_spec_service),
) -> list[dict]:
    return tool_spec_service.list_artifacts(limit=limit)


@router.post("/artifacts/{artifact_id}/review")
def review_tool_spec_artifact(
    artifact_id: int,
    approved: bool = Query(...),
    review_comment: str | None = Query(default=None),
    tool_spec_service: ToolSpecService = Depends(get_tool_spec_service),
) -> dict:
    try:
        return tool_spec_service.review_artifact(
            artifact_id=artifact_id,
            approved=approved,
            review_comment=review_comment,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    


@router.post("/artifacts/{artifact_id}/implement")
def mark_tool_spec_artifact_as_implemented(
    artifact_id: int,
    implemented_tool_name: str = Query(...),
    implemented_module_path: str = Query(...),
    review_comment: str | None = Query(default=None),
    tool_spec_service: ToolSpecService = Depends(get_tool_spec_service),
) -> dict:
    try:
        return tool_spec_service.mark_artifact_as_implemented(
            artifact_id=artifact_id,
            implemented_tool_name=implemented_tool_name,
            implemented_module_path=implemented_module_path,
            review_comment=review_comment,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    

@router.get("/dynamic/registry")
def get_dynamic_registry_snapshot(
    dynamic_tool_registry: DynamicToolRegistry = Depends(get_dynamic_tool_registry),
    dynamic_plan_registry: DynamicPlanRegistry = Depends(get_dynamic_plan_registry),
) -> dict:
    return {
        "dynamic_tools": dynamic_tool_registry.snapshot(),
        "dynamic_plans": dynamic_plan_registry.snapshot(),
    }