from sqlmodel import SQLModel, Field, Relationship
from typing import Optional

class Topic(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    keywords: str  # Could be a comma-separated string of keywords
