import json
import os
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from models import Book


load_dotenv()

RATING_MAPPING = json.loads(os.getenv("RATING_MAPPING"))


def parse_book_html(html: str, url: str) -> Book:
    soup = BeautifulSoup(html, "html.parser")

    name = soup.find("h1").get_text(strip=True)

    desc_header = soup.find("div", id="product_description")
    description = desc_header.find_next_sibling("p").get_text(strip=True) if desc_header else "No description"

    category_tag = soup.select_one(".breadcrumb li:nth-of-type(3) a")
    category = category_tag.text.strip() if category_tag else "Books"

    price_excl = soup.find("th", string="Price (excl. tax)").find_next("td").get_text(strip=True)
    price_incl = soup.find("th", string="Price (incl. tax)").find_next("td").get_text(strip=True)
    availability = soup.find("th", string="Availability").find_next("td").get_text(strip=True)
    reviews = soup.find("th", string="Number of reviews").find_next("td").get_text(strip=True)

    image_url = soup.find("img")["src"].replace("../../", "https://books.toscrape.com/")

    rating_class = soup.find("p", class_="star-rating")["class"]
    rating = RATING_MAPPING.get(rating_class[1], 0) if len(rating_class) > 1 else 0


    return Book(
        name=name,
        description=description,
        category=category,
        price_excl_tax=price_excl,
        price_incl_tax=price_incl,
        availability=availability,
        number_of_reviews=reviews,
        image_url=image_url,
        rating=rating,
        source_url=url,
        raw_html=html,
        crawl_timestamp=datetime.utcnow(),
    )