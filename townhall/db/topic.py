from sqlmodel import SQLModel, Field, Relationship
from typing import Optional

class Topic(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    topic_index: int
    keywords: str  # Could be a comma-separated string of keywords
    message_id: Optional[int] = Field(default=None, foreign_key="message.id")
    message: Optional["Message"] = Relationship(back_populates="topics")
