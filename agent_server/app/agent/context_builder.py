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
                "fallback",
            ],
            "memory": memory_context or {
                "recent_messages": [],
                "recent_message_count": 0,
                "slot_memory": {},
            },
        }