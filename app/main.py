from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db
from app.routers import activities, users, recommendations

app = FastAPI(title="Hubby Recommender API")

# Allow the frontend (running on localhost:5500 or wherever) to call the API.
# In production you'd lock this to specific origins.
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/")
def root():
    return {"message": "Hubby Recommender API is running"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/health/db")
def health_check_db(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        return {"status": "error", "database": "disconnected", "detail": str(e)}
    

# Register routers — keeps the application modular.
app.include_router(activities.router)
app.include_router(users.router)
app.include_router(recommendations.router) 