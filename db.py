import logging
from datetime import datetime

import motor.motor_asyncio

from models import Book


# TODO use dotenv
MONGO_URI = "mongodb://localhost:27017"
COLLECTION = "books"
DB_NAME = "bookstore"
PROGRESS_COLLECTION = "crawler_progress"
CRAWLER_NAME = "books_scraper"

CLIENT = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
DB = CLIENT[DB_NAME]

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

async def save_book(db, book: Book):
    """Save book data, avoiding duplicates."""
    # Convert Pydantic model into a Mongo-friendly.
    # Ensures all special types (HttpUrl, datetime, Decimal, etc.) are serialized to JSON-safe primitives (strings, numbers)
    doc = book.model_dump(mode="json")

    await db[COLLECTION].update_one(
        {"source_url": str(doc["source_url"])},
        {"$set": doc},
        upsert=True,
    )


async def get_last_page(db):
    """Read last crawled page number from MongoDB."""
    progress = await db[PROGRESS_COLLECTION].find_one({"_id": CRAWLER_NAME})
    if progress:
        logging.info(f"Resuming from page {progress['last_page']}...")
        return progress["last_page"]
    logging.info("Starting fresh crawl from page 1...")
    return 1


async def save_progress(db, page_number):
    """Save the last successfully crawled page number to MongoDB."""
    # TODO how to automatically check if the last page has been reached.
    # TODO The Request of page fails so it kinda behaves like a missing book link?
    await db[PROGRESS_COLLECTION].update_one(
        {"_id": CRAWLER_NAME},
        {
            "$set": {
                "last_page": page_number,
                "updated_at": datetime.utcnow(),
            }
        },
        upsert=True,
    )
