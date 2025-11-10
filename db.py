import motor.motor_asyncio

from models import Book


# TODO use dotenv
MONGO_URI = "mongodb://localhost:27017"
COLLECTION = "books"
DB_NAME = "bookstore"

CLIENT = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
DB = CLIENT[DB_NAME]


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
