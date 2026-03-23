from datetime import datetime

from app.db.repositories.resource_repository import ResourceRepository


class ResourceService:
    def __init__(self, resource_repository: ResourceRepository) -> None:
        self.resource_repository = resource_repository

    def list_available_resources(
        self,
        *,
        resource_type: str,
        start_time: datetime,
        end_time: datetime,
    ) -> dict:
        items = self.resource_repository.list_available_resources_for_timeslot(
            resource_type=resource_type,
            start_time=start_time,
            end_time=end_time,
        )

        return {
            "success": True,
            "resource_type": resource_type,
            "total": len(items),
            "items": [
                {
                    "resource_id": item.id,
                    "resource_code": item.resource_code,
                    "resource_name": item.resource_name,
                    "resource_type": item.resource_type,
                    "location": item.location,
                    "capacity": item.capacity,
                    "status": item.status,
                }
                for item in items
            ],
        }