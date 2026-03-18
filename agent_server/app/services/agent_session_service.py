import logging
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
from app.rag.retriever import Retriever
from app.services.audit_service import AuditService
from app.services.campus_card_service import CampusCardService
from app.services.leave_service import LeaveService
from app.services.schedule_service import ScheduleService
from app.services.tool_execution_log_service import ToolExecutionLogService
from app.tools.campus_card_tools import ExecuteCampusCardTopupTool, QueryCampusCardBalanceTool
from app.tools.leave_tools import ExecuteLeaveCreateTool
from app.tools.rag_tools import QueryPolicyKnowledgeTool
from app.tools.registry import ToolRegistry
from app.tools.schedule_tools import QueryMyScheduleTool
from app.workflows.leave_workflow import LeaveWorkflow
from app.workflows.recharge_workflow import RechargeWorkflow
from app.agent.memory import MemoryManager
from app.db.repositories.agent_session_memory_repository import AgentSessionMemoryRepository
from app.services.agent_memory_service import AgentMemoryService
from app.agent.session_manager import SessionSummaryManager
from app.agent.response_composer import ResponseComposer
from app.services.course_plan_service import CoursePlanService
from app.tools.course_plan_tools import GenerateCoursePlanTool, SubmitCoursePlanTool
from app.services.course_enrollment_service import CourseEnrollmentService
from app.workflows.course_plan_workflow import CoursePlanWorkflow
from app.services.notification_service import NotificationService
from app.tools.notification_tools import ExecuteSendNotificationTool


logger = logging.getLogger(__name__)


