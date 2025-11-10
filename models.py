# models.py
from pydantic import BaseModel, HttpUrl, Field
from typing import Optional
from datetime import datetime


class Book(BaseModel):
    name: str
    description: str
    category: str
    price_excl_tax: str
    price_incl_tax: str
    availability: str
    rating: int
    image_url: HttpUrl
    number_of_reviews: str
    source_url: HttpUrl
    raw_html: Optional[str] = None
    crawl_timestamp: datetime = Field(default_factory=datetime.utcnow)
    status: str = "success"

    class Config:
        from_attributes = True
