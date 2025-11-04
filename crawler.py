import requests
from bs4 import BeautifulSoup

from get_book_metadata import get_book_metadata

BASE_URL = "https://books.toscrape.com/"
page = requests.get(BASE_URL)
# print(page.text)

soup = BeautifulSoup(page.content, "html.parser")
books = soup.find_all("article", class_="product_pod")

for book in books:
    book_url = BASE_URL+book.find("a")["href"]
    data = get_book_metadata(book_url)
    print(data)
    break


"""
TODO: Check if a new book has been added.
Use the book titles list fetched in DB against new fetch. i.e set difference.
Then search by diff title and add new books to DB.
"""
