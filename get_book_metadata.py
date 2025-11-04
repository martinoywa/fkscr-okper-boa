import requests
from bs4 import BeautifulSoup

from models import Book

BASE_URL = "https://books.toscrape.com/"
RATING_MAPPING = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5,}

def get_book_metadata(book_url):
    request = requests.get(book_url)
    soup = BeautifulSoup(request.content, "html.parser")

    name = soup.find("h1").get_text(strip=True)

    desc_header = soup.find("div", id="product_description")
    description = desc_header.find_next_sibling("p").get_text(strip=True) if desc_header else "No description"

    category = soup.find("tr", text="Product Type")
    if not category:
        category = "Books"
    else:
        category = category.find_next("td").get_text(strip=True)

    price_excl = soup.find("th", string="Price (excl. tax)").find_next("td").get_text(strip=True)
    price_incl = soup.find("th", string="Price (incl. tax)").find_next("td").get_text(strip=True)

    availability = soup.find("th", string="Availability").find_next("td").get_text(strip=True)

    reviews = soup.find("th", string="Number of reviews").find_next("td").get_text(strip=True)

    image_url = soup.find("img")["src"].replace("../../", BASE_URL)

    rating_class = soup.find("p", class_="star-rating")["class"]
    rating = rating_class[1] if len(rating_class) > 1 else "No rating"

    data = {
        "Name": name,
        "Description": description,
        "Category": category,
        "Price (excl. tax)": price_excl,
        "Price (incl. tax)": price_incl,
        "Availability": availability,
        "Number of reviews": reviews,
        "Image URL": image_url,
        "Rating": rating,

    }

    return Book(
        name=name,
        description=description,
        category=category,
        price_excl_tax=price_excl,
        price_incl_tax=price_incl,
        availability=availability,
        rating=RATING_MAPPING.get(rating, 0),
        image_url=image_url,
        number_of_reviews=reviews,
        raw_html=request.content,
    )