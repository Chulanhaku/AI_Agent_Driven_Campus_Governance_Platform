import re

from app.db.models import AgentMessage
from app.db.repositories.agent_session_repository import AgentSessionRepository


class MemoryManager:
    def __init__(self, agent_session_repository: AgentSessionRepository) -> None:
        self.agent_session_repository = agent_session_repository

    def get_recent_messages(
        self,
        *,
        session_id: int,
        limit: int = 8,
    ) -> list[AgentMessage]:
        messages = self.agent_session_repository.list_messages_by_session_id(session_id)
        return messages[-limit:] if len(messages) > limit else messages

    def build_memory_context(
        self,
        *,
        session_id: int,
        limit: int = 8,
    ) -> dict:
        messages = self.get_recent_messages(session_id=session_id, limit=limit)

        serialized_messages = []
        for msg in messages:
            serialized_messages.append(
                {
                    "role": msg.role,
                    "content": msg.content,
                    "message_type": msg.message_type,
                }
            )

        slot_memory = self._extract_slot_memory(serialized_messages)

        return {
            "recent_messages": serialized_messages,
            "recent_message_count": len(serialized_messages),
            "slot_memory": slot_memory,
        }

    def _extract_slot_memory(self, messages: list[dict]) -> dict:
        slot_memory = {
            "pending_intent": None,
            "campus_card_topup": {
                "amount": None,
            },
            "leave_create": {
                "days": None,
                "reason": None,
                "leave_type": "sick",
            },
        }

        for item in messages:
            role = item["role"]
            content = item["content"]

            if role != "user":
                continue

            normalized = content.strip().lower()

            # ---- intent memory ----
            if any(keyword in normalized for keyword in ["请假", "请病假", "请事假", "leave"]):
                slot_memory["pending_intent"] = "leave_create"

            elif any(keyword in normalized for keyword in ["充值", "充钱", "充校园卡", "校园卡充值", "topup", "recharge"]):
                slot_memory["pending_intent"] = "campus_card_topup"

            elif any(keyword in normalized for keyword in ["课表", "课程表", "schedule"]):
                slot_memory["pending_intent"] = "query_schedule"

            # ---- topup amount ----
            amount = self._extract_amount(content)
            if amount is not None:
                slot_memory["campus_card_topup"]["amount"] = amount

            # ---- leave days ----
            days = self._extract_leave_days(content)
            if days is not None:
                slot_memory["leave_create"]["days"] = days

            # ---- leave reason ----
            reason = self._extract_leave_reason(content)
            if reason is not None:
                slot_memory["leave_create"]["reason"] = reason

        return slot_memory

    def _extract_amount(self, message: str) -> str | None:
        match = re.search(r"(\d+(?:\.\d{1,2})?)", message)
        if match:
            return match.group(1)
        return None

    def _extract_leave_days(self, message: str) -> int | None:
        match = re.search(r"(\d+)\s*天", message)
        if match:
            return int(match.group(1))
        return None

    def _extract_leave_reason(self, message: str) -> str | None:
        patterns = [
            r"原因是(.+)$",
            r"因为(.+)$",
            r"原因[:：]\s*(.+)$",
        ]

        for pattern in patterns:
            match = re.search(pattern, message)
            if match:
                reason = match.group(1).strip()
                if reason:
                    return reason

        return None
    

# add save slot
    def save_slot_memory(
        self,
        *,
        session_id: int,
        pending_intent: str,
        intent_slots: dict,
    ) -> None:
        import json

        memory_context = self.build_memory_context(session_id=session_id, limit=20)
        current_slot_memory = memory_context.get("slot_memory", {}).copy()

        current_slot_memory["pending_intent"] = pending_intent

        for intent_name, slots in intent_slots.items():
            existing_slots = current_slot_memory.get(intent_name, {}).copy()
            existing_slots.update(slots)
            current_slot_memory[intent_name] = existing_slots

        self.agent_session_repository.add_message(
            session_id=session_id,
            role="system",
            content=json.dumps(current_slot_memory, ensure_ascii=False),
            message_type="slot_memory",
        )