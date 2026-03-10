from app.services.campus_card_service import CampusCardService
from app.tools.base import BaseTool


class QueryCampusCardBalanceTool(BaseTool):
    name = "query_campus_card_balance"
    description = "查询当前登录用户的校园卡余额"

    def __init__(self, campus_card_service: CampusCardService) -> None:
        self.campus_card_service = campus_card_service

    def run(self, *, user_id: int, **kwargs) -> dict:
        data = self.campus_card_service.get_balance(user_id=user_id)
        return {
            "success": True,
            "tool_name": self.name,
            "data": data,
        }


class ExecuteCampusCardTopupTool(BaseTool):
    name = "execute_campus_card_topup"
    description = "执行校园卡充值。该工具应该只在用户确认后调用"

    def __init__(self, campus_card_service: CampusCardService) -> None:
        self.campus_card_service = campus_card_service

    def run(self, *, user_id: int, amount: str, **kwargs) -> dict:
        data = self.campus_card_service.topup(user_id=user_id, amount=amount)
        return {
            "success": True,
            "tool_name": self.name,
            "data": data,
        }