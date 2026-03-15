from app.db.models import User
from app.tools.registry import ToolRegistry


class ContextBuilder:
    def build(
        self,
        *,
        current_user: User,
        message: str,
        tool_registry: ToolRegistry,
        memory_context: dict | None = None,
    ) -> dict:
        return {
            "current_user": {
                "id": current_user.id,
                "username": current_user.username,
                "full_name": current_user.full_name,
                "role_id": current_user.role_id,
                "status": current_user.status,
            },
            "message": message,
            "available_tools": tool_registry.list_names(),
            "supported_intents": [
                "query_schedule",
                "campus_card_topup",
                "leave_create",
                "policy_qa",
                "send_notification",
                "fallback",
                "course_plan_generate",
            ],
            "memory": memory_context or {
                "recent_messages": [],
                "recent_message_count": 0,
                "slot_memory": {},
                "summary_text": "" ,
                # "current_intent": None,    intent 由 LLM 输出，初始值不设定为 None，避免被误用为“已明确无意图”
            },
        }