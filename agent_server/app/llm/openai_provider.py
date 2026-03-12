import logging
from openai import OpenAI
import time

from app.config.settings import get_settings
from app.llm.base import BaseLlmProvider
from app.llm.output_parser import OutputParser

logger = logging.getLogger("app.llm")

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
- policy_qa
- fallback

用户消息:
{message}

输出格式:
{{
  "intent": "query_schedule|campus_card_topup|leave_create|policy_qa|fallback",
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

如果 intent == query_schedule 或 policy_qa，可返回空对象。

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
- 制度问答

用户姓名：{user_name}
用户消息：{message}

请直接给出回复正文。
""".strip()

        return self._chat(prompt).strip()

    def answer_with_context(
        self,
        *,
        user_name: str,
        question: str,
        context_text: str,
    ) -> str:
        prompt = f"""
你是校园综合事务 AI 助手。
请严格基于给定制度材料回答，不要编造材料中没有的信息。
如果材料不足以回答，请明确说“根据当前检索到的制度材料，无法确定”。

用户姓名：{user_name}
用户问题：{question}

制度材料：
{context_text}

请直接给出中文回答。
""".strip()

        return self._chat(prompt).strip()

    def _chat(self, prompt: str) -> str:
        start_time = time.perf_counter()
        prompt_len = len(prompt)
        trace_name = f"openai_{self.model}"

        logger.info(
            "[llm_call_start] trace_name=%s model=%s prompt_len=%s",
            trace_name,
            self.model,
            prompt_len,
        )
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "你是一个严谨的校务 AI 助手模块。"},
                {"role": "user", "content": prompt},
            ],
            temperature=0,
            extra_body={
                "enable_thinking": False
            }
        )

        elapsed_ms = (time.perf_counter() - start_time) * 1000

        logger.info(
            "[llm_call_end] trace_name=%s cost_ms=%.2f",
            trace_name,
            elapsed_ms,
        )
        return response.choices[0].message.content or ""
    
    def generate_session_title(self, *, messages_text: str) -> str:
        prompt = f"""
请根据下面的对话内容，生成一个简短中文会话标题。
要求：
1. 不超过 12 个字
2. 直接输出标题，不要加引号，不要解释
3. 标题要体现主要事务主题

对话内容：
{messages_text}
""".strip()

        return self._chat(prompt).strip()

    def summarize_session(
        self,
        *,
        existing_summary: str,
        recent_messages_text: str,
    ) -> str:
        prompt = f"""
你是一个会话摘要器。
请基于已有摘要和最近对话，输出更新后的会话摘要。
要求：
1. 使用中文
2. 控制在 120 字以内
3. 保留关键意图、关键槽位、当前状态
4. 直接输出摘要正文，不要解释

已有摘要：
{existing_summary or "无"}

最近对话：
{recent_messages_text}
""".strip()

        return self._chat(prompt).strip()
    
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
        prompt = f"""
你是校园综合事务 AI 助手。
请基于工具结果和用户原始需求，生成自然、简洁、有帮助的中文回复。

要求：
1. 必须回应用户原始问题
2. 不要只机械复述结构化结果
3. 如果用户除了主任务外还有附加诉求，也要一起回应
4. 不要编造工具结果中没有的事实
5. 可以给出合理建议，但要明确这是建议
6. 输出自然中文，不要写“根据工具结果”这种生硬说法

用户姓名：{user_name}
用户原始消息：{user_message}
主意图：{primary_intent}
附加意图：{secondary_intents}
会话摘要：{memory_summary or "无"}

工具结果摘要：
{tool_result_summary}

请直接输出最终回复正文。
""".strip()

        return self._chat(prompt).strip()