class AgentSessionService:
    def __init__(
        self,
        agent_session_repository: AgentSessionRepository,
        agent_memory_service: AgentMemoryService,    #addded
        pending_action_repository: PendingActionRepository,
        schedule_service: ScheduleService,
        campus_card_service: CampusCardService,
        leave_service: LeaveService,
        audit_service: AuditService,
        tool_execution_log_service: ToolExecutionLogService,
        llm_provider: BaseLlmProvider,
        retriever: Retriever,
        rag_top_k: int,
        course_plan_service: CoursePlanService,
        course_enrollment_service: CourseEnrollmentService,
    ) -> None:
        self.agent_session_repository = agent_session_repository
        self.pending_action_repository = pending_action_repository
        self.schedule_service = schedule_service
        self.campus_card_service = campus_card_service
        self.leave_service = leave_service
        self.audit_service = audit_service
        self.tool_execution_log_service = tool_execution_log_service
        self.llm_provider = llm_provider
        self.retriever = retriever
        self.rag_top_k = rag_top_k

        self.router = AgentRouter(llm_provider=llm_provider)
        self.context_builder = ContextBuilder()
        self.planner = Planner(llm_provider=llm_provider)
        self.executor = Executor()
        self.response_formatter = ResponseFormatter()
        self.prompt_manager = PromptManager()
        self.agent_memory_service = agent_memory_service
        self.memory_manager = MemoryManager(agent_session_repository)
        self.session_summary_manager = SessionSummaryManager(llm_provider)
        self.response_composer = ResponseComposer(llm_provider)
        self.notification_service = NotificationService()

        self.course_plan_service = course_plan_service
        self.course_enrollment_service = course_enrollment_service

    def get_user_session(self, session_id: int, user_id: int) -> AgentSession | None:
        return self.agent_session_repository.get_session_by_id_and_user_id(
            session_id=session_id,
            user_id=user_id,
        )

    def list_session_messages(self, session_id: int, user_id: int) -> list[AgentMessage] | None:
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
                session = self.agent_session_repository.create_session(
                    user_id=current_user.id,
                    title=content[:30],
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

            recent_memory_context = self.memory_manager.build_memory_context(
                session_id=session.id,
                limit=8,
            )

            # 只在 title 为空或过于原始时更新标题
            if not session.title or session.title == content[:30]:
                generated_title = self.session_summary_manager.generate_title(
                    recent_messages=recent_memory_context.get("recent_messages", []),
                )
                self.agent_session_repository.update_title(
                    session=session,
                    title=generated_title,
                )

            existing_memory = self.agent_memory_service.get_session_memory(session.id)
            existing_summary = existing_memory.summary_text if existing_memory else ""

            generated_summary = self.session_summary_manager.generate_summary(
                existing_summary=existing_summary or "",
                recent_messages=recent_memory_context.get("recent_messages", []),
            )

            # self.agent_memory_service.save_memory_snapshot(
            #     session_id=session.id,
            #     summary_text=generated_summary,
            #     current_intent=recent_memory_context.get("current_intent"),
            #     slot_snapshot_json=recent_memory_context.get("slot_memory"),
            # )
            latest_memory = self.agent_memory_service.get_session_memory(session.id)
            latest_slot_snapshot = latest_memory.slot_snapshot_json if latest_memory else {}

            # merged_slot_snapshot = dict(latest_slot_snapshot or {})
            # merged_slot_snapshot.update(recent_memory_context.get("slot_memory", {}) or {})

            self.agent_memory_service.save_memory_snapshot(
                session_id=session.id,
                summary_text=generated_summary,
                current_intent=recent_memory_context.get("current_intent"),
                slot_snapshot_json=latest_slot_snapshot,
            )
#
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
                    input_json={"user_id": current_user.id, "amount": amount},
                )

                try:
                    result = tool.run(user_id=current_user.id, amount=amount)
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

            elif action.action_type == "course_plan_submit":
                semester = str(action.payload_json["semester"])
                selected_plan = dict(action.payload_json["selected_plan"])

                tool = SubmitCoursePlanTool(self.course_enrollment_service)

                tool_log = self.tool_execution_log_service.start_log(
                    session_id=session.id,
                    tool_name=tool.name,
                    input_json={
                        "user_id": current_user.id,
                        "semester": semester,
                        "selected_plan": selected_plan,
                    },
                )

                try:
                    result = tool.run(
                        user_id=current_user.id,
                        semester=semester,
                        selected_plan=selected_plan,
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
                    intent="course_plan_submit",
                    result=result,
                )

                self.audit_service.record(
                    user_id=current_user.id,
                    action="course_plan.submit",
                    target_type="pending_action",
                    target_id=action.id,
                    detail_json={
                        "semester": semester,
                        "session_id": session.id,
                        "result": result,
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
        rag_tool = QueryPolicyKnowledgeTool(self.retriever, top_k=self.rag_top_k)
        course_plan_tool = GenerateCoursePlanTool(self.course_plan_service)
        notification_tool = ExecuteSendNotificationTool(self.notification_service)

        tool_registry.register(schedule_tool)
        tool_registry.register(balance_tool)
        tool_registry.register(rag_tool)
        tool_registry.register(course_plan_tool)
        tool_registry.register(notification_tool)

        persisted_memory_obj = self.agent_memory_service.get_session_memory(session_id)
        persisted_memory = None

        if persisted_memory_obj is not None:
            persisted_memory = {
                "summary_text": persisted_memory_obj.summary_text,
                "current_intent": persisted_memory_obj.current_intent,
                "slot_snapshot_json": persisted_memory_obj.slot_snapshot_json,
            }

        memory_context = self.memory_manager.build_memory_context(
            session_id=session_id,
            limit=8,
            persisted_memory=persisted_memory,
        )
        slot_memory = memory_context.get("slot_memory", {})

        intent = self.router.detect_intent(
            message=user_message,
            memory_context=memory_context,
        )
        secondary_intents = self.router.detect_secondary_intents(user_message)

        amount = self.router.extract_amount(user_message)
        leave_days = self.router.extract_leave_days(user_message)
        leave_reason = self.router.extract_leave_reason(user_message)
        selected_plan_index = self.router.extract_selected_plan_index(user_message)



        if intent == "fallback":
            pending_intent = slot_memory.get("pending_intent")
            if pending_intent in {
                "campus_card_topup",
                "leave_create",
                "query_schedule",
            }:
                intent = pending_intent

        if not amount:
            amount = (
                slot_memory.get("campus_card_topup", {})
                .get("amount")
            )

        if not leave_days:
            leave_days = (
                slot_memory.get("leave_create", {})
                .get("days")
            )

        if not leave_reason:
            leave_reason = (
                slot_memory.get("leave_create", {})
                .get("reason")
            )

        llm_slots = {}
        if (
            (intent == "campus_card_topup" and not amount)
            or (intent == "leave_create" and (not leave_days or not leave_reason))
            or (intent == "course_plan_submit" and not selected_plan_index)
        ):
            llm_slots = self.router.extract_slots_with_llm(intent=intent, message=user_message)
        if intent == "course_plan_submit" and not selected_plan_index:
            selected_plan_index = llm_slots.get("selected_plan_index")
        print("LLM extracted slots:", llm_slots)
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
            memory_context=memory_context,
        )
        context["secondary_intents"] = secondary_intents   # wait for test
        self.agent_memory_service.save_memory_snapshot(
            session_id=session_id,
            summary_text=memory_context.get("summary_text"),
            current_intent=memory_context.get("current_intent"),
            slot_snapshot_json=memory_context.get("slot_memory"),
        )
        context["session_id"] = session_id
        context["amount"] = amount
        context["leave_days"] = leave_days
        context["leave_reason"] = leave_reason
        context["semester"] = "2026-spring"   # for course planning, hardcoded for now, can be extracted from message or user profile in the future

        if selected_plan_index is None:
            selected_plan_index = (
                memory_context.get("slot_memory", {})
                .get("course_plan_generate", {})
                .get("selected_plan_index")
            )

        context["selected_plan_index"] = selected_plan_index

        use_llm_planner = self.prompt_manager.should_use_llm_planner(
            primary_intent=intent,
            secondary_intents=secondary_intents,
            user_message=user_message,
        )

        print("service line 517",intent, secondary_intents, use_llm_planner)
        plan = self.planner.build_plan(
            intent=intent,
            context=context,
            use_llm_planner=use_llm_planner,
        )

        self.audit_service.record(
            user_id=current_user.id,
            action="agent.plan.generated",
            target_type="agent_session",
            target_id=session_id,
            detail_json={
                "intent": intent,
                "secondary_intents": secondary_intents,
                "use_llm_planner": use_llm_planner,
                "plan": plan,
            },
        )


        steps = plan.get("steps", [])
        first_step_type = steps[0]["type"] if steps else "fallback"

        if first_step_type == "create_pending_topup":
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

        if first_step_type == "create_pending_leave":
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

        if first_step_type == "create_pending_course_plan_submit":
            slot_memory = memory_context.get("slot_memory", {})
            course_plan_memory = slot_memory.get("course_plan_generate", {})
            last_generated_plans = course_plan_memory.get("last_generated_plans", [])
            selected_plan_index = context.get("selected_plan_index")

            if not selected_plan_index:
                return "我识别到你想提交选课方案，但没有解析到方案编号。比如你可以说：选方案2。", False, None

            if not last_generated_plans:
                return "当前会话中还没有可提交的候选选课方案，请先让我为你生成选课方案。", False, None

            if selected_plan_index < 1 or selected_plan_index > len(last_generated_plans):
                return f"方案编号超出范围。当前共有 {len(last_generated_plans)} 套候选方案。", False, None

            selected_plan = last_generated_plans[selected_plan_index - 1]
            semester = course_plan_memory.get("semester") or "2026-spring"

            workflow = CoursePlanWorkflow(self.pending_action_repository)
            pending_action = workflow.create_pending_submit(
                current_user=current_user,
                session_id=session_id,
                semester=semester,
                selected_plan=selected_plan,
                selected_plan_index=selected_plan_index,
            )

            self.audit_service.record(
                user_id=current_user.id,
                action="pending_action.create",
                target_type="pending_action",
                target_id=pending_action.id,
                detail_json={
                    "action_type": "course_plan_submit",
                    "semester": semester,
                    "selected_plan_index": selected_plan_index,
                    "session_id": session_id,
                },
            )

            response_text = self.response_formatter.format(
                intent="course_plan_submit",
                result={
                    "requires_confirmation": True,
                    "selected_plan_index": selected_plan_index,
                    "action_id": pending_action.id,
                },
            )
            return response_text, True, pending_action.id
        print("Generated plan:", plan)
        execution_result = self._execute_multistep_plan(
            session_id=session_id,
            plan=plan,
            tool_registry=tool_registry,
            user_message=user_message,
        )

        if execution_result.get("fallback"):
            return self._build_fallback_reply(
                user_name=current_user.full_name,
                user_message=user_message,
                memory_context=memory_context,
            ), False, None

        if not execution_result.get("success"):
            return "我识别到了你的业务请求，但执行过程中出了点问题。后面我们会补上更完整的错误处理。", False, None
        
        if intent == "query_schedule":
            self.audit_service.record(
                user_id=current_user.id,
                action="schedule.query",
                target_type="agent_session",
                target_id=session_id,
                detail_json={
                    "message": user_message,
                    "secondary_intents": secondary_intents,
                },
            )

            tool_result_summary = self._build_tool_result_summary(
                primary_intent=intent,
                execution_result=execution_result,
            )
            reasoning_result_summary = self._build_reasoning_result_summary(
                execution_result=execution_result,
            )

            final_reply = self.response_composer.compose(
                user_name=current_user.full_name,
                user_message=user_message,
                primary_intent=intent,
                secondary_intents=secondary_intents,
                tool_result_summary=tool_result_summary,
                reasoning_result_summary=reasoning_result_summary,
                memory_summary=memory_context.get("summary_text"),
            )
            return final_reply, False, None

        if intent == "policy_qa":
            tool_result_summary = self._build_tool_result_summary(
                primary_intent=intent,
                execution_result=execution_result,
            )

            final_reply = self.response_composer.compose(
                user_name=current_user.full_name,
                user_message=user_message,
                primary_intent=intent,
                secondary_intents=secondary_intents,
                tool_result_summary=tool_result_summary,
                reasoning_result_summary=None,
                memory_summary=memory_context.get("summary_text"),
            )

            self.audit_service.record(
                user_id=current_user.id,
                action="policy.query",
                target_type="agent_session",
                target_id=session_id,
                detail_json={
                    "question": user_message,
                    "secondary_intents": secondary_intents,
                },
            )

            retrieval_appendix = self._build_policy_retrieval_appendix(
                execution_result=execution_result,
            )
            if retrieval_appendix:
                final_reply = f"{final_reply}\n\n{retrieval_appendix}"

            return final_reply, False, None
        
        if intent == "course_plan_generate":
            self.audit_service.record(
                user_id=current_user.id,
                action="course_plan.generate",
                target_type="agent_session",
                target_id=session_id,
                detail_json={
                    "message": user_message,
                },
            )

            tool_result_summary = self._build_tool_result_summary(
                primary_intent=intent,
                execution_result=execution_result,
            )

            final_reply = self.response_composer.compose(
                user_name=current_user.full_name,
                user_message=user_message,
                primary_intent=intent,
                secondary_intents=secondary_intents,
                tool_result_summary=tool_result_summary,
                reasoning_result_summary=None,
                memory_summary=memory_context.get("summary_text"),
            )


            updated_slot_snapshot = memory_context.get("slot_memory", {}).copy()
            updated_slot_snapshot["course_plan_generate"] = {
                "semester": execution_result.get("tool_results", {})
                    .get("generate_course_plan", {})
                    .get("semester"),
                "last_generated_plans": execution_result.get("tool_results", {})
                    .get("generate_course_plan", {})
                    .get("plans", []),
                "selected_plan_index": None,
            }

            self.agent_memory_service.save_memory_snapshot(
                session_id=session_id,
                summary_text=memory_context.get("summary_text"),
                current_intent="course_plan_generate",
                slot_snapshot_json=updated_slot_snapshot,
            )
            return final_reply, False, None

        return self.response_formatter.format(intent=intent, result=execution_result), False, None
    
    # old query
        # result = self._execute_logged_tool(
        #     session_id=session_id,
        #     plan=plan,
        #     tool_registry=tool_registry,
        # )

        # if intent == "fallback" or plan.get("action") == "fallback":
        #     return self._build_fallback_reply(
        #         user_name=current_user.full_name,
        #         user_message=user_message,
        #         memory_context=memory_context,
        #     ), False, None

        # if not result.get("success"):
        #     return "我识别到了你的业务请求，但执行过程中出了点问题。后面我们会补上更完整的错误处理。", False, None

        # if intent == "query_schedule":
        #     self.audit_service.record(
        #         user_id=current_user.id,
        #         action="schedule.query",
        #         target_type="agent_session",
        #         target_id=session_id,
        #         detail_json={
        #             "message": user_message,
        #             "result_total": result.get("total", 0),
        #         },
        #     )

        #     #
        #     # tool_result_summary = self.response_formatter.format(intent=intent, result=result)

        #     # secondary_intents = self.router.detect_secondary_intents(user_message)

        #     # if secondary_intents:
        #     #     reply = self.llm_provider.compose_tool_response(
        #     #         user_name=current_user.full_name,
        #     #         user_message=user_message,
        #     #         primary_intent=intent,
        #     #         secondary_intents=secondary_intents,
        #     #         tool_result_summary=tool_result_summary,
        #     #         memory_summary=memory_context.get("summary_text"),
        #     #     )
        #     #     return reply, False, None


        #     # reply = self.llm_provider.compose_tool_response(
        #     #     user_name=current_user.full_name,
        #     #     user_message=user_message,
        #     #     primary_intent=intent,
        #     #     secondary_intents=[],
        #     #     tool_result_summary=tool_result_summary,
        #     #     memory_summary=memory_context.get("summary_text"),
        #     # )
        #     # return reply, False, None
        #     #

        #     return self.response_formatter.format(intent=intent, result=result), False, None

        # if intent == "policy_qa":
        #     items = result.get("items", [])
        #     context_text = "\n\n".join(
        #         f"[{item['filename']}] {item['content']}" for item in items
        #     )

        #     answer = self.llm_provider.answer_with_context(
        #         user_name=current_user.full_name,
        #         question=user_message,
        #         context_text=context_text,
        #     )

        #     self.audit_service.record(
        #         user_id=current_user.id,
        #         action="policy.query",
        #         target_type="agent_session",
        #         target_id=session_id,
        #         detail_json={
        #             "question": user_message,
        #             "result_total": result.get("total", 0),
        #         },
        #     )
        #     return answer, False, None

        # return self.response_formatter.format(intent=intent, result=result), False, None

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
    
    def _execute_multistep_plan(
        self,
        *,
        session_id: int,
        plan: dict,
        tool_registry: ToolRegistry,
        user_message: str,
    ) -> dict:
        steps = plan.get("steps", [])

        tool_results: dict = {}
        reasoning_results: dict = {}

        for step in steps:
            step_type = step.get("type")

            if step_type == "call_tool":
                tool_name = step["tool_name"]
                params = step.get("params", {})

                tool_log = self.tool_execution_log_service.start_log(
                    session_id=session_id,
                    tool_name=tool_name,
                    input_json=params,
                )

                try:
                    tool = tool_registry.get(tool_name)
                    if tool is None:
                        self.tool_execution_log_service.finish_log(
                            log=tool_log,
                            output_json={"error": f"Tool not found: {tool_name}"},
                            status="failed",
                        )
                        return {
                            "success": False,
                            "error": f"Tool not found: {tool_name}",
                            "tool_results": tool_results,
                            "reasoning_results": reasoning_results,
                        }

                    result = tool.run(**params)
                    tool_results[tool_name] = result

                    self.tool_execution_log_service.finish_log(
                        log=tool_log,
                        output_json=result,
                        status="success" if result.get("success") else "failed",
                    )

                    if not result.get("success"):
                        return {
                            "success": False,
                            "error": f"Tool execution failed: {tool_name}",
                            "tool_results": tool_results,
                            "reasoning_results": reasoning_results,
                        }

                except Exception as exc:
                    self.tool_execution_log_service.finish_log(
                        log=tool_log,
                        output_json={"error": str(exc)},
                        status="failed",
                    )
                    raise

            elif step_type == "reason":
                goal = step["goal"]
                result = self.executor.reasoning_engine.reason(
                    goal=goal,
                    tool_results=tool_results,
                    user_message=user_message,
                )
                reasoning_results[goal] = result

            elif step_type == "compose":
                continue

            elif step_type == "fallback":
                return {
                    "success": False,
                    "fallback": True,
                    "tool_results": tool_results,
                    "reasoning_results": reasoning_results,
                }

            elif step_type in {"create_pending_topup", "create_pending_leave"}:
                return {
                    "success": True,
                    "workflow_step": step,
                    "tool_results": tool_results,
                    "reasoning_results": reasoning_results,
                }

        return {
            "success": True,
            "tool_results": tool_results,
            "reasoning_results": reasoning_results,
        }





    def _build_fallback_reply(
        self,
        *,
        user_name: str,
        user_message: str,
        memory_context: dict | None = None,
    ) -> str:
        recent_messages = memory_context.get("recent_messages", []) if memory_context else []
        summary_text = memory_context.get("summary_text", "") if memory_context else ""

        memory_text = ""
        if recent_messages:
            lines = []
            for item in recent_messages[-4:]:
                lines.append(f"{item['role']}: {item['content']}")
            memory_text = "\n".join(lines)

        prompt_message = user_message
        if summary_text or memory_text:
            prompt_message = (
                f"会话摘要：{summary_text}\n\n"
                f"最近对话：\n{memory_text}\n\n"
                f"用户当前消息：{user_message}"
            )

        try:
            return self.llm_provider.generate_fallback_reply(
                user_name=user_name,
                message=prompt_message,
            )
        except Exception:
            return (
                f"你好，{user_name}。我已经收到你的消息：{user_message}。"
                "当前这条消息还没有匹配到已实现的 Agent 工具能力，所以先返回一条 fallback 回复。"
            )


    def _build_tool_result_summary(
        self,
        *,
        primary_intent: str,
        execution_result: dict,
    ) -> str:
        tool_results = execution_result.get("tool_results", {})

        if primary_intent == "query_schedule":
            schedule_result = tool_results.get("query_my_schedule", {})
            return self.response_formatter.format(
                intent="query_schedule",
                result=schedule_result,
            )

        if primary_intent == "policy_qa":
            policy_result = tool_results.get("query_policy_knowledge", {})
            return self.response_formatter.format(
                intent="policy_qa",
                result=policy_result,
            )

        if primary_intent == "course_plan_generate":
            course_plan_result = tool_results.get("generate_course_plan", {})
            return self.response_formatter.format(
                intent="course_plan_generate",
                result=course_plan_result,
            )

        return "已完成相关工具调用。"

    def _build_reasoning_result_summary(
        self,
        *,
        execution_result: dict,
    ) -> str:
        reasoning_results = execution_result.get("reasoning_results", {})
        lines: list[str] = []

        if "time_planning_advice" in reasoning_results:
            result = reasoning_results["time_planning_advice"]
            if result.get("success"):
                items = result.get("items", [])
                for item in items:
                    lines.append(
                        f"{item['course_name']}（星期{item['weekday']} {item['class_start_time']}）"
                        f"建议约 {item['suggested_departure_time']} 出门。"
                    )

        if "weekly_busyness_analysis" in reasoning_results:
            result = reasoning_results["weekly_busyness_analysis"]
            if result.get("success"):
                busiest_weekday = result.get("busiest_weekday")
                weekday_count = result.get("weekday_count", {})
                if busiest_weekday is not None:
                    lines.append(
                        f"课表分析显示，星期{busiest_weekday} 课程最多，"
                        f"当天共有 {weekday_count.get(busiest_weekday, 0)} 节安排。"
                    )

        return "\n".join(lines)

    def _build_policy_retrieval_appendix(
        self,
        *,
        execution_result: dict,
    ) -> str:
        tool_results = execution_result.get("tool_results", {})
        policy_result = tool_results.get("query_policy_knowledge", {})
        items = policy_result.get("items", [])

        if not items:
            return ""

        lines = ["检索依据："]
        filtered_items: list[dict] = []
        seen_keys: set[str] = set()
        seen_filenames: set[str] = set()
        for item in items:
            dedupe_key = self._build_policy_item_key(item)
            if not dedupe_key or dedupe_key in seen_keys:
                continue

            filename = (item.get("filename") or "").strip().lower()
            if filename in seen_filenames:
                continue

            seen_keys.add(dedupe_key)
            seen_filenames.add(filename)
            filtered_items.append(item)
            if len(filtered_items) >= 3:
                break

        for idx, item in enumerate(filtered_items, start=1):
            filename = item.get("filename") or "unknown"
            score = float(item.get("score", 0.0))
            content = (item.get("content") or "").strip().replace("\n", " ")
            snippet = content[:180]
            lines.append(f"{idx}. [{filename}] (score={score:.2f}) {snippet}")

        return "\n".join(lines)

    def _build_policy_item_key(self, item: dict) -> str:
        import re

        filename = (item.get("filename") or "").strip().lower()
        content = (item.get("content") or "").strip().replace("\n", " ")
        normalized = " ".join(content.split())

        marker_match = re.search(
            r"第[一二三四五六七八九十百千零两0-9]+(条|章)", normalized
        )
        if marker_match:
            return f"{filename}:{marker_match.group(0)}"

        return f"{filename}:{normalized[:160]}"
