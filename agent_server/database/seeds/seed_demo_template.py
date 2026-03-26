from app.db.models import ApprovalTemplate
from app.db.session import SessionLocal


def seed_demo_approval_templates() -> None:
    db = SessionLocal()
    try:
        exists = db.query(ApprovalTemplate).first()
        if exists:
            print("approval templates already exist")
            return

        items = [
            ApprovalTemplate(
                template_code="leave_application_v1",
                template_name="请假申请",
                approval_type="leave_application",
                description="学生请假申请模板",
                required_fields_json=["reason", "start_date", "end_date"],
                approver_role_code="teacher",
                status="active",
            ),
            ApprovalTemplate(
                template_code="outing_application_v1",
                template_name="外出申请",
                approval_type="outing_application",
                description="学生外出申请模板",
                required_fields_json=["reason", "start_date", "end_date"],
                approver_role_code="teacher",
                status="active",
            ),
            ApprovalTemplate(
                template_code="certificate_request_v1",
                template_name="在读证明申请",
                approval_type="certificate_request",
                description="学生在读证明申请模板",
                required_fields_json=["reason"],
                approver_role_code="teacher",
                status="active",
            ),
        ]

        db.add_all(items)
        db.commit()
        print("seed demo approval templates success")
    except Exception as exc:
        db.rollback()
        print(f"seed demo approval templates failed: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_demo_approval_templates()