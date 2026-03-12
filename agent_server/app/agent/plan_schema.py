from typing import Literal, Any

from pydantic import BaseModel, Field


StepType = Literal[
    "call_tool",
    "reason",
    "compose",
    "fallback",
    "create_pending_topup",
    "create_pending_leave",
]


class PlanStepSchema(BaseModel):
    type: StepType
    tool_name: str | None = None
    goal: str | None = None
    params: dict[str, Any] | None = None


class ExecutionPlanSchema(BaseModel):
    plan_type: Literal["multi_step", "workflow", "fallback"]
    steps: list[PlanStepSchema] = Field(default_factory=list)