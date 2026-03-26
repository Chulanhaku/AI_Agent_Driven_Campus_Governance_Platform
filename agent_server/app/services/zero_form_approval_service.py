from app.db.models import User
from app.db.repositories.approval_request_repository import ApprovalRequestRepository
from app.db.repositories.approval_template_repository import ApprovalTemplateRepository
from app.db.repositories.user_repository import UserRepository


class ZeroFormApprovalService:
    def __init__(
        self,
        approval_template_repository: ApprovalTemplateRepository,
        approval_request_repository: ApprovalRequestRepository,
        user_repository: UserRepository,
    ) -> None:
        self.approval_template_repository = approval_template_repository
        self.approval_request_repository = approval_request_repository
        self.user_repository = user_repository

    def build_form_draft(
        self,
        *,
        current_user: User,
        approval_type: str,
        parsed_fields: dict,
    ) -> dict:
        template = self.approval_template_repository.get_active_by_approval_type(
            approval_type=approval_type,
        )
        if template is None:
            return {
                "success": False,
                "message": f"当前没有可用的审批模板：{approval_type}",
            }

        base_form_data = {
            "student_id": getattr(current_user, "username", None),
            "student_name": current_user.full_name,
            "approval_type": approval_type,
        }

        merged_form_data = {
            **base_form_data,
            **parsed_fields,
        }

        missing_fields = []
        required_fields = template.required_fields_json or []
        for field_name in required_fields:
            if merged_form_data.get(field_name) in (None, "", []):
                missing_fields.append(field_name)

        approver = self._resolve_approver_by_role_code(
            role_code=template.approver_role_code,
        )

        return {
            "success": True,
            "approval_type": approval_type,
            "template_id": template.id,
            "template_name": template.template_name,
            "approver_user_id": approver.id if approver else None,
            "approver_name": approver.full_name if approver else None,
            "form_data": merged_form_data,
            "missing_fields": missing_fields,
        }

    def submit_form_request(
        self,
        *,
        current_user: User,
        approval_type: str,
        template_id: int,
        approver_user_id: int | None,
        form_data: dict,
    ) -> dict:
        try:
            item = self.approval_request_repository.create_request(
                user_id=current_user.id,
                template_id=template_id,
                approval_type=approval_type,
                form_data_json=form_data,
                approver_user_id=approver_user_id,
                status="pending",
            )
            self.approval_request_repository.commit()

            return {
                "success": True,
                "request_id": item.id,
                "approval_type": approval_type,
                "approver_user_id": approver_user_id,
                "status": item.status,
            }
        except Exception:
            self.approval_request_repository.rollback()
            raise

    def _resolve_approver_by_role_code(
        self,
        *,
        role_code: str,
    ) -> User | None:
        # 当前随便做做：在 user_repository 中找第一个 active 且角色匹配的人
        return self.user_repository.get_first_active_user_by_role_code(role_code=role_code)