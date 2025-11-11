import os
from datetime import datetime, timedelta

import motor.motor_asyncio
from dotenv import load_dotenv

from models import Book
from utils import compute_hash, build_changed_content, logger

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")
COLLECTION = os.getenv("COLLECTION")
PROGRESS_COLLECTION = os.getenv("PROGRESS_COLLECTION")
CHANGELOG_COLLECTION = os.getenv("CHANGELOG_COLLECTION")
CRAWLER_NAME = os.getenv("CRAWLER_NAME")


CLIENT = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
DB = CLIENT[DB_NAME]


async def save_book(db, book: Book):
    """
    Save book data, avoiding duplicates.
    - New book  -> insert + log "new"
    - Existing, same content_hash -> do nothing
    - Existing, different content_hash -> update + log "update"
    """
    # Convert Pydantic model into a Mongo-friendly.
    # Ensures all special types (HttpUrl, datetime, Decimal, etc.) are serialized to JSON-safe primitives (strings, numbers)
    doc = book.model_dump(mode="json")

    # Compute hash and append to content
    content_hash = compute_hash(doc)
    doc["content_hash"] = content_hash

    # Query the db by trying to fetch data
    collection = db[COLLECTION]
    existing = await collection.find_one({"source_url": str(doc["source_url"])})
    now = datetime.utcnow()

    if not existing: # New book
        doc["created_at"] = now
        doc["updated_at"] = now
        await collection.insert_one(doc)
        await log_change(db, doc, "new", {})
        logger.info(f"Saved new book: {doc['name']}")
        return

    # Skip if nothing changed
    if existing.get("content_hash") == content_hash:
        logger.info(f"No changes for book: {doc['name']}")
        return

    # Detect and log changes otherwise.
    doc["updated_at"] = now
    changed_content = build_changed_content(doc, existing)

    await collection.update_one(
        {"_id": existing["_id"]},
        {"$set": doc},
        upsert=True,
    )
    await log_change(db, doc, "update", changed_content)
    logger.info(f"Updated book: {doc['name']}")


async def get_last_page(db):
    """Read last crawled page number from MongoDB."""
    progress = await db[PROGRESS_COLLECTION].find_one({"_id": CRAWLER_NAME})
    if progress:
        logger.info(f"Resuming from page {progress['last_page']}...")
        return progress["last_page"]
    logger.info("Starting fresh crawl from page 1...")
    return 1


async def save_progress(db, page_number):
    """Save the last successfully crawled page number to MongoDB."""
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


async def log_change(db, book_doc, change_type, changes):
    """
    Insert a row in the change-log collection.

    change_type: "new" or "update"
    changes: {field_name: {"old": old_val, "new": new_val}}
    """
    payload = {
        "book_url": str(book_doc.get("source_url")),
        "book_name": book_doc.get("name"),
        "change_type": change_type,
        "changes": changes,
        "changed_at": datetime.utcnow(),
    }
    await db[CHANGELOG_COLLECTION].insert_one(payload)

    # Alerting line to the log.
    logger.info(
        f"[CHANGE] {change_type.upper()} for '{payload['book_name']}' "
        f"{payload['book_url']} -> {changes}"
    )


async def fetch_changes_for_day(target_date: datetime):
    """Fetch all change log entries for the given date (UTC) from MongoDB."""
    start = datetime(target_date.year, target_date.month, target_date.day)
    end = start + timedelta(days=1)

    cursor = DB[CHANGELOG_COLLECTION].find({
        "changed_at": {"$gte": start, "$lt": end}
    })

    results = await cursor.to_list(length=None)

    return results
