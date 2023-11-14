from sqlmodel import SQLModel, Field, Relationship
from typing import Optional

class Opinion(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    sentiment_score: float
    message_id: int = Field(foreign_key="message.id")
    message: Optional["Message"] = Relationship(back_populates="opinions")
