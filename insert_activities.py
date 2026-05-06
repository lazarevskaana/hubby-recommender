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

def load_cleaned_data(path: str) -> pd.DataFrame:
    """
    Load the cleaned CSV. The 'working_hours' column was saved as a
    JSON string — parse it back into a Python dict here.
    """
    # TODO: implement
    # Hint: pd.read_csv(path), then df["working_hours"] = df["working_hours"].apply(...)
    # Be careful: missing/null working_hours should stay None, not crash json.loads
    pass


def row_to_activity_dict(row: pd.Series) -> dict:
    """
    Convert a pandas row into a dict that matches the Activity model.
    This dict will be passed to bulk_insert_mappings.
    """
    # TODO: implement
    # Return something like:
    # {
    #     "name": row["name"],
    #     "type": row["type"],
    #     "subtype": row["subtype"],
    #     "phone_number": row["phone_number"],
    #     "rating": row["rating"],
    #     "user_rating_count": row["user_rating_count"],
    #     "latitude": row["latitude"],
    #     "longitude": row["longitude"],
    #     "working_hours": row["working_hours"],
    # }
    # Watch out for NaN values from pandas — convert them to None.
    pass


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
        # Bulk insert is much faster than adding one row at a time.
        # If you prefer, you can also loop with session.add() and session.commit().
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