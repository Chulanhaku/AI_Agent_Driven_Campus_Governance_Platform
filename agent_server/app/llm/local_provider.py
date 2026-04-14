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
    
    def parse_user_request(
        self,
        *,
        message: str,
        memory_summary: str | None = None,
    ) -> dict:
        return {
            "primary_intent": "fallback",
            "secondary_intents": [],
            "slots": {},
        }
    
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
    

    def generate_execution_plan(
        self,
        *,
        user_message: str,
        available_tools: list[str],
        primary_intent: str,
        secondary_intents: list[str],
        memory_summary: str | None,
    ) -> dict:
        return {
            "plan_type": "fallback",
            "steps": [
                {
                    "type": "fallback",
                }
            ],
        }
        
    def generate_capability_proposal(
        self,
        *,
        user_message: str,
        research_summary: dict,
        memory_summary: str | None,
    ) -> dict:
        normalized = user_message.strip().lower()

        capability_name = "unknown_capability"
        if "校车" in normalized or "班车" in normalized:
            capability_name = "query_shuttle_schedule"
        elif "羽毛球馆" in normalized:
            capability_name = "book_badminton_court"
        elif "成绩单" in normalized:
            capability_name = "export_transcript"

        return {
            "proposal_type": "tool_spec",
            "capability_name": capability_name,
            "needs_new_tool": True,
            "intent_aliases": [],
            "reason": "local/mock provider generated fallback capability proposal",
            "research_summary": research_summary,
            "confidence_score": 0.55,
            "risk_level": "medium",
        }