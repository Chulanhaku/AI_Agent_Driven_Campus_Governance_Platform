from pydantic import BaseModel


class LeaveRequestResponseSchema(BaseModel):
    leave_request_id: int
    leave_type: str
    start_date: str
    end_date: str
    reason: str
    status: str