# Book Craweler and API
### Project Description
1. A scalable and fault-tolerant web crawling.
2. Has change detection mechanism to maintain up-to-date records.
3. RESTful API with authentication and filtering capabilities.

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

### How to Run
1. Clone repository.
2. Create and activate `Python 3.10.19` virtual environment.
```bash
$ python -m venv env
$ source env/bin/activate
```
2. Install dependecies
```bash
$ pip install -r requirements.txt
```
3. Update the `.env` file. You may need to change the lines below.
```
MONGO_URI=mongodb://localhost:27017
API_KEY=f0493rujfifodusf8034jsadof823
```
4. Run tests
```bash
$ pytest -v
```
5. Start the scheduler. This is the main entry point to the crawler. 
Set `generate-report=True` with `report-formet=csv|json` if you want a daily report. The report date is automatically selected.
```bash
$ python scheduler/scheduler.py --generate-report True --report-format csv 
```
The scheduler configs are in the `.env` file as.
```
# Run every day at 12:40 server time
SCHEDULER_CRAWL_HOUR=12
SCHEDULER_CRAWL_MINUTE=40
```
6. 
