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


    def parse_user_request(
        self,
        *,
        message: str,
        memory_summary: str | None = None,
    ) -> dict:
        prompt = f"""
你是一个校园事务 Agent 的请求解析器。
请从用户输入中提取：
1. primary_intent
2. secondary_intents
3. slots

请只输出 JSON，不要输出任何额外文字。

支持的 primary_intent:
- query_schedule
- campus_card_topup
- leave_create
- policy_qa
- course_plan_generate
- course_plan_submit
- resource_booking_generate
- resource_booking_submit
- zero_form_approval_generate
- zero_form_approval_submit
- fallback

支持的 secondary_intents:
- time_planning_advice
- weekly_busyness_analysis

请提取可能的 slots：
- amount: 字符串或 null
- leave_days: 整数或 null
- leave_reason: 字符串或 null
- semester: 例如 "2026-spring" 或 null
- resource_type: library_seat / study_room / meeting_room / lab_room / null
- booking_start_time: ISO 8601 字符串或 null
- booking_end_time: ISO 8601 字符串或 null
- selected_plan_index: 整数或 null
- selected_resource_index: 整数或 null
- approval_type: leave_application / outing_application / certificate_request / null
- approval_reason: 字符串或 null
- start_date: YYYY-MM-DD 或 null #这个是给零表单审批用的，表示请假/外出/证明的开始日期
- end_date: YYYY-MM-DD 或 null  #对应的结束日期

要求：
1. 不确定就填 null 或 []
2. 不要编造事实
3. 如果用户是多意图表达，要尽量识别 secondary_intents
4. 如果用户只是在选择之前的方案或资源，也要识别 submit 类 intent,并且submit 类 intent 的优先级要高于 generate 类 intent
5. 如果用户是在发起审批申请，例如“帮我申请外出”“帮我开在读证明”“我要请假申请”等类似的语言，primary_intent 应为 zero_form_approval_generate。如果用户是在确认提交已经生成好的审批草稿，primary_intent 应为 zero_form_approval_submit。
6. 所有index都是1为基底的
7. 如果用户的要求很明显是可以正常支持的intent,不在目前支持的primary_intent范围内，primary_intent 应为 fallback  //以方便生成新的能力提案
8. query_schedule 是专属于课表查询的，其他时刻表不能使用query_schedule

会话摘要：
{memory_summary or "无"}

用户消息：
{message}

输出示例：
{{
  "primary_intent": "resource_booking_generate",
  "secondary_intents": [],
  "slots": {{
    "amount": null,
    "leave_days": null,
    "leave_reason": null,
    "semester": null,
    "resource_type": "study_room",
    "booking_start_time": "2026-03-24T14:00:00",
    "booking_end_time": "2026-03-24T16:00:00",
    "selected_plan_index": null,
    "selected_resource_index": null,
    "approval_type": "certificate_request",
    "approval_reason": null,
    "start_date": null,
    "end_date": null
  }}
}}
""".strip()

        content = self._chat(prompt)
        return self.output_parser.parse_json(content)



    def classify_intent(
        self,
        *,
        message: str,
        recent_messages_text: str | None = None,
    ) -> dict:
        prompt = f"""
你是一个校务 Agent 的意图分类器。
请只输出 JSON，不要输出任何额外文字。

支持的 intent:
- query_schedule
- campus_card_topup
- leave_create
- policy_qa
- course_plan_generate
- course_plan_submit
- resource_booking_generate
- resource_booking_submit
- zero_form_approval_generate
- zero_form_approval_submit
- fallback

分类规则：
1. 用户请求生成、推荐、安排选课方案时，返回 course_plan_generate
2. 用户在已有方案中做选择、确认、提交时，返回 course_plan_submit
3. 像“第一套”“第二套”“方案1”“方案一”“我选第一套”“就这个方案”这类，
如果结合最近对话可知是在确认已生成的选课方案，优先返回 course_plan_submit
4. 用户询问制度、规则、流程、条件，或提到“学生手册”“第X章”“第X条”时，返回 policy_qa
5. 无法确定时返回 fallback
6.如果用户是在找图书馆座位、自习室、会议室、实验室并希望预约，分类为 resource_booking_generate。
如果用户是在已有候选资源中选择某个资源，例如“选第一个”“预约这个”“就这个”，分类为 resource_booking_submit。
7. 如果用户是在发起审批申请，例如“帮我申请外出”“帮我开在读证明”“我要请假申请”等类似的语言，primary_intent 应为 zero_form_approval_generate。如果用户是在确认提交已经生成好的审批草稿，primary_intent 应为 zero_form_approval_submit。

最近对话：
{recent_messages_text or "无"}

用户消息：
{message}

输出格式:
{{
"intent": "query_schedule|campus_card_topup|leave_create|policy_qa|fallback|course_plan_generate|course_plan_submit",
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

如果 intent == course_plan_submit，请提取:
- selected_plan_index: 整数，无法提取则为 null

如果 intent == resource_booking_generate，请提取:
- resource_type: library_seat / study_room / meeting_room / lab_room / null
- booking_start_time: ISO 8601 字符串或 null
- booking_end_time: ISO 8601 字符串或 null

如果 intent == resource_booking_submit，请提取:
- selected_resource_index: 整数，一般用户会直接第几套就是几，无法提取则为 null
- booking_start_time: ISO 8601 字符串或 null
- booking_end_time: ISO 8601 字符串或 null

如果 intent == zero_form_approval_generate，请提取:
- approval_type: leave_application / outing_application / certificate_request / null
- reason: 字符串，无法提取则为 null
- start_date: YYYY-MM-DD 或 null
- end_date: YYYY-MM-DD 或 null

如果 intent == query_schedule 或 policy_qa 或 course_plan_generate，可返回空对象。

用户消息:
{message}

输出示例:
{{
  "amount": null,
  "days": null,
  "reason": null,
  "leave_type": "sick",
  "selected_plan_index": null,
  "resource_type": "study_room",
  "booking_start_time": "2026-03-24T14:00:00",
  "booking_end_time": "2026-03-24T16:00:00",
  "selected_resource_index": null
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
    

    def generate_execution_plan(
        self,
        *,
        user_message: str,
        available_tools: list[str],
        primary_intent: str,
        secondary_intents: list[str],
        memory_summary: str | None,
    ) -> dict:
        prompt = f"""
