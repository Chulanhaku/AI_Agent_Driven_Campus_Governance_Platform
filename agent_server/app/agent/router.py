import re

from app.llm.base import BaseLlmProvider
from app.self_iteration import dynamic_plan_registry
from app.utils.semester_utils import SemesterUtils
from datetime import datetime, timedelta
from app.agent.intent_catalog import IntentCatalog

class AgentRouter:
    def __init__(
        self,
        llm_provider: BaseLlmProvider | None = None,
        capability_registry=None,
        dynamic_plan_registry=None,
    ) -> None:
        self.llm_provider = llm_provider
        self.capability_registry = capability_registry
        self.dynamic_plan_registry = dynamic_plan_registry

    # def detect_intent(self, message: str) -> str:
    #     rule_intent = self._detect_intent_by_rules(message)
    #     if rule_intent != "fallback":
    #         return rule_intent

    #     if self.llm_provider is not None:
    #         try:
    #             result = self.llm_provider.classify_intent(message=message)
    #             intent = result.get("intent", "fallback")
    #             if intent in {
    #                 "query_schedule",
    #                 "campus_card_topup",
    #                 "leave_create",
    #                 "policy_qa",
    #                 "fallback",
    #                 "course_plan_generate",
    #                 "course_plan_submit",
    #             }:
    #                 return intent
    #         except Exception:
    #             pass

    #     return "fallback"
    def get_supported_primary_intents(self) -> list[str]:
        dynamic_intents = []
        if self.dynamic_plan_registry is not None:
            dynamic_intents = self.dynamic_plan_registry.list_primary_intents()

        return IntentCatalog.merge_primary_intents(
            dynamic_primary_intents=dynamic_intents,
        )

    def parse_request(
        self,
        *,
        message: str,
        memory_summary: str | None = None,
    ) -> dict:
        rule_primary_intent = self.detect_intent(message=message)
        rule_secondary_intents = self.detect_secondary_intents(message=message)

        rule_slots = {
            "amount": self.extract_amount(message),
            "leave_days": self.extract_leave_days(message),
            "leave_reason": self.extract_leave_reason(message),
            "semester": self.extract_semester(message),
            "resource_type": self.extract_resource_type(message),
            "booking_start_time": None,
            "booking_end_time": None,
            "selected_plan_index": self.extract_plan_index(message),
            "selected_resource_index": self.extract_candidate_index(message),
        }

        booking_time_range = self.extract_booking_time_range(message)
        if booking_time_range is not None:
            rule_slots["booking_start_time"] = booking_time_range[0]
            rule_slots["booking_end_time"] = booking_time_range[1]
        supported_primary_intents = self.get_supported_primary_intents()
        supported_secondary_intents = IntentCatalog.get_static_secondary_intents()
        llm_result = None
        if self.llm_provider is not None:
            try:
                llm_result = self.llm_provider.parse_user_request(
                    message=message,
                    memory_summary=memory_summary,
                    supported_primary_intents=supported_primary_intents,
                    supported_secondary_intents=supported_secondary_intents,
                )
            except Exception:
                llm_result = None

        llm_primary_intent = None
        llm_secondary_intents: list[str] = []
        llm_slots: dict = {}

        if llm_result:
            llm_primary_intent = llm_result.get("primary_intent")
            llm_secondary_intents = llm_result.get("secondary_intents", []) or []
            llm_slots = llm_result.get("slots", {}) or {}

        resolved_primary_intent = rule_primary_intent
        if resolved_primary_intent == "fallback" and llm_primary_intent:
            resolved_primary_intent = llm_primary_intent

        resolved_secondary_intents = list(dict.fromkeys(rule_secondary_intents + llm_secondary_intents))

        resolved_slots = {}
        for key, rule_value in rule_slots.items():
            resolved_slots[key] = rule_value if rule_value not in (None, [], "") else llm_slots.get(key)

        return {
            "primary_intent": resolved_primary_intent,
            "secondary_intents": resolved_secondary_intents,
            "slots": resolved_slots,
            "rule_primary_intent": rule_primary_intent,
            "llm_primary_intent": llm_primary_intent,
        }




    def detect_intent(
        self,
        *,
        message: str,
        memory_context: dict | None = None,
    ) -> str:
        if self.capability_registry is not None:
            aliased_intent = self.capability_registry.resolve_intent_alias(message=message)
            if aliased_intent:
                return aliased_intent

        rule_intent = self._detect_intent_by_rules(
            message=message,
            memory_context=memory_context,
        )
        if rule_intent != "fallback":
            return rule_intent

        if self.llm_provider is not None:
            try:
                recent_messages_text = self._build_recent_messages_text(memory_context)
                result = self.llm_provider.classify_intent(
                    message=message,
                    recent_messages_text=recent_messages_text,
                )
                intent = result.get("intent", "fallback")
                allowed_intent = set(self.get_supported_primary_intents())
                if intent in allowed_intent:
                    return intent
                # if intent in {
                #     "query_schedule",
                #     "campus_card_topup",
                #     "leave_create",
                #     "policy_qa",
                #     "fallback",
                #     "course_plan_generate",
                #     "course_plan_submit",
                #     "resource_booking_generate",
                #     "resource_booking_submit",
                #     "zero_form_approval_generate",
                #     "zero_form_approval_submit",
                #     "dynamic_course_catalog_query",
                # }:
                #     return intent
            except Exception:
                pass

        return "fallback"

    def _detect_intent_by_rules(
        self,
        *,
        message: str,
        memory_context: dict | None = None,
    ) -> str:
        return "fallback"
        normalized = message.strip().lower()

        policy_keywords = [
            "学生手册",
            "手册",
            "规定",
            "制度",
            "规则",
            "要求",
            "审批",
            "流程",
            "条件",
            "几天",
            "多久",
            "超过",
            "怎么办",
            "怎么处理",
            "如何处理",
            "怎么申请",
            "如何申请",
            "是否可以",
            "可不可以",
            "能不能",
            "要不要",
            "?",
            "？",
        ]

        leave_keywords = [
            "请假",
            "我要请假",
            "请病假",
            "请事假",
            "leave",
        ]

        topup_keywords = [
            "充值",
            "充钱",
            "充校园卡",
            "校园卡充值",
            "topup",
            "recharge",
        ]

        schedule_keywords = [
            "课表",
            "课程表",
            "schedule",
            "明天上什么课",
            "今天上什么课",
            "这周课表",
            "今天课表",
            "明天课表",
        ]

        course_plan_keywords = [
            "选课方案",
            "帮我选课",
            "安排选课",
            "生成选课方案",
            "本学期选课",
            "最优选课",
            "课程安排方案",
            "选课",
        ]
        course_plan_submit_keywords = [
            "选方案",
            "提交方案",
            "就这个方案",
            "提交选课方案",
            "把方案提交",
        ]

        resource_booking_submit_keywords = [
            "选第一个",
            "选第二个",
            "选第三个",
            "预约这个",
            "就这个",
            "提交预约",
            "帮我预约它",
        ]
        for keyword in resource_booking_submit_keywords:
            if keyword in normalized:
                return "resource_booking_submit"

        resource_booking_keywords = [
            "预约图书馆",
            "预约自习室",
            "预约会议室",
            "预约实验室",
            "图书馆座位",
            "找自习室",
            "找会议室",
            "找实验室",
            "帮我预约",
            "我要预约",
        ]

        zero_form_submit_keywords = [
            "提交审批",
            "确认提交审批",
            "提交这个申请",
            "就按这个提交",
        ]
        for keyword in zero_form_submit_keywords:
            if keyword in normalized:
                return "zero_form_approval_submit"

        zero_form_generate_keywords = [
            "帮我申请",
            "帮我提交申请",
            "帮我填申请",
            "我想申请",
            "我要申请",
            "开证明",
            "外出申请",
            "请假申请",
        ]
        for keyword in zero_form_generate_keywords:
            if keyword in normalized:
                return "zero_form_approval_generate"

        for keyword in resource_booking_keywords:
            if keyword in normalized:
                return "resource_booking_generate"
        for keyword in course_plan_submit_keywords:
            if keyword in normalized:
                return "course_plan_submit"
        for keyword in course_plan_keywords:
            if keyword in normalized:
                return "course_plan_generate"

        if "请假" in normalized and any(keyword in normalized for keyword in policy_keywords):
            return "policy_qa"

        if re.search(r"第[一二三四五六七八九十百千零两0-9]+(章|条)", message):
            return "policy_qa"

        if any(keyword in normalized for keyword in policy_keywords):
            return "policy_qa"


        for keyword in leave_keywords:
            if keyword in normalized:
                return "leave_create"


        for keyword in topup_keywords:
            if keyword in normalized:
                return "campus_card_topup"

        for keyword in course_plan_submit_keywords:
            if keyword in normalized:
                return "course_plan_submit"

        for keyword in schedule_keywords:
            if keyword in normalized:
                print("rule matched query_schedule")
                return "query_schedule"

        return "fallback"

    def extract_amount(self, message: str) -> str | None:
        match = re.search(r"(\d+(?:\.\d{1,2})?)", message)
        if match:
            return match.group(1)
        return None

    def extract_leave_days(self, message: str) -> int | None:

        match = re.search(r"(\d+)\s*天", message)
        if match:
            return int(match.group(1))


        if "半天" in message:
            return 0


        chinese_day_mapping = {
            "一天": 1,
            "两天": 2,
            "二天": 2,
            "三天": 3,
            "四天": 4,
            "五天": 5,
            "六天": 6,
            "七天": 7,
            "八天": 8,
            "九天": 9,
            "十天": 10,
        }

        for text, days in chinese_day_mapping.items():
            if text in message:
                return days

        return None

    def extract_leave_reason(self, message: str) -> str | None:
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

    def extract_slots_with_llm(self, *, intent: str, message: str) -> dict:
        if self.llm_provider is None:
            return {}

        try:
            return self.llm_provider.extract_slots(intent=intent, message=message)
        except Exception:
            return {}
        
    def detect_secondary_intents(self, message: str) -> list[str]:
        normalized = message.strip().lower()
        results: list[str] = []

        planning_keywords = [
            "几点出门",
            "怎么安排时间",
            "安排一下",
            "帮我规划",
            "时间安排",
            "怎么去",
            "多久出门",
        ]
        if any(keyword in normalized for keyword in planning_keywords):
            results.append("time_planning_advice")

        busyness_keywords = [
            "哪天最忙",
            "这周哪天最满",
            "什么时候最忙",
            "哪天课最多",
        ]
        if any(keyword in normalized for keyword in busyness_keywords):
            results.append("weekly_busyness_analysis")


        summary_keywords = [
            "顺便告诉我",
            "另外",
            "并且",
            "并安排",
            "顺便安排",
        ]
        if any(keyword in normalized for keyword in summary_keywords):
            if "time_planning_advice" not in results and any(
                keyword in normalized for keyword in planning_keywords
            ):
                results.append("time_planning_advice")

        return results
    
    def _build_recent_messages_text(
        self,
        memory_context: dict | None,
    ) -> str:
        if not memory_context:
            return ""

        recent_messages = memory_context.get("recent_messages", [])
        summary_text = memory_context.get("summary_text", "")

        lines: list[str] = []

        if summary_text:
            lines.append(f"会话摘要：{summary_text}")

        if recent_messages:
            lines.append("最近对话：")
            for item in recent_messages[-6:]:
                role = item.get("role", "unknown")
                content = (item.get("content") or "").strip()
                if content:
                    lines.append(f"{role}: {content}")

        return "\n".join(lines)
    
    def extract_selected_plan_index(self, message: str) -> int | None:
        normalized = message.strip().lower()

        patterns = [
            r"方案\s*([1-9]\d*)",
            r"第\s*([1-9]\d*)\s*套",
            r"第\s*([1-9]\d*)\s*个",
            r"我选\s*([1-9]\d*)",
            r"选\s*([1-9]\d*)",
        ]

        for pattern in patterns:
            match = re.search(pattern, normalized)
            if match:
                return int(match.group(1))

        chinese_mapping = {
            "方案一": 1,
            "方案二": 2,
            "方案三": 3,
            "第一套": 1,
            "第二套": 2,
            "第三套": 3,
            "第一个": 1,
            "第二个": 2,
            "第三个": 3,
            "我选第一套": 1,
            "我选第二套": 2,
            "我选第三套": 3,
        }

        for text, index in chinese_mapping.items():
            if text in message:
                return index

        return None
    
    def extract_resource_type(self, message: str) -> str | None:
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
    

    def extract_candidate_index(self, message: str) -> int | None:
        import re

        match = re.search(r"第\s*(\d+)\s*个", message)
        if match:
            return int(match.group(1))

        match = re.search(r"选\s*(\d+)", message)
        if match:
            return int(match.group(1))

        match = re.search(r"资源\s*(\d+)", message)
        if match:
            return int(match.group(1))

        return None
    

    def extract_plan_index(self, message: str) -> int | None:
        match = re.search(r"方案\s*(\d+)", message)
        if match:
            return int(match.group(1))

        match = re.search(r"选\s*方案\s*(\d+)", message)
        if match:
            return int(match.group(1))

        return None

    def extract_booking_time_range(self, message: str) -> tuple[str, str] | None:
        normalized = message.strip().lower()
        now = datetime.now()

        # 默认：今天未来一小时到两小时
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
    
    def extract_semester(self, message: str) -> str | None:
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