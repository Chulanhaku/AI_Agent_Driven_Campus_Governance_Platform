from openai import OpenAI

from app.config.settings import get_settings
from app.llm.base import BaseLlmProvider
from app.llm.output_parser import OutputParser


class OpenAiProvider(BaseLlmProvider):
    def __init__(self) -> None:
        settings = get_settings()

        client_kwargs = {
            "api_key": settings.openai_api_key,
        }
        if settings.openai_base_url:
            client_kwargs["base_url"] = settings.openai_base_url

        self.client = OpenAI(**client_kwargs)
        self.model = settings.openai_model
        self.output_parser = OutputParser()

    def classify_intent(self, *, message: str) -> dict:
        prompt = f"""
你是一个校务 Agent 的意图分类器。
请只输出 JSON，不要输出任何额外文字。

支持的 intent:
- query_schedule
- campus_card_topup
- leave_create
- fallback

用户消息:
{message}

输出格式:
{{
  "intent": "query_schedule|campus_card_topup|leave_create|fallback",
  "confidence": 0.0
}}
""".strip()

        content = self._chat(prompt)
        return self.output_parser.parse_json(content)

    def extract_slots(self, *, intent: str, message: str) -> dict:
        prompt = f"""
你是一个校务 Agent 的参数提取器。
请只输出 JSON，不要输出任何额外文字。

当前 intent:
{intent}

如果 intent == campus_card_topup，请提取:
- amount: 字符串，无法提取则为 null

如果 intent == leave_create，请提取:
- days: 整数，无法提取则为 null
- reason: 字符串，无法提取则为 null
- leave_type: 固定返回 "sick"

如果 intent == query_schedule，可返回空对象。

用户消息:
{message}

输出示例:
{{
  "amount": "50",
  "days": 2,
  "reason": "发烧",
  "leave_type": "sick"
}}
""".strip()

        content = self._chat(prompt)
        return self.output_parser.parse_json(content)

    def generate_fallback_reply(self, *, user_name: str, message: str) -> str:
        prompt = f"""
你是一个校园综合事务 AI 助手。
请用简洁、自然的中文回答用户，不要编造系统已经具备的功能。
当前系统已支持：
- 查课表
- 校园卡充值
- 请假申请

用户姓名：{user_name}
用户消息：{message}

请直接给出回复正文。
""".strip()

        return self._chat(prompt).strip()

    def _chat(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "你是一个严谨的校务 AI 助手模块。"},
                {"role": "user", "content": prompt},
            ],
            temperature=0,
        )
        return response.choices[0].message.content or ""