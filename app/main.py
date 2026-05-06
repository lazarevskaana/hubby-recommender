from fastapi import FastAPI
from app.database import engine, Base
import app.models

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Hubby API")

@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "Hubby API is running"
    }

@app.get("/health")
def health():
    return { "status" : "healthy" }