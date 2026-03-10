from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ChatSendRequestSchema(BaseModel):
    session_id: int | None = None
    content: str


class ChatConfirmRequestSchema(BaseModel):
    session_id: int
    action_id: int
    approved: bool


class ChatMessageSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    session_id: int
    role: str
    content: str
    message_type: str
    created_at: datetime


class ChatSendResponseSchema(BaseModel):
    session_id: int
    user_message: ChatMessageSchema
    assistant_message: ChatMessageSchema
    requires_confirmation: bool = False
    action_id: int | None = None


class ChatHistoryResponseSchema(BaseModel):
    session_id: int
    items: list[ChatMessageSchema]
    total: int