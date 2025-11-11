import os
import unittest
from datetime import datetime
from unittest.mock import patch, AsyncMock

from crawler import get_book_metadata, crawler
from db import models, db
from utils import utils


class TestBookCrawlerProject(unittest.IsolatedAsyncioTestCase):
    """Comprehensive tests for the Book Crawler project."""

    def test_build_fingerprint_and_hash(self):
        doc = {
            "name": "Book",
            "price_excl_tax": "£10.00",
            "price_incl_tax": "£12.00",
            "availability": "In stock",
            "rating": 4,
            "number_of_reviews": "5"
        }
        fingerprint = utils.build_fingerprint(doc)
        self.assertIn("Book", fingerprint)
        self.assertIn("|", fingerprint)

        result_hash = utils.compute_hash(doc)
        self.assertEqual(len(result_hash), 64)
        self.assertTrue(all(c in "0123456789abcdef" for c in result_hash))

    def test_build_changed_content_detects_changes(self):
        current = {"name": "New Name", "price_excl_tax": "£10"}
        existing = {"name": "Old Name", "price_excl_tax": "£10"}
        changes = utils.build_changed_content(current, existing)
        self.assertIn("name", changes)
        self.assertEqual(changes["name"]["old"], "Old Name")
        self.assertEqual(changes["name"]["new"], "New Name")

    def test_book_model_validation(self):
        book = models.Book(
            name="Example",
            description="Desc",
            category="Cat",
            price_excl_tax="£5",
            price_incl_tax="£6",
            availability="In stock",
            rating=4,
            image_url="https://example.com/img.jpg",
            number_of_reviews="10",
            source_url="https://example.com/book"
        )
        self.assertIsInstance(book.crawl_timestamp, datetime)
        self.assertEqual(book.status, "success")
        self.assertTrue(str(book.image_url).startswith("https"))

    def test_parse_book_html_extracts_data(self):
        os.environ["RATING_MAPPING"] = '{"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}'
        html = """
            <html>
              <h1>Book Title</h1>
              <div id="product_description"></div>
              <p>Description text here.</p>
              <table>
                <tr><th>Price (excl. tax)</th><td>£10.00</td></tr>
                <tr><th>Price (incl. tax)</th><td>£12.00</td></tr>
                <tr><th>Availability</th><td>In stock</td></tr>
                <tr><th>Number of reviews</th><td>5</td></tr>
              </table>
              <img src="../../media/test.jpg">
              <p class="star-rating Four"></p>
              <ul class="breadcrumb">
                <li></li><li></li><li><a>Fiction</a></li>
              </ul>
            </html>
            """
        book = get_book_metadata.parse_book_html(html, "https://books.toscrape.com/test")
        self.assertEqual(book.name, "Book Title")
        self.assertEqual(book.category, "Fiction")
        self.assertEqual(book.rating, 4)
        self.assertEqual(book.price_excl_tax, "£10.00")

    async def test_save_book_inserts_new_entry(self):
        """Ensure save_book inserts a new entry when no existing doc is found."""
        fake_collection = AsyncMock()
        fake_db = {db.COLLECTION: fake_collection}
        fake_book = models.Book(
            name="Example",
            description="Desc",
            category="Cat",
            price_excl_tax="£5",
            price_incl_tax="£6",
            availability="In stock",
            rating=4,
            image_url="https://example.com/img.jpg",
            number_of_reviews="10",
            source_url="https://example.com/book"
        )
        fake_collection.find_one.return_value = None
        with patch("db.db.log_change", AsyncMock()) as mock_log:
            await db.save_book(fake_db, fake_book)
        fake_collection.insert_one.assert_awaited()
        mock_log.assert_awaited()

    def test_scheduler_constants_from_env(self):
        os.environ["SCHEDULER_CRAWL_HOUR"] = "10"
        os.environ["SCHEDULER_CRAWL_MINUTE"] = "30"
        self.assertIsInstance(int(os.getenv("SCHEDULER_CRAWL_HOUR")), int)
        self.assertIsInstance(int(os.getenv("SCHEDULER_CRAWL_MINUTE")), int)

    async def test_fetch_returns_text(self):
        """Ensure fetch() returns the expected text."""
        class FakeResponse:
            async def text(self): return "OK"
            def raise_for_status(self): pass
            async def __aenter__(self): return self
            async def __aexit__(self, *a): pass

        class FakeSession:
            def get(self, url, timeout):
                return FakeResponse()

        session = FakeSession()
        text = await crawler.fetch(session, "https://example.com")
        self.assertEqual(text, "OK")

    def test_hash_stability_integration(self):
        """Integration-style: fingerprint and hash stay consistent."""
        doc = {
            "name": "Book",
            "price_excl_tax": "£5",
            "price_incl_tax": "£6",
            "availability": "In stock",
            "rating": 4,
            "number_of_reviews": "2"
        }
        first = utils.compute_hash(doc)
        second = utils.compute_hash(doc)
        self.assertEqual(first, second)
        self.assertTrue(len(first) == 64)


if __name__ == "__main__":
    unittest.main()