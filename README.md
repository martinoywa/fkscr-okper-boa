# Book Craweler and API
### Project Description
1. A scalable and fault-tolerant web crawling.
2. Has change detection mechanism to maintain up-to-date records.
3. RESTful API with authentication and filtering capabilities.
4. Logging is eneabled across the system. Check `logs/crawler.log` once project is running.

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


3. 
