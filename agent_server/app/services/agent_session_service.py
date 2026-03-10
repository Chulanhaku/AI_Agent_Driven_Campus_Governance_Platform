from app.agent.context_builder import ContextBuilder
from app.agent.executor import Executor
from app.agent.planner import Planner
from app.agent.prompt_manager import PromptManager
from app.agent.response_formatter import ResponseFormatter
from app.agent.router import AgentRouter
from app.db.models import AgentMessage, AgentSession, User
from app.db.repositories.agent_session_repository import AgentSessionRepository
from app.db.repositories.pending_action_repository import PendingActionRepository
from app.llm.base import BaseLlmProvider
from app.services.audit_service import AuditService
from app.services.campus_card_service import CampusCardService
from app.services.leave_service import LeaveService
from app.services.schedule_service import ScheduleService
from app.services.tool_execution_log_service import ToolExecutionLogService
from app.tools.campus_card_tools import ExecuteCampusCardTopupTool, QueryCampusCardBalanceTool
from app.tools.leave_tools import ExecuteLeaveCreateTool
from app.tools.registry import ToolRegistry
from app.tools.schedule_tools import QueryMyScheduleTool
from app.workflows.leave_workflow import LeaveWorkflow
from app.workflows.recharge_workflow import RechargeWorkflow


