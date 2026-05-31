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
    if value is None:
        return None
    try:
        if math.isnan(value):
            return None
    except (TypeError, ValueError):
        pass
    return value


def parse_working_hours(value):
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
    df = pd.read_csv(path)
    df["working_hours"] = df["working_hours"].apply(parse_working_hours)
    return df


def row_to_activity_dict(row: pd.Series) -> dict:
    return {
        "name":              nan_to_none(row["name"]),
        "type":              nan_to_none(row["type"]),
        "subtype":           nan_to_none(row["subtype"]),
        "phone_number":      nan_to_none(row["phone_number"]),
        "rating":            nan_to_none(row["rating"]),
        "user_rating_count": int(nan_to_none(row["user_rating_count"]) or 0),
        "latitude":          nan_to_none(row["latitude"]),
        "longitude":         nan_to_none(row["longitude"]),
        "working_hours":     row["working_hours"],
    }


# -------------------------------------------------------------------
# MAIN PIPELINE
# -------------------------------------------------------------------

def main():
    print(f"Loading cleaned data from {INPUT_PATH}...")
    df = load_cleaned_data(INPUT_PATH)
    print(f"  Loaded {len(df)} rows")

    session = SessionLocal()
    inserted = 0
    skipped = 0

    try:
        # Fetch existing names to detect duplicates (using name + lat/lng as identity)
        existing = session.query(Activity.name, Activity.latitude, Activity.longitude).all()
        existing_set = {(r.name, r.latitude, r.longitude) for r in existing}
        print(f"  Found {len(existing_set)} existing activities in DB")

        print("Inserting new activities...")
        for _, row in df.iterrows():
            activity_dict = row_to_activity_dict(row)
            key = (activity_dict["name"], activity_dict["latitude"], activity_dict["longitude"])

            if key in existing_set:
                skipped += 1
                continue

            session.add(Activity(**activity_dict))
            existing_set.add(key)  # prevent dupes within the same run
            inserted += 1

        session.commit()

    except SQLAlchemyError as e:
        session.rollback()
        print(f"  ERROR: {e}")
    finally:
        session.close()

    print(f"\n--- Summary ---")
    print(f"Inserted: {inserted}")
    print(f"Skipped:  {skipped}")


if __name__ == "__main__":
    main()