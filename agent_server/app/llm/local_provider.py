from app.llm.base import BaseLlmProvider


class LocalLlmProvider(BaseLlmProvider):
    def classify_intent(self, *, message: str) -> dict:
        return {
            "intent": "fallback",
            "confidence": 0.0,
        }

    def extract_slots(self, *, intent: str, message: str) -> dict:
        return {}

    def generate_fallback_reply(self, *, user_name: str, message: str) -> str:
        return (
            f"你好，{user_name}。我已经收到你的消息：{message}。"
            "当前模型提供器还处于 mock/local 占位状态，所以这里只返回一条基础回复。"
        )

    def answer_with_context(
        self,
        *,
        user_name: str,
        question: str,
        context_text: str,
    ) -> str:
        return (
            f"我检索到了以下制度内容，可供参考：\n\n"
            f"{context_text}\n\n"
            f"你的问题是：{question}\n"
            f"当前是本地/mock 模式，所以先直接返回检索结果摘要。"
        )

    def generate_session_title(self, *, messages_text: str) -> str:
        lines = [line.strip() for line in messages_text.splitlines() if line.strip()]
        if not lines:
            return "新会话"
        first = lines[0]
        return first[:20]

    def summarize_session(
        self,
        *,
        existing_summary: str,
        recent_messages_text: str,
    ) -> str:
        if existing_summary and recent_messages_text:
            return f"{existing_summary}；最近内容：{recent_messages_text[:120]}"
        if recent_messages_text:
            return f"会话摘要：{recent_messages_text[:160]}"
        return existing_summary or ""

    def compose_tool_response(
        self,
        *,
        user_name: str,
        user_message: str,
        primary_intent: str,
        secondary_intents: list[str],
        tool_result_summary: str,
        memory_summary: str | None,
    ) -> str:
        extra_text = ""
        if secondary_intents:
            extra_text = f"\n附加诉求：{', '.join(secondary_intents)}"

        return (
            f"{tool_result_summary}\n\n"
            f"这是基于当前工具结果整理的回复。"
            f"{extra_text}"
        )