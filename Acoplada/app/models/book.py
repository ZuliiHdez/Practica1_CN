from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid

class BookBase(BaseModel):
    title: str = Field(..., example="El nombre del viento")
    author: str = Field(..., example="Patrick Rothfuss")
    genre: Optional[str] = Field(None, example="Fantasía")
    year: Optional[int] = Field(None, ge=0, example=2007)
    status: Optional[str] = Field(
        "available",
        pattern="^(available|borrowed|reserved|lost)$",
        example="available"
    )
    rating: Optional[str] = Field(
        "medium",
        pattern="^(low|medium|high|excellent)$",
        example="excellent"
    )
    tags: Optional[List[str]] = Field(default_factory=list, example=["fantasía", "aventura"])

class BookCreate(BookBase):
    pass

class BookUpdate(BookBase):
    title: Optional[str] = None
    author: Optional[str] = None

class Book(BookBase):
    book_id: str = Field(default_factory=lambda: str(uuid.uuid4()), example="550e8400-e29b-41d4-a716-446655440000")
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

    class Config:
        orm_mode = True