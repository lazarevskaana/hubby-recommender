"""
insert_activities.py

Reads the cleaned activities CSV and inserts the rows into PostgreSQL
using SQLAlchemy.

INPUT:  data/cleaned_activities.csv (produced by preprocess_activities_tsv.py)
OUTPUT: rows in the 'activities' table in PostgreSQL

Run with:
    python insert_activities.py

PREREQUISITES:
    - Docker container running (docker compose up -d)
    - Tables exist (python drop_and_recreate_tables.py)
    - Cleaned CSV exists (python preprocess_activities_tsv.py)

"""

import json
import math
import pandas as pd
from sqlalchemy.exc import SQLAlchemyError

from app.database import SessionLocal
from app.models import Activity

# -------------------------------------------------------------------
# CONFIGURATION
# -------------------------------------------------------------------

INPUT_PATH = "data/cleaned_activities.csv"


# -------------------------------------------------------------------
# HELPERS
# -------------------------------------------------------------------

def nan_to_none(value):
    """Convert pandas NaN/float NaN to None, leave everything else as-is."""
    if value is None:
        return None
    try:
        if math.isnan(value):
            return None
    except (TypeError, ValueError):
        pass
    return value


def parse_working_hours(value):
    """
    Parse the working_hours JSON string back into a Python dict.
    Returns None if the value is missing or not a valid string.
    """
    if value is None:
        return None
    try:
        if math.isnan(value):
            return None
    except (TypeError, ValueError):
        pass
    if isinstance(value, str):
        try:
            return json.loads(value)
        except (json.JSONDecodeError, ValueError):
            return None
    return None


def load_cleaned_data(path: str) -> pd.DataFrame:
    """
    Load the cleaned CSV. The 'working_hours' column was saved as a
    JSON string — parse it back into a Python dict here.
    """
    df = pd.read_csv(path)
    df["working_hours"] = df["working_hours"].apply(parse_working_hours)
    return df


def row_to_activity_dict(row: pd.Series) -> dict:
    """
    Convert a pandas row into a dict that matches the Activity model.
    This dict will be passed to bulk_insert_mappings.
    """
    return {
        "name":              nan_to_none(row["name"]),
        "type":              nan_to_none(row["type"]),
        "subtype":           nan_to_none(row["subtype"]),
        "phone_number":      nan_to_none(row["phone_number"]),
        "rating":            nan_to_none(row["rating"]),
        "user_rating_count": int(nan_to_none(row["user_rating_count"]) or 0),
        "latitude":          nan_to_none(row["latitude"]),
        "longitude":         nan_to_none(row["longitude"]),
        "working_hours":     row["working_hours"],  # already None or dict
    }


# -------------------------------------------------------------------
# MAIN PIPELINE
# -------------------------------------------------------------------

def main():
    print(f"Loading cleaned data from {INPUT_PATH}...")
    df = load_cleaned_data(INPUT_PATH)
    print(f"  Loaded {len(df)} rows")

    print("Converting rows to Activity dicts...")
    activity_dicts = [row_to_activity_dict(row) for _, row in df.iterrows()]

    print("Inserting into PostgreSQL...")
    session = SessionLocal()
    inserted = 0
    skipped = 0
    try:
        session.bulk_insert_mappings(Activity, activity_dicts)
        session.commit()
        inserted = len(activity_dicts)
    except SQLAlchemyError as e:
        session.rollback()
        print(f"  ERROR during insert: {e}")
        skipped = len(activity_dicts)
    finally:
        session.close()

    print(f"\n--- Summary ---")
    print(f"Inserted: {inserted}")
    print(f"Skipped:  {skipped}")


if __name__ == "__main__":
    main()