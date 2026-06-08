# Hubby Recommender — Setup Guide

This guide walks you through running Hubby Recommender locally — from a fresh repo clone to seeing recommendations in your browser. Total setup time: about 10 minutes.

## Prerequisites

Make sure you have the following installed before starting:

- **Python 3.11+**
- **Docker Desktop** (running)
- **Git**
- **A modern web browser** (Chrome, Firefox, or Safari)

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

The defaults in `.env.example` work for local development — no editing required.

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

### 7. Populate the database

Run these scripts in order:

```bash
python preprocess_activities_tsv.py    # cleans both raw TSV files → cleaned_activities.csv
python insert_activities.py            # loads 206 activities into PostgreSQL
python generate_dummy_users.py         # generates ~70 dummy users
python insert_users.py                 # loads users into PostgreSQL
python verify_data.py                  # sanity checks
```

After this you should have **206 activities** and **~70 users** in the database.

---

## Daily Workflow

To run the application, you need **two terminal windows** open at the same time — one for the backend, one for the frontend. Don't close either while you're using the app.

### Terminal 1 — Backend

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

Wait until you see `Application startup complete.` — then **leave this terminal alone**.

The API will be available at: **http://localhost:8000**  
Interactive docs (Swagger UI): **http://localhost:8000/docs**

### Terminal 2 — Frontend

Open a **new** terminal window (don't close the first one):

```bash
cd frontend
python -m http.server 5500
```

You should see `Serving HTTP on :: port 5500`.

### Browser

Open **http://localhost:5500** in your browser. Allow geolocation when prompted (or the app falls back to Skopje coordinates).

You should see:
- The orange "H" header at the top
- The "Where to next?" hero heading
- A search bar with five inputs and a Search button
- An interactive map on the left
- Recommendation cards on the right

---

## Verifying Everything Works

After both servers are running, test these:

| Check | Expected result |
|---|---|
| Open `http://localhost:8000/health/db` | `{"status":"ok","database":"connected"}` |
| Open `http://localhost:8000/docs` | Swagger UI with all endpoints listed |
| Run `SELECT COUNT(*) FROM activities;` in DBeaver | `206` |
| Change context dropdown from Auto to Dinner | Cards re-rank — restaurants/bars climb to the top |
| Hover any card | Detail view appears with "Open in Google Maps" button |
| Click an orange pin on the map | Polished popup with name, rating, score |

---

## Stopping the Project

```bash
# Stop the API server (in Terminal 1)
Ctrl + C

# Stop the frontend (in Terminal 2)
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

If the schema changes (`app/models.py` is modified) or you want clean data:

```bash
python drop_and_recreate_tables.py
```

This drops all tables and recreates them. You'll need to re-run the data population scripts afterwards (preprocess → insert activities → generate users → insert users).

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

### "Address already in use" (port 8000 or 5500)

A previous server is still running and holding the port. Kill it:

```bash
lsof -ti:8000 | xargs kill -9      # for the backend
lsof -ti:5500 | xargs kill -9      # for the frontend
```

This happens when a terminal window is closed without first pressing `Ctrl+C`. To avoid it next time, always stop the server cleanly with `Ctrl+C` before closing the window.

### Frontend shows a directory listing instead of the app

You ran `python -m http.server` from the wrong folder. Stop it with `Ctrl+C`, then:

```bash
cd frontend
python -m http.server 5500
```

The `cd frontend` step is essential — `index.html` lives inside that folder.

### Page loads but cards say "Could not reach the API"

The backend isn't running. Check Terminal 1 — if you see `Shutting down` then it was killed. Restart it with `uvicorn app.main:app --reload` and leave the terminal alone.

To verify the backend is up independently, open `http://localhost:8000/health/db` in a new browser tab. You should see a JSON response confirming the connection.

### Browser shows old behavior / changes don't appear

The browser cached the previous version of the JavaScript. Hard refresh:

- **macOS:** `Cmd + Shift + R`
- **Windows/Linux:** `Ctrl + Shift + R`

If that doesn't work, open DevTools (`Cmd+Option+I` / `F12`), right-click the refresh button, and choose **"Empty Cache and Hard Reload"**.

### Port 5432 already in use

Something else is running on port 5432 — usually a local PostgreSQL installation.

**macOS (Homebrew PostgreSQL):**
```bash
brew services stop postgresql
```

**Windows:** Open Services (Win+R → `services.msc`), find any PostgreSQL service, right-click → Stop.

Alternatively, change the port in `docker-compose.yml` from `"5432:5432"` to `"5433:5432"` and update `DATABASE_URL` in `.env` to use port 5433.

### Database stuck at 153 activities instead of 206

You skipped the data population scripts. Each teammate has their own local database — running the scripts is required on every machine. Run them again:

```bash
python preprocess_activities_tsv.py
python insert_activities.py
```

You should see `Inserted: 53, Skipped: 153` or similar.

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

---

## Project Structure

```
hubby-recommender/
├── app/
│   ├── __init__.py
│   ├── main.py                      # FastAPI entry, CORS, router registration
│   ├── database.py                  # SQLAlchemy session factory
│   ├── models.py                    # User and Activity models
│   ├── schemas.py                   # Pydantic schemas for API I/O
│   ├── recommendations_config.py    # Scoring weights, time windows, category map
│   ├── routers/
│   │   ├── activities.py            # Activity API endpoints
│   │   ├── users.py                 # User API endpoints (incl. GET /users/{id})
│   │   └── recommendations.py       # Recommendations API endpoints + pipeline
│   └── services/
│       ├── geo.py                   # Haversine, radius filtering
│       ├── opening_hours.py         # is_open_at check
│       ├── context.py               # Time-of-day inference
│       └── scoring.py               # The four sub-scores + final score
├── data/
│   ├── unique_activities.tsv        # Original raw dataset (153 rows)
│   ├── uniques_activities_2.tsv     # Week 6 expansion (53 rows)
│   ├── cleaned_activities.csv       # Output of preprocessing (gitignored)
│   └── dummy_users.csv              # Output of user generation (gitignored)
├── frontend 
│   ├── index.html                   # Single-page app with embedded styles
│   └── app.js                       # Fetch, render, Leaflet, hover popover
├── docs/
│   ├── screenshot_landing.png       # README screenshot
│   ├── screenshot_hover.png         # README screenshot
│   ├── team_documentation_en.pdf    # Full technical docs (English)
│   └── team_documentation_mk.pdf    # Full technical docs (Macedonian)
├── .env.example                     # Environment variable template
├── .env                             # Local config (gitignored)
├── .gitignore
├── docker-compose.yml               # PostgreSQL container definition
├── requirements.txt                 # Python dependencies
├── drop_and_recreate_tables.py
├── preprocess_activities_tsv.py
├── insert_activities.py
├── generate_dummy_users.py
├── insert_users.py
├── verify_data.py
├── README.md                        # Public-facing project overview
└── SETUP.md                         # This file
``````