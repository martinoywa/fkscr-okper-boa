# Book Craweler and API
### Project Description
1. A scalable and fault-tolerant web crawler.
2. Has change detection mechanism to maintain up-to-date records.
3. RESTful API with authentication and filtering capabilities.
4. Logging eneabled across the system. Check `logs/crawler.log` once project is running.

### Directory Structure
```bash
root
.
├── api
│   ├── __init__.py
│   ├── api.py
│   ├── models.py
│   └── utils.py
├── crawler
│   ├── __init__.py
│   ├── crawler.py
│   └── get_book_metadata.py
├── db
│   ├── __init__.py
│   ├── db.py
│   └── models.py
├── logs # Excluded
│   └── crawler.log
├── reports # Excluded
│   └── change_report_2025-11-11.csv
├── requirements.txt
├── scheduler
│   ├── __init__.py
│   └── scheduler.py
├── tests
│   ├── __init__.py
│   └── test_crawler.py
└── utils
    ├── __init__.py
    └── utils.py
```

### How to Run (Project Setup)
1. Clone repository.
2. Create and activate `Python 3.10.19` virtual environment.
```bash
$ python -m venv env
$ source env/bin/activate
```
2. Install dependencies.
```bash
$ pip install -r requirements.txt
```
3. Update the `.env` file. You may need to change the lines below.
```
MONGO_URI=mongodb://localhost:27017
API_KEY=f0493rujfifodusf8034jsadof823
```
4. Run tests.
```bash
$ pytest -v
```
5. Start the crawler scheduler. This is the main entry point to the crawler. 
Set `generate-report=True` with `report-formet=csv|json` if you want a daily report. The report date is automatically selected.
```bash
$ python scheduler/scheduler.py --generate-report True --report-format csv 
```
The scheduler configs are in the `.env` file as.
```
# Runs every day at 12:40 server time
SCHEDULER_CRAWL_HOUR=12
SCHEDULER_CRAWL_MINUTE=40
```
6. Run the API.
```
$ fastapi run api/api.py --reload
```

### How to Run (Swagger UI for API testing)
1. Swagger UI URL. `http://127.0.0.1:8000/docs`
2. Swagger UI Authentication.
```
- Click the Authorize Button at the top.
- Enter your API key. Check .env file.
- Click the Close Button. You can now use the API Endpoints.
```
3. API Endpoint Specifications.

| Method | Endpoint | Description | Query Parameters | Response | Status Codes |
|:-------|:----------|:-------------|:------------------|:-----------|:--------------|
| **GET** | `/books` | Retrieve a paginated list of books with optional filters and sorting. | - `category`: filter by category<br>- `min_price`, `max_price`: filter by price range<br>- `rating`: filter by numeric rating (1–5)<br>- `sort_by`: one of `"rating"`, `"price"`, or `"reviews"`<br>- `page`: page number (default 1)<br>- `page_size`: items per page (default 10) | **BookListResponse**<br>`{ total: int, page: int, page_size: int, items: List[Book] }` | 200 OK<br>400 Invalid query params<br>401 Unauthorized<br>429 Rate limit exceeded |
| **GET** | `/books/{book_id}` | Retrieve full details of a specific book by its Mongo `_id`. | None | **Book** object | 200 OK<br>404 Not found<br>401 Unauthorized |
| **GET** | `/changes` | Retrieve recent changes from `CHANGELOG_COLLECTION`. | - `limit`: max number of entries<br>- `since_hours`: how far back to look (e.g., last 24 hours) | **ChangeListResponse**<br>`{ items: List[ChangeEntry] }` | 200 OK<br>401 Unauthorized<br>429 Rate limit exceeded |


