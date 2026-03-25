from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    is_admin: bool = False

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None

class MessageSchema(BaseModel):
    sender: str
    content: str
    timestamp: datetime

    class Config:
        from_attributes = True

class ChatSessionSchema(BaseModel):
    id: int
    title: str
    created_at: datetime
    messages: List[MessageSchema] = []

    class Config:
        from_attributes = True

class ChatRequest(BaseModel):
    session_id: Optional[int] = None
    message: str

class ProcessStatusBase(BaseModel):
    task_name: str
    status: str
    notes: Optional[str] = None

class ProcessStatusResponse(ProcessStatusBase):
    id: int
    updated_at: datetime

    class Config:
        from_attributes = True
