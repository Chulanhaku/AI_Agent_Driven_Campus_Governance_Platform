from app.services.notification_service import NotificationService
from app.tools.base import BaseTool

class ExecuteSendNotificationTool(BaseTool):
    # 这是 AI 在调用时看到的工具名称和描述
    name = "execute_send_notification"
    description = "给指定用户发送通知消息。当你需要提醒用户重要事项时调用此工具。"

    def __init__(self, notification_service: NotificationService) -> None:
        self.notification_service = notification_service

    def run(self, *, user_id: int, message: str, **kwargs) -> dict:
        # 调用 Service 层的方法
        data = self.notification_service.send_notification(
            user_id=user_id,
            message=message
        )
        return {
            "success": True,
            "tool_name": self.name,
            "data": data,
        }