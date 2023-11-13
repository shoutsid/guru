from datetime import datetime
from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship

class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    thread: Optional["Thread"] = Relationship(back_populates="messages")
    thread_id: Optional[int] = Field(default=None, foreign_key="thread.id")
    user: Optional["User"] = Relationship(back_populates="messages")
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    content: str
    role: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    entities: List["Entity"] = Relationship(back_populates="message")
    emotions: List["Emotion"] = Relationship(back_populates="message")
    opinions: List["Opinion"] = Relationship(back_populates="message")
    topics: List["Topic"] = Relationship(back_populates="message")

class MessageResponse:
    id: int
    thread_id: int
    user_id: int
    content: str
    role: str
