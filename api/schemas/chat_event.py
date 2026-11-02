from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator


class BaseEvent(BaseModel):
    """Входящее WS-событие. Все поля кроме to_user_id сохраняются в Mongo как есть."""
    to_user_id: int

    def preview(self) -> str:
        """Текст для last_message в списке чатов."""
        raise NotImplementedError


class BaseEventResponse(BaseModel):
    # из Mongo приходит _id/sender_id, а FastAPI при проверке response_model валидирует уже по именам полей
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)
    id_: str = Field(validation_alias="_id")
    chat_id: int
    created_at: datetime

    @field_validator("id_", mode="before")
    @classmethod
    def object_id_to_str(cls, value):
        return str(value)
