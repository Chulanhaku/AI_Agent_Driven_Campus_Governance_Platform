from app.services.leave_service import LeaveService
from app.tools.base import BaseTool


class ExecuteLeaveCreateTool(BaseTool):
    name = "execute_leave_create"
    description = "创建并提交请假申请。该工具应当只在用户确认后调用"

    def __init__(self, leave_service: LeaveService) -> None:
        self.leave_service = leave_service

    def run(
        self,
        *,
        user_id: int,
        days: int,
        reason: str,
        leave_type: str = "sick",
        **kwargs,
    ) -> dict:
        data = self.leave_service.create_leave_request(
            user_id=user_id,
            days=days,
            reason=reason,
            leave_type=leave_type,
        )
        return {
            "success": True,
            "tool_name": self.name,
            "data": data,
        }