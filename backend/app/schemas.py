from pydantic import BaseModel
from typing import Optional

class SubjectBase(BaseModel):
    name: str
    totalHours: int

class SubjectCreate(SubjectBase):
    pass

class Subject(SubjectBase):
    id: int
    skipped: int
    last_skipped: Optional[int] = None

    class Config:
        from_attributes = True

class ChatMessage(BaseModel):
    message: str
    file_base64: Optional[str] = None
    file_type: Optional[str] = None
