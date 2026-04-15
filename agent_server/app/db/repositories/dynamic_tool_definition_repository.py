from sqlalchemy.orm import Session

from app.db.models import DynamicToolDefinition


class DynamicToolDefinitionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_active(self, *, limit: int = 500) -> list[DynamicToolDefinition]:
        return (
            self.db.query(DynamicToolDefinition)
            .filter(DynamicToolDefinition.status == "active")
            .order_by(DynamicToolDefinition.id.asc())
            .limit(limit)
            .all()
        )

    def get_by_tool_name(
        self,
        *,
        tool_name: str,
    ) -> DynamicToolDefinition | None:
        return (
            self.db.query(DynamicToolDefinition)
            .filter(DynamicToolDefinition.tool_name == tool_name)
            .first()
        )

    def create_definition(
        self,
        *,
        source_proposal_id: int | None,
        tool_name: str,
        primary_intent: str,
        tool_type: str,
        description: str,
        input_schema_json: dict,
        execution_config_json: dict,
        status: str = "active",
    ) -> DynamicToolDefinition:
        item = DynamicToolDefinition(
            source_proposal_id=source_proposal_id,
            tool_name=tool_name,
            primary_intent=primary_intent,
            tool_type=tool_type,
            description=description,
            input_schema_json=input_schema_json,
            execution_config_json=execution_config_json,
            status=status,
        )
        self.db.add(item)
        self.db.flush()
        return item

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()