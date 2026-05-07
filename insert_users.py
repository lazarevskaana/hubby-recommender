

import pandas as pd
from sqlalchemy.exc import SQLAlchemyError

from app.database import SessionLocal
from app.models import User

INPUT_PATH = "data/dummy_users.csv"


# -------------------------------------------------------------------
# HELPERS
# -------------------------------------------------------------------

def load_users(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df = df.where(pd.notnull(df), None)
    return df


def row_to_user_dict(row: pd.Series) -> dict:
    return {
        "name": row["name"] if pd.notnull(row["name"]) else None,
        "surname": row["surname"] if pd.notnull(row["surname"]) else None,
        "email": row["email"] if pd.notnull(row["email"]) else None,
        "destination": row["destination"] if pd.notnull(row["destination"]) else None,
        "latitude": row["latitude"] if pd.notnull(row["latitude"]) else None,
        "longitude": row["longitude"] if pd.notnull(row["longitude"]) else None,
    }


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