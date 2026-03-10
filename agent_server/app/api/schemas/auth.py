from pydantic import BaseModel


class LoginRequestSchema(BaseModel):
    username: str
    password: str


class LoginResponseSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"


class CurrentUserResponseSchema(BaseModel):
    id: int
    username: str
    full_name: str
    role_id: int
    status: str