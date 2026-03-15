class NotificationService:
    def send_notification(self, user_id: int, message: str) -> dict:
        # 这里是业务逻辑层，未来可以接入第三方短信或钉钉/企业微信接口
        print(f"[系统日志] 正在执行发送通知：给用户 {user_id} 发送消息 - {message}")
        
        # 返回一个简单的状态，方便 Agent 确认执行成功
        return {
            "status": "success",
            "user_id": user_id,
            "message": message
        }