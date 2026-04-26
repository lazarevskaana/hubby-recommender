# Project Setup Guide

## Prerequisites

Make sure you have the following installed before starting:

- **Python 3.11+**
- **Docker & Docker Compose**
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
python -m venv .venv
source .venv/bin/activate        # Linux / macOS
# .venv\Scripts\activate         # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and fill in any required values (database credentials, secrets, etc.).

### 5. Check for port conflicts

The database runs on port **5432**. If something is already using that port (e.g. a local PostgreSQL installation), stop it first:

```bash
# Check what's using port 5432
sudo ss -tlnp | grep 5432

# Stop a local PostgreSQL service if running
sudo systemctl stop postgresql
```

### 6. Start the database

```bash
docker compose up -d
```

---

## Starting the Project (Daily Use)

Every time you open the project, run these commands in order:

```bash
# 1. Activate the virtual environment
source .venv/bin/activate        # Linux / macOS
# .venv\Scripts\activate         # Windows

# 2. Start the database container (if not already running)
docker compose up -d

# 3. Start the API server
uvicorn app.main:app --reload
```

The API will be available at: **http://localhost:8000**  
Interactive docs (Swagger UI): **http://localhost:8000/docs**

---

## Stopping the Project

```bash
# Stop the API server
Ctrl + C

# Stop the database container
docker compose down
```

> Use `docker compose down -v` to also **delete the database volume** (all data will be lost). Only do this if you want a clean slate.

---

## Common Issues

### Port 5432 already in use
A local PostgreSQL service is running on the same port as the Docker container.

```bash
sudo systemctl stop postgresql
docker compose up -d
```

### Virtual environment not activated
If you see `ModuleNotFoundError`, you forgot to activate the venv:

```bash
source .venv/bin/activate
```

### Docker container not starting
Check the container logs for details:

```bash
docker compose logs
```

---

## Project Structure

```
.
├── .env.example        # Environment variable template
├── .env                # Your local config (not committed to git)
├── docker-compose.yml  # Database container definition
├── requirements.txt    # Python dependencies
└── ...                 # Application source files
```