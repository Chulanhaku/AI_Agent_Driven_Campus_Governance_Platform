from app.tools.base import BaseTool


class PayUtilityBillTool(BaseTool):
    name = "pay_utility_bill"
    description = "处理用户校园电费及其他公用事业费用的查询与缴纳请求"

    def run(self, **kwargs) -> dict:
        return {
            "success": False,
            "message": "generated tool stub not implemented yet",
            "expected_inputs": {'bill_type': 'string', 'amount': 'number|null', 'payment_method': 'string|null'},
        }
