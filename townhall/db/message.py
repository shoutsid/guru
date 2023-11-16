from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel

class Message(SQLModel, table=True):
    __tablename__ = "open_ai_messages"
    id: Optional[int] = Field(default=None, primary_key=True)
    content: str
    role: str
    thread_id: Optional[int] = Field(default=None, foreign_key="open_ai_threads.id")
    created_at: datetime = Field(default=datetime.now())
    updated_at: datetime = Field(default=datetime.now())