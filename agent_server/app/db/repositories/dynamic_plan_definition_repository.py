from sqlalchemy.orm import Session

from app.db.models import DynamicPlanDefinition


class DynamicPlanDefinitionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_active(self, *, limit: int = 500) -> list[DynamicPlanDefinition]:
        return (
            self.db.query(DynamicPlanDefinition)
            .filter(DynamicPlanDefinition.status == "active")
            .order_by(DynamicPlanDefinition.id.asc())
            .limit(limit)
            .all()
        )

    def get_by_primary_intent(
        self,
        *,
        primary_intent: str,
    ) -> DynamicPlanDefinition | None:
        return (
            self.db.query(DynamicPlanDefinition)
            .filter(
                DynamicPlanDefinition.primary_intent == primary_intent,
                DynamicPlanDefinition.status == "active",
            )
            .first()
        )

    def create_definition(
        self,
        *,
        source_proposal_id: int | None,
        capability_name: str,
        primary_intent: str,
        description: str | None,
        plan_json: dict,
        status: str = "active",
    ) -> DynamicPlanDefinition:
        item = DynamicPlanDefinition(
            source_proposal_id=source_proposal_id,
            capability_name=capability_name,
            primary_intent=primary_intent,
            description=description,
            plan_json=plan_json,
            status=status,
        )
        self.db.add(item)
        self.db.flush()
        return item

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()