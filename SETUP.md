# Project Setup Guide

## Prerequisites

Make sure you have the following installed before starting:

- **Python 3.11+**
- **Docker Desktop** (running)
- **Git**

---

## First-Time Setup

Follow these steps once when you first clone the project.

### 1. Clone the repository

```bash
git clone https://github.com/lazarevskaana/hubby-recommender.git
cd hubby-recommender
```

### 2. Create and activate the virtual environment

```bash
python3 -m venv venv
source venv/bin/activate         # macOS / Linux
# venv\Scripts\activate          # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env             # macOS / Linux
# copy .env.example .env         # Windows
```

Open `.env` and confirm the database credentials match the local Docker setup.

### 5. Start the database

```bash
docker compose up -d
```

Verify it's running:

```bash
docker ps
```

You should see `hubby_postgres` in the list with status "Up".

### 6. Initialize the database schema

```bash
python drop_and_recreate_tables.py
```

Type `yes` when prompted. This creates the `users` and `activities` tables.

### 7. Populate the database (Week 3 pipeline)

Run these scripts in order:

```bash
python preprocess_activities_tsv.py    # cleans the raw TSV → CSV
python insert_activities.py            # loads activities into PostgreSQL
python generate_dummy_users.py         # generates ~70 dummy users
python insert_users.py                 # loads users into PostgreSQL
python verify_data.py                  # sanity checks
```

After this you should have ~153 activities and ~70 users in the database.

---

## Daily Workflow

Every time you open the project, run these commands:

```bash
# 1. Activate the virtual environment
source venv/bin/activate         # macOS / Linux
# venv\Scripts\activate          # Windows

# 2. Pull latest changes from the team
git pull

# 3. Install any new dependencies
pip install -r requirements.txt

# 4. Start the database (if not already running)
docker compose up -d

# 5. Start the API server
uvicorn app.main:app --reload
```

The API will be available at: **http://localhost:8000**  
Interactive docs (Swagger UI): **http://localhost:8000/docs**

---

## Stopping the Project

```bash
# Stop the API server
Ctrl + C

# Stop the database container (data is preserved)
docker compose down
```

To also delete the database volume (full wipe):

```bash
docker compose down -v
```

Only do this if you want to start completely fresh.

---

## Resetting the Database

If the schema changes (`app/models.py` is modified) or you want to start with clean data:

```bash
python drop_and_recreate_tables.py
```

This drops all tables and recreates them with the latest schema. You'll need to re-run the data population scripts afterwards (preprocess → insert activities → generate users → insert users).

---

## Connecting via DBeaver (Optional)

For visual database inspection, connect DBeaver with these settings:

| Field | Value |
|---|---|
| Host | `localhost` |
| Port | `5432` |
| Database | `hubby_db` |
| Username | `hubby` |
| Password | `hubby_dev_password` |

---

## Common Issues

### Port 5432 already in use

Something else is running on port 5432 — usually a local PostgreSQL installation.

**macOS (Homebrew PostgreSQL):**
```bash
brew services stop postgresql
```

**Windows:** Open Services (Win+R → `services.msc`), find any PostgreSQL service, right-click → Stop.

Alternatively, change the port in `docker-compose.yml` from `"5432:5432"` to `"5433:5432"` and update `DATABASE_URL` in `.env` to use port 5433.

### Virtual environment not activated

If you see `ModuleNotFoundError` or `command not found: uvicorn`, you forgot to activate the venv:

```bash
source venv/bin/activate
```

### Docker container not starting

Most common cause: Docker Desktop isn't running. Open the Docker Desktop app and wait for the whale icon to appear in your menu bar/system tray.

If still failing, check the container logs:

```bash
docker compose logs
```

### `python` vs `python3`

On macOS/Linux, use `python3`. On Windows, use `python`.

### GitHub authentication fails

If `git push` returns a 403 error, you may be authenticated as the wrong GitHub account. Switch with:

```bash
gh auth switch
```

---

## Project Structure

```
hubby-recommender/
├── app/
│   ├── __init__.py
│   ├── main.py                          # FastAPI application
│   ├── database.py                      # SQLAlchemy connection setup
│   └── models.py                        # User and Activity models
├── data/
│   ├── unique_activities.tsv            # raw Google Places data (committed)
│   ├── cleaned_activities.csv           # output of preprocessing (gitignored)
│   └── dummy_users.csv                  # output of user generation (gitignored)
├── .env.example                         # environment variable template
├── .env                                 # local config (gitignored)
├── .gitignore
├── docker-compose.yml                   # PostgreSQL container definition
├── requirements.txt                     # Python dependencies
├── drop_and_recreate_tables.py          # database schema reset
├── preprocess_activities_tsv.py         # raw → clean data
├── insert_activities.py                 # load activities into DB
├── generate_dummy_users.py              # create ~70 fake users
├── insert_users.py                      # load users into DB
├── verify_data.py                       # sanity checks
├── README.md
└── SETUP.md
```