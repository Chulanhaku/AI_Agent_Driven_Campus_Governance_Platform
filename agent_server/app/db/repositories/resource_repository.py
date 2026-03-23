from datetime import datetime

from sqlalchemy.orm import Session

from app.db.models import Resource, ResourceBooking


class ResourceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_available_resources(
        self,
        *,
        resource_type: str,
    ) -> list[Resource]:
        return (
            self.db.query(Resource)
            .filter(
                Resource.resource_type == resource_type,
                Resource.status == "available",
            )
            .order_by(Resource.id.asc())
            .all()
        )

    def list_available_resources_for_timeslot(
        self,
        *,
        resource_type: str,
        start_time: datetime,
        end_time: datetime,
    ) -> list[Resource]:
        resources = self.list_available_resources(resource_type=resource_type)
        available_resources: list[Resource] = []

        for resource in resources:
            conflict = (
                self.db.query(ResourceBooking)
                .filter(
                    ResourceBooking.resource_id == resource.id,
                    ResourceBooking.status.in_(["pending", "confirmed", "checked_in"]),
                    ResourceBooking.start_time < end_time,
                    ResourceBooking.end_time > start_time,
                )
                .first()
            )
            if conflict is None:
                available_resources.append(resource)

        return available_resources