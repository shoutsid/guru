from sqlmodel import SQLModel, Field, Relationship
from typing import Optional

class Entity(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    text: str
    label: str
    # message_id: Optional[int] = Field(default=None, foreign_key="message.id")
    # message: Optional["Message"] = Relationship(back_populates="entities")
