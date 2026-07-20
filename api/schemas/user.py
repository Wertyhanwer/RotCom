from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    login: str
    email: EmailStr
    password: str

class UserUpdateUsername(BaseModel):
    username: str

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id_: int
    username: str
    login: str
    email: str
    created_at: datetime