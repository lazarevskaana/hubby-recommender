"""
insert_users.py

Reads the dummy users CSV and inserts the rows into PostgreSQL.

INPUT:  data/dummy_users.csv (produced by generate_dummy_users.py)
OUTPUT: rows in the 'users' table

Run with:
    python insert_users.py

PREREQUISITES:
    - Docker container running
    - Tables exist (python drop_and_recreate_tables.py)
    - Dummy users CSV exists (python generate_dummy_users.py)


"""

import pandas as pd
from sqlalchemy.exc import SQLAlchemyError

from app.database import SessionLocal
from app.models import User

# -------------------------------------------------------------------
# CONFIGURATION
# -------------------------------------------------------------------

INPUT_PATH = "data/dummy_users.csv"


# -------------------------------------------------------------------
# HELPERS
# -------------------------------------------------------------------

def load_users(path: str) -> pd.DataFrame:
    """
    Load the dummy users CSV.
    """
    # TODO: implement
    pass


def row_to_user_dict(row: pd.Series) -> dict:
    """
    Convert a pandas row into a dict matching the User model.
    Handle NaN -> None where appropriate.
    """
    # TODO: implement
    pass


# -------------------------------------------------------------------
# MAIN PIPELINE
# -------------------------------------------------------------------

def main():
    print(f"Loading users from {INPUT_PATH}...")
    df = load_users(INPUT_PATH)
    print(f"  Loaded {len(df)} rows")

    print("Converting rows to User dicts...")
    user_dicts = [row_to_user_dict(row) for _, row in df.iterrows()]

    print("Inserting into PostgreSQL...")
    session = SessionLocal()
    inserted = 0
    skipped = 0
    try:
        session.bulk_insert_mappings(User, user_dicts)
        session.commit()
        inserted = len(user_dicts)
    except SQLAlchemyError as e:
        session.rollback()
        print(f"  ERROR during insert: {e}")
        skipped = len(user_dicts)
    finally:
        session.close()

    print(f"\n--- Summary ---")
    print(f"Inserted: {inserted}")
    print(f"Skipped:  {skipped}")


if __name__ == "__main__":
    main()