### Miscellaneous
1. Successfule Crawls + Scheduled Runs.
```
2025-11-11 14:02:27,683 [INFO] apscheduler.scheduler: Adding job tentatively -- it will be properly scheduled when the scheduler starts
2025-11-11 14:02:27,684 [INFO] apscheduler.scheduler: Added job "run_crawl" to job store "default"
2025-11-11 14:02:27,684 [INFO] apscheduler.scheduler: Scheduler started
2025-11-11 14:02:27,684 [INFO] book_scraper: Scheduler started. Waiting for jobs...
2025-11-11 14:03:00,001 [INFO] apscheduler.executors.default: Running job "run_crawl (trigger: cron[hour='14', minute='3'], next run at: 2025-11-12 14:03:00 EAT)" (scheduled at 2025-11-11 14:03:00+03:00)
2025-11-11 14:03:00,002 [INFO] book_scraper: Starting scheduled crawl...
2025-11-11 14:03:00,027 [INFO] book_scraper: Resuming from page 1...
2025-11-11 14:03:00,027 [INFO] book_scraper: Crawling https://books.toscrape.com/catalogue/page-1.html
2025-11-11 14:03:01,585 [INFO] book_scraper: No changes for book: A Light in the Attic
...
2025-11-11 14:03:50,615 [INFO] book_scraper: No next page found at https://books.toscrape.com/catalogue/page-51.html. Resetting progress to 1.
2025-11-11 14:03:50,618 [INFO] book_scraper: Scheduled crawl finished.
2025-11-11 14:03:50,618 [INFO] book_scraper: Generating daily change report for 2025-11-11...
2025-11-11 14:03:50,645 [INFO] book_scraper: Change report saved to: change_report_2025-11-11.csv
2025-11-11 14:03:50,645 [INFO] book_scraper: Daily change report generated successfully.
2025-11-11 14:03:50,645 [INFO] apscheduler.executors.default: Job "run_crawl (trigger: cron[hour='14', minute='3'], next run at: 2025-11-12 14:03:00 EAT)" executed successfully
```
2. MongoDB Sample Document Structures.
- Books
```
[
  {
    "_id": {"$oid": "6912f24a4a95f9000b05c101"},
    "availability": "In stock (22 available)",
    "category": "Poetry",
    "content_hash": "9a79f17bdd4ea7f34c5627590b58f9436088b5720eb2cfc65ce6e608eb1ea395",
    "crawl_timestamp": "2025-11-11T08:22:34.745708",
    "created_at": {"$date": "2025-11-11T08:22:34.754Z"},
    "description": "It's hard to imagine a world without A Light in the Attic. This now-classic collection of poetry and drawings from Shel Silverstein celebrates its 20th anniversary with this special edition. Silverstein's humorous and creative verse can amuse the dowdiest of readers. Lemon-faced adults and fidgety kids sit still and read these rhythmic words and laugh and smile and love th It's hard to imagine a world without A Light in the Attic. This now-classic collection of poetry and drawings from Shel Silverstein celebrates its 20th anniversary with this special edition. Silverstein's humorous and creative verse can amuse the dowdiest of readers. Lemon-faced adults and fidgety kids sit still and read these rhythmic words and laugh and smile and love that Silverstein. Need proof of his genius? RockabyeRockabye baby, in the treetopDon't you know a treetopIs no safe place to rock?And who put you up there,And your cradle, too?Baby, I think someone down here'sGot it in for you. Shel, you never sounded so good. ...more",
    "image_url": "https://books.toscrape.com/media/cache/fe/72/fe72f0532301ec28892ae79a629a293c.jpg",
    "name": "A Light in the Attic",
    "number_of_reviews": "0",
    "price_excl_tax": "£51.77",
    "price_incl_tax": "£51.77",
    "rating": 3,
    "raw_html": "\n\n<!DOCTYPE html>\n<!--[if lt IE 7]> ...",
    "source_url": "https://books.toscrape.com//catalogue/a-light-in-the-attic_1000/index.html",
    "status": "success",
    "updated_at": {"$date": "2025-11-11T08:22:34.754Z"}
  }
]
```

- Crawler Progress. Supports Resuming.
```
[
  {
    "_id": "books_scraper",
    "last_page": 1,
    "updated_at": {"$date": "2025-11-11T11:03:50.612Z"}
  }
]
```

- Books Changelog.
```
[
  {
    "_id": {"$oid": "6912f24a4a95f9000b05c102"},
    "book_name": "A Light in the Attic",
    "book_url": "https://books.toscrape.com//catalogue/a-light-in-the-attic_1000/index.html",
    "change_type": "new",
    "changed_at": {"$date": "2025-11-11T08:22:34.791Z"},
    "changes": "{}"
  }
]
```


---
**GGs!** 🏁  
_If you made it this far, you deserve a coffee ☕._