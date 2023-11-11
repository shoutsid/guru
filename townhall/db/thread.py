from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship

class Thread(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    messages: List["Message"] = Relationship(back_populates="thread")