from datetime import time

from pydantic import BaseModel, ConfigDict


class CourseSimpleSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    course_code: str
    course_name: str
    semester: str


class ScheduleEntrySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    weekday: int
    start_time: time
    end_time: time
    classroom: str | None
    week_range: str
    semester: str
    course: CourseSimpleSchema


class ScheduleListResponseSchema(BaseModel):
    items: list[ScheduleEntrySchema]
    total: int