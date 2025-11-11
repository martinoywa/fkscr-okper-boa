import os
import time
from collections import defaultdict

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader


load_dotenv()

API_KEY = os.getenv("API_KEY")
API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)
API_RATE_LIMIT = float(os.getenv("API_RATE_LIMIT"))
API_RATE_LIMIT_WINDOW_SECONDS = float(os.getenv("API_RATE_LIMIT_WINDOW_SECONDS"))


async def get_api_key(api_key_header: str = Depends(API_KEY_HEADER)) -> str:
    """API key-based authentication."""
    if api_key_header is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key",
        )
    if api_key_header != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
    return api_key_header


# List of request timestamps (float)
request_log = defaultdict(list)
async def rate_limiter(api_key=Depends(get_api_key)):
    """In-memory rate limiter."""
    now = time.time()
    window_start = now - API_RATE_LIMIT_WINDOW_SECONDS

    timestamps = request_log[api_key]

    # Drop timestamps older than current window
    while timestamps and timestamps[0] < window_start:
        timestamps.pop(0)

    if len(timestamps) >= API_RATE_LIMIT:
        # Too many requests in the last hour
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Max 100 requests per hour.",
        )

    timestamps.append(now)


def parse_price(price_str: str) -> float:
    """Convert '£10.00' -> 10.0. Fallback to 0.0 on any error."""
    if not price_str:
        return 0.0
    # Remove currency symbol and commas
    cleaned = price_str.replace("£", "").replace(",", "").strip()
    try:
        return float(cleaned)
    except ValueError:
        return 0.0
