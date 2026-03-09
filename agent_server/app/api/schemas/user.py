from pydantic import BaseModel, ConfigDict


class CurrentUserSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    full_name: str
    role_id: int
    status: str