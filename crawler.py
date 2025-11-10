import asyncio
import logging

import aiohttp
from aiohttp import ClientSession

import requests
from bs4 import BeautifulSoup

from db import save_book, DB
from get_book_metadata import parse_book_html

# TODO use dotenv
BASE_URL = "https://books.toscrape.com/"
MAX_RETRIES = 3

# page = requests.get(BASE_URL)
# print(page.text)

# soup = BeautifulSoup(page.content, "html.parser")
# books = soup.find_all("article", class_="product_pod")

# for book in books:
#     book_url = BASE_URL+book.find("a")["href"]
#     data = get_book_metadata(book_url)
#     print(data)
#     break

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


async def fetch(session: ClientSession, url: str, retries=MAX_RETRIES) -> str:
    """Fetches a URL with retry logic."""
    for attempt in range(1, retries + 1):
        try:
            async with session.get(url, timeout=15) as response:
                response.raise_for_status()
                return await response.text()
        except Exception as e:
            logging.warning(f"Attempt {attempt} failed for {url}: {e}")
            if attempt == retries:
                raise
            await asyncio.sleep(2 * attempt)  # backoff


async def get_book_links(session, page_html):
    """Extracts all book URLs from a page."""
    soup = BeautifulSoup(page_html, "html.parser")
    books = soup.select("article.product_pod h3 a")
    return [BASE_URL + b["href"] for b in books]


async def process_book(session, db, book_url):
    """Fetch and parse a single book, then save it."""
    try:
        html = await fetch(session, book_url)
        book = parse_book_html(html, book_url)
        # logging.info(f"Found book {book.name}")
        await save_book(db, book)
        logging.info(f"Saved: {book.name}")
    except Exception as e:
        logging.error(f"Error processing {book_url}: {e}")


async def crawl_page(session, db, page_number):
    """Crawl a single page of book listings."""
    # paginated_url = BASE_URL+f"catalogue/page-{page_number}.html"
    url = BASE_URL.format(page_number)
    logging.info(f"Crawling {url}")
    try:
        page_html = await fetch(session, url)
    except Exception as e:
        logging.error(f"Failed to crawl {url}: {e}")
        return False

    book_links = await get_book_links(session, page_html)
    if not book_links:
        logging.info(f"No books found on {url}. Stopping pagination.")
        return False
    # logging.info(f"Found {len(book_links)}. "
    #              f"First and last books: {book_links[0]} and {book_links[-1]}")

    tasks = []
    for link in book_links:
        tasks.append(process_book(session, db, link))
    await asyncio.gather(*tasks)
    return True

"""
TODO: Check if a new book has been added.
Use the book titles list fetched in DB against new fetch. i.e set difference.
Then search by diff title and add new books to DB.
"""

async def main():
    async with aiohttp.ClientSession() as session:
        page = 1
        while True:
            success = await crawl_page(session, DB, page)
            if not success:
                break
            page += 1
            break
        logging.info("Crawling finished!")

if __name__ == "__main__":
    asyncio.run(main())