from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
import os

# Load variables from .env into the environment
load_dotenv()

# Read the database URL we set in .env
DATABASE_URL = os.getenv("DATABASE_URL")

# The "engine" is SQLAlchemy's connection pool to PostgreSQL
engine = create_engine(DATABASE_URL)

# A session is one "conversation" with the database
# We'll use SessionLocal() in our API code to talk to the DB
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base is the parent class for all our table models
Base = declarative_base()