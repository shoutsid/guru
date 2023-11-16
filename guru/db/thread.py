from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel

class Thread(SQLModel, table=True):
    __tablename__ = "open_ai_threads"
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default=datetime.now())
    updated_at: datetime = Field(default=datetime.now())
    discord: bool = Field(default=False)