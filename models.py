from typing import Optional

from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime


class Book(BaseModel):
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    price_excl_tax: str
    price_incl_tax: str
    availability: Optional[str] = None
    number_of_reviews: Optional[int] = None
    image_url: Optional[HttpUrl] = None
    rating: Optional[int] = None
    crawl_timestamp: datetime = Field(default_factory=datetime.utcnow)
    crawl_status: str = "success"  # success | failed
    raw_html: Optional[str] = None