class AgentSessionService:
    def __init__(
        self,
        agent_session_repository: AgentSessionRepository,
        pending_action_repository: PendingActionRepository,
        schedule_service: ScheduleService,
        campus_card_service: CampusCardService,
        leave_service: LeaveService,
        audit_service: AuditService,
        tool_execution_log_service: ToolExecutionLogService,
        llm_provider: BaseLlmProvider,
    ) -> None:
        self.agent_session_repository = agent_session_repository
        self.pending_action_repository = pending_action_repository
        self.schedule_service = schedule_service
        self.campus_card_service = campus_card_service
        self.leave_service = leave_service
        self.audit_service = audit_service
        self.tool_execution_log_service = tool_execution_log_service
        self.llm_provider = llm_provider

        self.router = AgentRouter(llm_provider=llm_provider)
        self.context_builder = ContextBuilder()
        self.planner = Planner()
        self.executor = Executor()
        self.response_formatter = ResponseFormatter()
        self.prompt_manager = PromptManager()

    def get_user_session(
        self,
        session_id: int,
        user_id: int,
    ) -> AgentSession | None:
        return self.agent_session_repository.get_session_by_id_and_user_id(
            session_id=session_id,
            user_id=user_id,
        )

    def list_session_messages(
        self,
        session_id: int,
        user_id: int,
    ) -> list[AgentMessage] | None:
        session = self.get_user_session(session_id=session_id, user_id=user_id)
        if session is None:
            return None

        return self.agent_session_repository.list_messages_by_session_id(session_id)

    def send_message(
        self,
        current_user: User,
        content: str,
        session_id: int | None = None,
    ) -> tuple[AgentSession, AgentMessage, AgentMessage, bool, int | None]:
        try:
            if session_id is None:
                session_title = content[:30]
                session = self.agent_session_repository.create_session(
                    user_id=current_user.id,
                    title=session_title,
                )
            else:
                session = self.agent_session_repository.get_session_by_id_and_user_id(
                    session_id=session_id,
                    user_id=current_user.id,
                )
                if session is None:
                    raise ValueError("Session not found")

            user_message = self.agent_session_repository.add_message(
                session_id=session.id,
                role="user",
                content=content,
                message_type="text",
            )

            assistant_reply_text, requires_confirmation, action_id = self._build_agent_reply(
                current_user=current_user,
                user_message=content,
                session_id=session.id,
            )

            assistant_message = self.agent_session_repository.add_message(
                session_id=session.id,
                role="assistant",
                content=assistant_reply_text,
                message_type="text",
            )

            self.agent_session_repository.commit()
            return session, user_message, assistant_message, requires_confirmation, action_id
        except Exception:
            self.agent_session_repository.rollback()
            raise

    def confirm_action(
        self,
        *,
        current_user: User,
        session_id: int,
        action_id: int,
        approved: bool,
    ) -> tuple[AgentSession, AgentMessage, AgentMessage]:
        session = self.agent_session_repository.get_session_by_id_and_user_id(
            session_id=session_id,
            user_id=current_user.id,
        )
        if session is None:
            raise ValueError("Session not found")

        action = self.pending_action_repository.get_by_id_and_user_id(
            action_id=action_id,
            user_id=current_user.id,
        )
        if action is None:
            raise ValueError("Pending action not found")

        if action.session_id != session.id:
            raise ValueError("Pending action does not belong to this session")

        if action.status != "pending":
            raise ValueError("Pending action is no longer available")

        try:
            user_text = "确认执行该操作" if approved else "取消该操作"
            user_message = self.agent_session_repository.add_message(
                session_id=session.id,
                role="user",
                content=user_text,
                message_type="confirm_request",
            )

            if not approved:
                self.pending_action_repository.update_status(action=action, status="rejected")
                assistant_text = "已取消本次操作。"
                assistant_message = self.agent_session_repository.add_message(
                    session_id=session.id,
                    role="assistant",
                    content=assistant_text,
                    message_type="text",
                )
                self.agent_session_repository.commit()

                self.audit_service.record(
                    user_id=current_user.id,
                    action="pending_action.cancel",
                    target_type="pending_action",
                    target_id=action.id,
                    detail_json={
                        "action_type": action.action_type,
                        "session_id": session.id,
                    },
                )

                return session, user_message, assistant_message

            if action.action_type == "campus_card_topup":
                amount = str(action.payload_json["amount"])
                tool = ExecuteCampusCardTopupTool(self.campus_card_service)

                tool_log = self.tool_execution_log_service.start_log(
                    session_id=session.id,
                    tool_name=tool.name,
                    input_json={
                        "user_id": current_user.id,
                        "amount": amount,
                    },
                )

                try:
                    result = tool.run(
                        user_id=current_user.id,
                        amount=amount,
                    )
                    self.tool_execution_log_service.finish_log(
                        log=tool_log,
                        output_json=result,
                        status="success",
                    )
                except Exception as exc:
                    self.tool_execution_log_service.finish_log(
                        log=tool_log,
                        output_json={"error": str(exc)},
                        status="failed",
                    )
                    raise

                self.pending_action_repository.update_status(action=action, status="approved")

                assistant_text = self.response_formatter.format(
                    intent="campus_card_topup",
                    result=result,
                )

                self.audit_service.record(
                    user_id=current_user.id,
                    action="campus_card.topup",
                    target_type="pending_action",
                    target_id=action.id,
                    detail_json={
                        "amount": amount,
                        "session_id": session.id,
                        "result": result.get("data"),
                    },
                )

            elif action.action_type == "leave_create":
                days = int(action.payload_json["days"])
                reason = str(action.payload_json["reason"])
                leave_type = str(action.payload_json.get("leave_type", "sick"))

                tool = ExecuteLeaveCreateTool(self.leave_service)

                tool_log = self.tool_execution_log_service.start_log(
                    session_id=session.id,
                    tool_name=tool.name,
                    input_json={
                        "user_id": current_user.id,
                        "days": days,
                        "reason": reason,
                        "leave_type": leave_type,
                    },
                )

                try:
                    result = tool.run(
                        user_id=current_user.id,
                        days=days,
                        reason=reason,
                        leave_type=leave_type,
                    )
                    self.tool_execution_log_service.finish_log(
                        log=tool_log,
                        output_json=result,
                        status="success",
                    )
                except Exception as exc:
                    self.tool_execution_log_service.finish_log(
                        log=tool_log,
                        output_json={"error": str(exc)},
                        status="failed",
                    )
                    raise

                self.pending_action_repository.update_status(action=action, status="approved")

                assistant_text = self.response_formatter.format(
                    intent="leave_create",
                    result=result,
                )

                self.audit_service.record(
                    user_id=current_user.id,
                    action="leave.create",
                    target_type="pending_action",
                    target_id=action.id,
                    detail_json={
                        "days": days,
                        "reason": reason,
                        "session_id": session.id,
                        "result": result.get("data"),
                    },
                )

            else:
                raise ValueError(f"Unsupported action type: {action.action_type}")

            assistant_message = self.agent_session_repository.add_message(
                session_id=session.id,
                role="assistant",
                content=assistant_text,
                message_type="text",
            )

            self.agent_session_repository.commit()
            return session, user_message, assistant_message
        except Exception:
            self.agent_session_repository.rollback()
            raise

    def _build_agent_reply(
        self,
        *,
        current_user: User,
        user_message: str,
        session_id: int,
    ) -> tuple[str, bool, int | None]:
        tool_registry = ToolRegistry()
        schedule_tool = QueryMyScheduleTool(self.schedule_service)
        balance_tool = QueryCampusCardBalanceTool(self.campus_card_service)

        tool_registry.register(schedule_tool)
        tool_registry.register(balance_tool)

        intent = self.router.detect_intent(user_message)

        amount = self.router.extract_amount(user_message)
        leave_days = self.router.extract_leave_days(user_message)
        leave_reason = self.router.extract_leave_reason(user_message)

        # 规则抽不出来，再让 LLM 补
        llm_slots = {}
        if (
            (intent == "campus_card_topup" and not amount)
            or (intent == "leave_create" and (not leave_days or not leave_reason))
        ):
            llm_slots = self.router.extract_slots_with_llm(
                intent=intent,
                message=user_message,
            )

        if intent == "campus_card_topup" and not amount:
            amount = llm_slots.get("amount")

        if intent == "leave_create":
            if not leave_days:
                leave_days = llm_slots.get("days")
            if not leave_reason:
                leave_reason = llm_slots.get("reason")

        context = self.context_builder.build(
            current_user=current_user,
            message=user_message,
            tool_registry=tool_registry,
        )
        context["session_id"] = session_id
        context["amount"] = amount
        context["leave_days"] = leave_days
        context["leave_reason"] = leave_reason

        plan = self.planner.build_plan(intent=intent, context=context)

        if plan.get("action") == "create_pending_topup":
            if not amount:
                return "我识别到你想充值校园卡，但没有解析到金额。比如你可以说：帮我充值 50 元。", False, None

            workflow = RechargeWorkflow(self.pending_action_repository)
            pending_action = workflow.create_pending_topup(
                current_user=current_user,
                session_id=session_id,
                amount=amount,
            )

            self.audit_service.record(
                user_id=current_user.id,
                action="pending_action.create",
                target_type="pending_action",
                target_id=pending_action.id,
                detail_json={
                    "action_type": "campus_card_topup",
                    "amount": amount,
                    "session_id": session_id,
                },
            )

            response_text = self.response_formatter.format(
                intent="campus_card_topup",
                result={
                    "requires_confirmation": True,
                    "amount": amount,
                    "action_id": pending_action.id,
                },
            )
            return response_text, True, pending_action.id

        if plan.get("action") == "create_pending_leave":
            if not leave_days:
                return "我识别到你想请假，但没有解析到请假天数。比如你可以说：我要请假 2 天，原因是发烧。", False, None

            if not leave_reason:
                return "我识别到你想请假，但没有解析到请假原因。比如你可以说：我要请假 2 天，原因是发烧。", False, None

            workflow = LeaveWorkflow(self.pending_action_repository)
            pending_action = workflow.create_pending_leave_request(
                current_user=current_user,
                session_id=session_id,
                days=int(leave_days),
                reason=str(leave_reason),
                leave_type="sick",
            )

            self.audit_service.record(
                user_id=current_user.id,
                action="pending_action.create",
                target_type="pending_action",
                target_id=pending_action.id,
                detail_json={
                    "action_type": "leave_create",
                    "days": leave_days,
                    "reason": leave_reason,
                    "session_id": session_id,
                },
            )

            response_text = self.response_formatter.format(
                intent="leave_create",
                result={
                    "requires_confirmation": True,
                    "days": leave_days,
                    "reason": leave_reason,
                    "action_id": pending_action.id,
                },
            )
            return response_text, True, pending_action.id

        result = self._execute_logged_tool(
            session_id=session_id,
            plan=plan,
            tool_registry=tool_registry,
        )

        if intent == "fallback" or plan.get("action") == "fallback":
            return self._build_fallback_reply(
                user_name=current_user.full_name,
                user_message=user_message,
            ), False, None

        if not result.get("success"):
            return "我识别到了你的业务请求，但执行过程中出了点问题。后面我们会补上更完整的错误处理。", False, None

        if intent == "query_schedule":
            self.audit_service.record(
                user_id=current_user.id,
                action="schedule.query",
                target_type="agent_session",
                target_id=session_id,
                detail_json={
                    "message": user_message,
                    "result_total": result.get("total", 0),
                },
            )

        return self.response_formatter.format(intent=intent, result=result), False, None

    def _execute_logged_tool(
        self,
        *,
        session_id: int,
        plan: dict,
        tool_registry: ToolRegistry,
    ) -> dict:
        if plan.get("action") != "call_tool":
            return self.executor.execute(plan=plan, tool_registry=tool_registry)

        tool_name = plan["tool_name"]
        params = plan.get("params", {})

        tool_log = self.tool_execution_log_service.start_log(
            session_id=session_id,
            tool_name=tool_name,
            input_json=params,
        )

        try:
            result = self.executor.execute(plan=plan, tool_registry=tool_registry)
            status = "success" if result.get("success") else "failed"

            self.tool_execution_log_service.finish_log(
                log=tool_log,
                output_json=result,
                status=status,
            )
            return result
        except Exception as exc:
            self.tool_execution_log_service.finish_log(
                log=tool_log,
                output_json={"error": str(exc)},
                status="failed",
            )
            raise

    def _build_fallback_reply(
        self,
        *,
        user_name: str,
        user_message: str,
    ) -> str:
        try:
            return self.llm_provider.generate_fallback_reply(
                user_name=user_name,
                message=user_message,
            )
        except Exception:
            return (
                f"你好，{user_name}。我已经收到你的消息：{user_message}。"
                "当前这条消息还没有匹配到已实现的 Agent 工具能力，所以先返回一条 fallback 回复。"
                "目前我已经开始支持“查课表”“校园卡充值”“请假申请”这三类请求。"
            )