你是一个校园事务 Agent 的执行计划生成器。
请根据用户请求生成一个安全、简洁的执行计划。

规则：
1. 只允许输出 JSON
2. 只允许以下 step.type:
   - call_tool
   - reason
   - compose
   - fallback
3. 只允许以下工具名：
   {available_tools}
4. 只允许以下 reasoning goal：
   - time_planning_advice
   - weekly_busyness_analysis
5. 不要生成任何未列出的工具或步骤
6. 对于充值和请假这类需要确认的事务，不要在这里规划 create_pending_topup / create_pending_leave，仍由系统规则处理
7. 如果不确定，就返回 fallback
8.当 primary_intent == course_plan_generate 时：
- 必须优先调用 generate_course_plan
- 不允许调用 query_available_resources
- 如果 secondary_intents 包含 time_planning_advice，可在 generate_course_plan 后追加 reason
- 最后追加 compose

9.当 primary_intent == resource_booking_generate 时：
- 必须优先调用 query_available_resources
- 不允许调用 generate_course_plan
- 如果缺少 resource_type / booking_start_time / booking_end_time，则返回 fallback

用户消息：
{user_message}

主意图：
{primary_intent}

附加意图：
{secondary_intents}

会话摘要：
{memory_summary or "无"}

输出格式示例：
{{
  "plan_type": "multi_step",
  "steps": [
    {{
      "type": "call_tool",
      "tool_name": "query_my_schedule",
      "params": {{
        "user_id": "$CURRENT_USER_ID",
        "semester": null,
        "weekday": null
      }}
    }},
    {{
      "type": "reason",
      "goal": "time_planning_advice"
    }},
    {{
      "type": "compose"
    }}
  ]
}}
""".strip()

        content = self._chat(prompt)
        return self.output_parser.parse_json(content)
    
    
    
    
    def generate_capability_proposal(
        self,
        *,
        user_message: str,
        research_summary: dict,
        memory_summary: str | None,
    ) -> dict:
        prompt = f"""
你是一个校园事务 Agent 的能力设计器。
当前系统在处理用户请求时进入了 fallback，现在需要生成一条“能力提案”。

请只输出 JSON，不要输出任何额外文字。

目标：
根据用户消息、会话摘要、已有 research 信息，设计一条可执行的能力提案。
提案类型仅允许：
- knowledge_patch
- plan_patch
- tool_spec

要求：
1. 如果只是已有能力的表达方式扩展，优先输出 knowledge_patch
2. 如果可以基于现有工具和 planner 扩展实现，输出 plan_patch
3. 如果确实需要新工具，输出 tool_spec
4. 不要编造数据库表名
5. 不要输出 Python 代码，只输出结构化提案
6. capability_name 使用 snake_case

用户消息：
{user_message}

会话摘要：
{memory_summary or "无"}

research_summary：
{research_summary}

输出示例：
{{
  "proposal_type": "tool_spec",
  "capability_name": "query_shuttle_schedule",
  "needs_new_tool": true,
  "intent_aliases": ["校车时刻表", "班车时间"],
  "planner_patch": null,
  "tool_spec": {{
    "name": "query_shuttle_schedule",
    "description": "查询校车时刻表",
    "inputs": {{
      "campus": "string|null",
      "date": "string|null"
    }},
    "read_only": true,
    "data_sources": ["web_research", "db_search"]
  }},
  "reason": "用户需要查询校车时刻表，当前系统缺少该能力"
}}
""".strip()

        content = self._chat(prompt)
        return self.output_parser.parse_json(content)