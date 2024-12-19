from pydantic import BaseModel


class UserConsultRequest(BaseModel):
    chat_user_id: int
    target_id: int
    concern: str


