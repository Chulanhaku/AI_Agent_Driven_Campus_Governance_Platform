from app.llm.base import BaseLlmProvider


class SessionSummaryManager:
    def __init__(self, llm_provider: BaseLlmProvider) -> None:
        self.llm_provider = llm_provider

    def build_messages_text(self, recent_messages: list[dict], max_items: int = 6) -> str:
        lines = []
        for item in recent_messages[-max_items:]:
            role = item.get("role", "unknown")
            content = item.get("content", "")
            lines.append(f"{role}: {content}")
        return "\n".join(lines)

    def generate_title(
        self,
        *,
        recent_messages: list[dict],
    ) -> str:
        messages_text = self.build_messages_text(recent_messages, max_items=4)
        if not messages_text.strip():
            return "新会话"

        try:
            title = self.llm_provider.generate_session_title(messages_text=messages_text)
            return title[:30] if title else "新会话"
        except Exception:
            first_user_msg = next(
                (item["content"] for item in recent_messages if item.get("role") == "user"),
                "新会话",
            )
            return first_user_msg[:20]

    def generate_summary(
        self,
        *,
        existing_summary: str,
        recent_messages: list[dict],
    ) -> str:
        recent_messages_text = self.build_messages_text(recent_messages, max_items=8)

        try:
            summary = self.llm_provider.summarize_session(
                existing_summary=existing_summary,
                recent_messages_text=recent_messages_text,
            )
            return summary[:300] if summary else existing_summary
        except Exception:
            if existing_summary and recent_messages_text:
                return f"{existing_summary}；最近内容：{recent_messages_text[:120]}"
            if recent_messages_text:
                return f"会话摘要：{recent_messages_text[:160]}"
            return existing_summary