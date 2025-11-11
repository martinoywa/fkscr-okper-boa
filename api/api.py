from datetime import datetime, timedelta
from typing import List, Optional, Literal

from bson import ObjectId
from fastapi import FastAPI, Depends, HTTPException, Query, status

from api.models import BookListResponse, ChangeListResponse, ChangeEntry
from api.utils import rate_limiter, parse_price
from db.db import DB, COLLECTION, CHANGELOG_COLLECTION
from db.models import Book

app = FastAPI(
    title="Book Scraper API",
    description="RESTful API over scraped books and change logs.",
    version="1.0.0",
)


@app.get(
    "/books",
    response_model=BookListResponse,
    dependencies=[Depends(rate_limiter)],
    summary="List books with filters and pagination",
)
async def list_books(
    category=Query(None, description="Filter by category"),
    min_price=Query(None, ge=0, description="Minimum price (incl. tax)"),
    max_price=Query(None, ge=0, description="Maximum price (incl. tax)"),
    rating=Query(None, ge=0, le=5, description="Minimum rating"),
    sort_by: Optional[Literal["rating", "price", "reviews"]]=Query(
        "rating", description="Sort by rating, price, or reviews"
    ),
    page=Query(1, ge=1),
    page_size=Query(20, ge=1, le=100),
):
    db = DB
    filters: dict = {}

    if category:
        filters["category"] = category
    if rating is not None:
        filters["rating"] = {"$gte": rating}

    # Count total before pagination
    total = await db[COLLECTION].count_documents(filters)

    # Sorting
    sort_field = {
        "rating": "rating",
        "price": "price_incl_tax",
        "reviews": "number_of_reviews",
    }.get(sort_by or "rating", "rating")

    cursor = (
        db[COLLECTION]
        .find(filters)
        .sort(sort_field, 1)
        .skip((page - 1) * page_size)
        .limit(page_size)
    )
    docs = await cursor.to_list(length=page_size)

    # Checks since prices are stored as strings
    filtered_docs = []
    for doc in docs:
        price_val = parse_price(doc.get("price_incl_tax", "0"))
        if min_price is not None and price_val < min_price:
            continue
        if max_price is not None and price_val > max_price:
            continue
        filtered_docs.append(doc)

    # Map to Book model
    books = [Book(**d) for d in filtered_docs]

    return BookListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=books,
    )


@app.get(
    "/books/{book_id}",
    response_model=Book,
    dependencies=[Depends(rate_limiter)],
    summary="Get full details about a specific book",
)
async def get_book(book_id: str):
    db = DB
    try:
        oid = ObjectId(book_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid book_id",
        )

    doc = await db[COLLECTION].find_one({"_id": oid})
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found",
        )

    return Book(**doc)


@app.get(
    "/changes",
    response_model=ChangeListResponse,
    dependencies=[Depends(rate_limiter)],
    summary="View recent book updates and new books",
)
async def get_changes(
    limit: int = Query(50, ge=1, le=200, description="Max number of change entries"),
    since_hours: int = Query(
        24,
        ge=1,
        le=24 * 7,
        description="How far back to look (in hours)",
    ),
):
    db = DB
    now = datetime.utcnow()
    since = now - timedelta(hours=since_hours)

    cursor = (
        db[CHANGELOG_COLLECTION]
        .find({"changed_at": {"$gte": since}})
        .sort("changed_at", -1)
        .limit(limit)
    )
    docs = await cursor.to_list(length=limit)

    changes: List[ChangeEntry] = []
    for doc in docs:
        doc = dict(doc)
        doc.pop("_id", None)
        changes.append(ChangeEntry(**doc))

    return ChangeListResponse(
        total=len(changes),
        items=changes,
    )
