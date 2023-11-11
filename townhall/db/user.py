from typing import Optional, List
from sqlmodel import Field, SQLModel,Relationship

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    discriminator: str
    avatar: str
    messages: List["Message"] = Relationship(back_populates="user")