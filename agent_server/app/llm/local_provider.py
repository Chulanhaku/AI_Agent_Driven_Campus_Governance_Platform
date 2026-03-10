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