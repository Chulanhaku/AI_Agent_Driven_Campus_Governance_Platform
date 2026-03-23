from datetime import datetime

from app.services.resource_booking_service import ResourceBookingService
from app.services.resource_service import ResourceService
from app.tools.base import BaseTool


class QueryAvailableResourcesTool(BaseTool):
    name = "query_available_resources"
    description = "查询指定时间段内可预约的资源"

    def __init__(self, resource_service: ResourceService) -> None:
        self.resource_service = resource_service

    def run(
        self,
        *,
        resource_type: str,
        start_time: str,
        end_time: str,
        **kwargs,
    ) -> dict:
        start_dt = datetime.fromisoformat(start_time)
        end_dt = datetime.fromisoformat(end_time)

        return self.resource_service.list_available_resources(
            resource_type=resource_type,
            start_time=start_dt,
            end_time=end_dt,
        )


class SubmitResourceBookingTool(BaseTool):
    name = "submit_resource_booking"
    description = "提交资源预约，该工具只应在用户确认后调用"

    def __init__(self, resource_booking_service: ResourceBookingService) -> None:
        self.resource_booking_service = resource_booking_service

    def run(
        self,
        *,
        user_id: int,
        resource_id: int,
        booking_type: str,
        start_time: str,
        end_time: str,
        **kwargs,
    ) -> dict:
        start_dt = datetime.fromisoformat(start_time)
        end_dt = datetime.fromisoformat(end_time)

        return self.resource_booking_service.create_booking(
            user_id=user_id,
            resource_id=resource_id,
            booking_type=booking_type,
            start_time=start_dt,
            end_time=end_dt,
        )


class CheckInResourceBookingTool(BaseTool):
    name = "check_in_resource_booking"
    description = "对已预约资源执行签到"

    def __init__(self, resource_booking_service: ResourceBookingService) -> None:
        self.resource_booking_service = resource_booking_service

    def run(
        self,
        *,
        booking_id: int,
        user_id: int,
        **kwargs,
    ) -> dict:
        return self.resource_booking_service.mark_checked_in(
            booking_id=booking_id,
            user_id=user_id,
        )