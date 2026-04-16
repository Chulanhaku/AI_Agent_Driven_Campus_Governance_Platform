from app.services.zero_form_approval_service import ZeroFormApprovalService
from app.tools.base import BaseTool


class GenerateZeroFormApprovalTool(BaseTool):
    name = "generate_zero_form_approval"
    description = "根据用户自然语言生成零表单审批草稿"

    def __init__(self, zero_form_approval_service: ZeroFormApprovalService) -> None:
        self.zero_form_approval_service = zero_form_approval_service

    def run(
        self,
        *,
        current_user_id: int,
        approval_type: str,
        parsed_fields: dict,
        **kwargs,
    ) -> dict:
        current_user = self.zero_form_approval_service.user_repository.get_by_id(current_user_id)
        if current_user is None:
            raise ValueError(f"用户不存在: current_user_id={current_user_id}")

        return self.zero_form_approval_service.build_form_draft(
            current_user=current_user,
            approval_type=approval_type,
            parsed_fields=parsed_fields,
        )

class SubmitZeroFormApprovalTool(BaseTool):
    name = "submit_zero_form_approval"
    description = "提交零表单审批申请，必须在用户确认后调用"

    def __init__(self, zero_form_approval_service: ZeroFormApprovalService) -> None:
        self.zero_form_approval_service = zero_form_approval_service

    def run(
        self,
        *,
        current_user,
        approval_type: str,
        template_id: int,
        approver_user_id: int | None,
        form_data: dict,
        **kwargs,
    ) -> dict:
        return self.zero_form_approval_service.submit_form_request(
            current_user=current_user,
            approval_type=approval_type,
            template_id=template_id,
            approver_user_id=approver_user_id,
            form_data=form_data,
        )