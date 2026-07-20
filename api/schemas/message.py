from pydantic import BaseModel


class MessageIn(BaseModel):
    to_user_id: int
    content: str
