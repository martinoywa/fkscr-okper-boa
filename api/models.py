from datetime import datetime
from typing import List, Literal

from pydantic import BaseModel

from db.models import Book


class BookListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[Book]


class ChangeEntry(BaseModel):
    book_url: str
    book_name: str
    change_type: Literal["new", "update", "new_book", "price_change"]
    changes: dict
    changed_at: datetime | str  # validate from Mongo


class ChangeListResponse(BaseModel):
    total: int
    items: List[ChangeEntry]