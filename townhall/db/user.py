from datetime import datetime
from typing import Optional, List
from sqlmodel import Field, SQLModel,Relationship

class User(SQLModel, table=True):
    __tablename__ = "users"
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    discriminator: str
    avatar: str
    created_at: datetime = Field(default=datetime.now())
    updated_at: datetime = Field(default=datetime.now())