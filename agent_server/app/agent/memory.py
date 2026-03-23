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
        persisted_memory: dict | None = None,
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

        # 持久化快照优先补位
        persisted_slots = (persisted_memory or {}).get("slot_snapshot_json") or {}
        merged_slot_memory = self._merge_slot_memory(
            persisted_slot_memory=persisted_slots,
            runtime_slot_memory=slot_memory,
        )

        summary_text = self._build_summary_text(
            recent_messages=serialized_messages,
            slot_memory=merged_slot_memory,
            persisted_summary=(persisted_memory or {}).get("summary_text"),
        )

        current_intent = merged_slot_memory.get("pending_intent")

        return {
            "recent_messages": serialized_messages,
            "recent_message_count": len(serialized_messages),
            "slot_memory": merged_slot_memory,
            "summary_text": summary_text,
            "current_intent": current_intent,
        }

    def _extract_plan_index(self, message: str) -> int | None:
        match = re.search(r"方案\s*(\d+)", message)
        if match:
            return int(match.group(1))
        return None

    def _merge_slot_memory(
        self,
        *,
        persisted_slot_memory: dict,
        runtime_slot_memory: dict,
    ) -> dict:
        merged = {
            "pending_intent": runtime_slot_memory.get("pending_intent")
            or persisted_slot_memory.get("pending_intent"),
            "campus_card_topup": {
                "amount": (
                    runtime_slot_memory.get("campus_card_topup", {}).get("amount")
                    or persisted_slot_memory.get("campus_card_topup", {}).get("amount")
                ),
            },
            "leave_create": {
                "days": (
                    runtime_slot_memory.get("leave_create", {}).get("days")
                    or persisted_slot_memory.get("leave_create", {}).get("days")
                ),
                "reason": (
                    runtime_slot_memory.get("leave_create", {}).get("reason")
                    or persisted_slot_memory.get("leave_create", {}).get("reason")
                ),
                "leave_type": (
                    runtime_slot_memory.get("leave_create", {}).get("leave_type")
                    or persisted_slot_memory.get("leave_create", {}).get("leave_type")
                    or "sick"
                ),
            },
            "course_plan_generate": {
                "semester": (
                    runtime_slot_memory.get("course_plan_generate", {}).get("semester")
                    or persisted_slot_memory.get("course_plan_generate", {}).get("semester")
                ),
                "last_generated_plans": (
                    runtime_slot_memory.get("course_plan_generate", {}).get("last_generated_plans")
                    or persisted_slot_memory.get("course_plan_generate", {}).get("last_generated_plans")
                    or []
                ),
                "selected_plan_index": (
                    runtime_slot_memory.get("course_plan_generate", {}).get("selected_plan_index")
                    or persisted_slot_memory.get("course_plan_generate", {}).get("selected_plan_index")
                ),
            },
            "resource_booking": {
                "resource_type": (
                    runtime_slot_memory.get("resource_booking", {}).get("resource_type")
                    or persisted_slot_memory.get("resource_booking", {}).get("resource_type")
                ),
                "start_time": (
                    runtime_slot_memory.get("resource_booking", {}).get("start_time")
                    or persisted_slot_memory.get("resource_booking", {}).get("start_time")
                ),
                "end_time": (
                    runtime_slot_memory.get("resource_booking", {}).get("end_time")
                    or persisted_slot_memory.get("resource_booking", {}).get("end_time")
                ),
                "last_candidates": (
                    runtime_slot_memory.get("resource_booking", {}).get("last_candidates")
                    or persisted_slot_memory.get("resource_booking", {}).get("last_candidates")
                    or []
                ),
                "selected_resource_index": (
                    runtime_slot_memory.get("resource_booking", {}).get("selected_resource_index")
                    or persisted_slot_memory.get("resource_booking", {}).get("selected_resource_index")
                ),
            },
        }
        return merged

    def _build_summary_text(
        self,
        *,
        recent_messages: list[dict],
        slot_memory: dict,
        persisted_summary: str | None,
    ) -> str:
        parts = []

        pending_intent = slot_memory.get("pending_intent")
        if pending_intent:
            parts.append(f"当前主要意图：{pending_intent}")

        topup_amount = slot_memory.get("campus_card_topup", {}).get("amount")
        if topup_amount:
            parts.append(f"已知充值金额：{topup_amount}")

        leave_days = slot_memory.get("leave_create", {}).get("days")
        leave_reason = slot_memory.get("leave_create", {}).get("reason")
        if leave_days:
            parts.append(f"已知请假天数：{leave_days}")
        if leave_reason:
            parts.append(f"已知请假原因：{leave_reason}")

        if recent_messages:
            last_user_messages = [
                item["content"]
                for item in recent_messages
                if item["role"] == "user"
            ][-2:]
            if last_user_messages:
                parts.append(f"最近用户消息：{' | '.join(last_user_messages)}")

        if persisted_summary and not parts:
            return persisted_summary

        return "；".join(parts) if parts else (persisted_summary or "")

    def _extract_slot_memory(self, messages: list[dict]) -> dict:
        slot_memory = {
            "pending_intent": None,
            "semester": None,
            "campus_card_topup": {
                "amount": None,
            },
            "leave_create": {
                "days": None,
                "reason": None,
                "leave_type": "sick",
            },
            "course_plan_generate": {
                "semester": None,
                "last_generated_plans": [],
                "selected_plan_index": None,
            },
            "resource_booking": {
                "resource_type": None,
                "start_time": None,
                "end_time": None,
                "last_candidates": [],
                "selected_resource_index": None,
            },
        }

        for item in messages:
            role = item["role"]
            content = item["content"]

            if role != "user":
                continue

            normalized = content.strip().lower()

            if any(keyword in normalized for keyword in ["请假", "请病假", "请事假", "leave"]):
                slot_memory["pending_intent"] = "leave_create"
            elif any(keyword in normalized for keyword in ["充值", "充钱", "充校园卡", "校园卡充值", "topup", "recharge"]):
                slot_memory["pending_intent"] = "campus_card_topup"
            elif any(keyword in normalized for keyword in ["课表", "课程表", "schedule"]):
                slot_memory["pending_intent"] = "query_schedule"

            amount = self._extract_amount(content)
            if amount is not None:
                slot_memory["campus_card_topup"]["amount"] = amount
            
            semester = self._extract_semester(content)
            if semester is not None:
                slot_memory["semester"] = semester
                slot_memory["course_plan_generate"]["semester"] = semester

            plan_index = self._extract_plan_index(content)
            if plan_index is not None:
                slot_memory["course_plan_generate"]["selected_plan_index"] = plan_index

            days = self._extract_leave_days(content)
            if days is not None:
                slot_memory["leave_create"]["days"] = days

            reason = self._extract_leave_reason(content)
            if reason is not None:
                slot_memory["leave_create"]["reason"] = reason

            resource_type = self._extract_resource_type(content)
            if resource_type is not None:
                slot_memory["resource_booking"]["resource_type"] = resource_type

            time_range = self._extract_booking_time_range(content)
            if time_range is not None:
                slot_memory["resource_booking"]["start_time"] = time_range[0]
                slot_memory["resource_booking"]["end_time"] = time_range[1]

            candidate_index = self._extract_candidate_index(content)
            if candidate_index is not None:
                slot_memory["resource_booking"]["selected_resource_index"] = candidate_index
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

    def _extract_resource_type(self, message: str) -> str | None:
        normalized = message.strip().lower()

        if "图书馆" in normalized or "座位" in normalized:
            return "library_seat"
        if "自习室" in normalized:
            return "study_room"
        if "会议室" in normalized:
            return "meeting_room"
        if "实验室" in normalized:
            return "lab_room"
        return None

    def _extract_candidate_index(self, message: str) -> int | None:
        import re

        match = re.search(r"第\s*(\d+)\s*个", message)
        if match:
            return int(match.group(1))

        match = re.search(r"选\s*(\d+)", message)
        if match:
            return int(match.group(1))

        return None

    def _extract_booking_time_range(self, message: str) -> tuple[str, str] | None:
        from datetime import datetime, timedelta

        normalized = message.strip().lower()
        now = datetime.now()

        start = now + timedelta(hours=1)
        end = start + timedelta(hours=2)

        if "明天" in normalized:
            start = start + timedelta(days=1)
            end = end + timedelta(days=1)

        if "下午" in normalized:
            start = start.replace(hour=14, minute=0, second=0, microsecond=0)
            end = start.replace(hour=16, minute=0, second=0, microsecond=0)
        elif "上午" in normalized:
            start = start.replace(hour=9, minute=0, second=0, microsecond=0)
            end = start.replace(hour=11, minute=0, second=0, microsecond=0)
        elif "晚上" in normalized:
            start = start.replace(hour=19, minute=0, second=0, microsecond=0)
            end = start.replace(hour=21, minute=0, second=0, microsecond=0)

        return start.isoformat(), end.isoformat()

    def _extract_semester(self, message: str) -> str | None:
        from datetime import datetime
        import re

        normalized = message.strip().lower()

        def build_semester_by_date(target_date: datetime) -> str:
            year = target_date.year
            month = target_date.month

            # 约定：
            # fall: 秋季学期（9月~次年2月前半段按秋季学期理解）
            # spring: 春季学期（3月~8月）
            if month >= 9:
                return f"{year}-fall"
            if 1 <= month <= 2:
                return f"{year - 1}-fall"
            return f"{year}-spring"

        now = datetime.now()

        def next_semester(semester: str) -> str:
            match = re.match(r"(\d{4})-(spring|fall)", semester)
            if not match:
                return None
            year = int(match.group(1))
            season = match.group(2)

            if season == "fall":
                return f"{year + 1}-spring"
            return f"{year}-fall"

        def prev_semester(semester: str) -> str:
            match = re.match(r"(\d{4})-(spring|fall)", semester)
            if not match:
                return None
            year = int(match.group(1))
            season = match.group(2)

            if season == "spring":
                return f"{year - 1}-fall"
            return f"{year}-spring"

        current_semester = build_semester_by_date(now)

        # 相对学期
        if "下学期" in message:
            return next_semester(current_semester)

        if "上学期" in message:
            return prev_semester(current_semester)

        if "这学期" in message or "本学期" in message or "当前学期" in message:
            return current_semester

        # 直接匹配：2026-spring / 2026_fall / 2026 spring
        match = re.search(r"(20\d{2})\s*[-_\s]?\s*(spring|fall)", normalized)
        if match:
            year = match.group(1)
            season = match.group(2)
            return f"{year}-{season}"

        # 匹配：2026年春季学期 / 2026年秋季学期
        match = re.search(r"(20\d{2})\s*年\s*(春季|秋季)", message)
        if match:
            year = int(match.group(1))
            season = match.group(2)
            return f"{year}-spring" if season == "春季" else f"{year}-fall"

        # 匹配：2025-2026学年第一学期 / 第二学期
        # 约定：
        # 第一学期 -> 2025-fall
        # 第二学期 -> 2026-spring
        match = re.search(
            r"(20\d{2})\s*[-_/]\s*(20\d{2})\s*学年\s*第?\s*([一二12])\s*学期",
            message
        )
        if match:
            start_year = int(match.group(1))
            end_year = int(match.group(2))
            term_raw = match.group(3)

            if end_year == start_year + 1:
                if term_raw in ["一", "1"]:
                    return f"{start_year}-fall"
                return f"{end_year}-spring"

        # 匹配：2025-2026-1 / 2025-2026-2
        # 约定：
        # 1 -> 2025-fall
        # 2 -> 2026-spring
        match = re.search(r"(20\d{2})\s*[-_/]\s*(20\d{2})\s*[-_/]\s*([12])", normalized)
        if match:
            start_year = int(match.group(1))
            end_year = int(match.group(2))
            term = match.group(3)

            if end_year == start_year + 1:
                if term == "1":
                    return f"{start_year}-fall"
                return f"{end_year}-spring"

        # 口语写法
        if "秋季学期" in message:
            year_match = re.search(r"(20\d{2})", message)
            if year_match:
                return f"{year_match.group(1)}-fall"

        if "春季学期" in message:
            year_match = re.search(r"(20\d{2})", message)
            if year_match:
                return f"{year_match.group(1)}-spring"

        return None