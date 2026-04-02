from app.db.repositories.notification_repository import NotificationRepository


class NotificationService:
    def __init__(self, notification_repository: NotificationRepository) -> None:
        self.notification_repository = notification_repository

    def create_notification(
        self,
        *,
        user_id: int,
        title: str,
        content: str,
        notification_type: str,
        related_type: str | None = None,
        related_id: int | None = None,
    ) -> dict:
        try:
            item = self.notification_repository.create_notification(
                user_id=user_id,
                title=title,
                content=content,
                notification_type=notification_type,
                related_type=related_type,
                related_id=related_id,
            )
            self.notification_repository.commit()

            return {
                "success": True,
                "notification_id": item.id,
                "user_id": item.user_id,
                "title": item.title,
                "content": item.content,
                "notification_type": item.notification_type,
                "is_read": item.is_read,
            }
        except Exception:
            self.notification_repository.rollback()
            raise

    def create_notification_from_payload(
        self,
        *,
        payload: dict,
    ) -> dict:
        return self.create_notification(
            user_id=payload["user_id"],
            title=payload["title"],
            content=payload["content"],
            notification_type=payload["notification_type"],
            related_type=payload.get("related_type"),
            related_id=payload.get("related_id"),
        )

    def list_my_notifications(
        self,
        *,
        user_id: int,
        unread_only: bool = False,
        limit: int = 20,
    ) -> list[dict]:
        items = self.notification_repository.list_by_user_id(
            user_id=user_id,
            unread_only=unread_only,
            limit=limit,
        )

        return [
            {
                "id": item.id,
                "title": item.title,
                "content": item.content,
                "notification_type": item.notification_type,
                "related_type": item.related_type,
                "related_id": item.related_id,
                "is_read": item.is_read,
                "read_at": item.read_at.isoformat() if item.read_at else None,
                "created_at": item.created_at.isoformat() if item.created_at else None,
            }
            for item in items
        ]

    def mark_my_notification_as_read(
        self,
        *,
        notification_id: int,
        user_id: int,
    ) -> dict:
        item = self.notification_repository.get_by_id_and_user_id(
            notification_id=notification_id,
            user_id=user_id,
        )
        if item is None:
            raise ValueError("Notification not found")

        try:
            item = self.notification_repository.mark_as_read(notification=item)
            self.notification_repository.commit()

            return {
                "success": True,
                "notification_id": item.id,
                "is_read": item.is_read,
                "read_at": item.read_at.isoformat() if item.read_at else None,
            }
        except Exception:
            self.notification_repository.rollback()
            raise

    def build_resource_booking_confirmed_payload(
        self,
        *,
        user_id: int,
        booking_id: int,
        resource_name: str,
        start_time: str,
        end_time: str,
        check_in_deadline: str | None,
    ) -> dict:
        return {
            "user_id": user_id,
            "title": "资源预约成功",
            "content": (
                f"你已成功预约资源：{resource_name}。"
                f"预约单号：{booking_id}；开始时间：{start_time}；结束时间：{end_time}。"
                f"{'签到截止：' + check_in_deadline + '。' if check_in_deadline else ''}"
            ),
            "notification_type": "resource_booking_confirmed",
            "related_type": "resource_booking",
            "related_id": booking_id,
        }

    def build_no_show_notification_payload(
        self,
        *,
        user_id: int,
        booking_id: int,
        resource_name: str,
        score_delta: int,
    ) -> dict:
        return {
            "user_id": user_id,
            "title": "预约已失约",
            "content": (
                f"你的资源预约（{resource_name}，预约单号 {booking_id}）因未按时签到已自动释放。"
                f"诚信分变动：{score_delta}。"
            ),
            "notification_type": "resource_booking_no_show",
            "related_type": "resource_booking",
            "related_id": booking_id,
        }
        
    def build_zero_form_submitted_to_approver_payload(
        self,
        *,
        approver_user_id: int,
        request_id: int,
        approval_type: str,
        applicant_name: str,
    ) -> dict:
        return {
            "user_id": approver_user_id,
            "title": "新的审批申请待处理",
            "content": (
                f"{applicant_name} 提交了一条 {approval_type} 审批申请，"
                f"审批单号：{request_id}，请及时处理。"
            ),
            "notification_type": "zero_form_approval_pending",
            "related_type": "zero_form_approval_request",
            "related_id": request_id,
        }

    def build_zero_form_result_to_applicant_payload(
        self,
        *,
        applicant_user_id: int,
        request_id: int,
        approval_type: str,
        status: str,
    ) -> dict:
        status_text = "已通过" if status == "approved" else "已驳回"
        return {
            "user_id": applicant_user_id,
            "title": "审批结果通知",
            "content": (
                f"你的 {approval_type} 审批申请已处理，"
                f"审批单号：{request_id}，当前结果：{status_text}。"
            ),
            "notification_type": "zero_form_approval_result",
            "related_type": "zero_form_approval_request",
            "related_id": request_id,
        }