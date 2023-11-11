from typing import Optional
from sqlmodel import Field, SQLModel,Relationship

class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    thread: Optional["Thread"] = Relationship(back_populates="messages")
    thread_id: Optional[int] = Field(default=None, foreign_key="thread.id")
    user: Optional["User"] = Relationship(back_populates="messages")
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    content: str
    role: str

class MessageResponse:
    id: int
    thread_id: int
    user_id: int
    content: str
    role: str
