"""
preprocess_activities_tsv.py

Reads the raw Google Places TSV file, cleans and transforms it into a
database-ready CSV that matches the Activity model in app/models.py.

INPUT:  data/unique_activities.tsv
OUTPUT: data/cleaned_activities.csv

Run with:
    python preprocess_activities_tsv.py

"""

import json
import pandas as pd
from datetime import datetime
import re

# -------------------------------------------------------------------
# CONFIGURATION
# -------------------------------------------------------------------

INPUT_PATH = "data/unique_activities.tsv"
OUTPUT_PATH = "data/cleaned_activities.csv"

# Map raw Google primaryType values to broad categories.
# This is the "type" column in our schema.
# The original value is preserved as "subtype".
TYPE_CATEGORY_MAP = {
    # food
    "restaurant": "food",
    "pizza_restaurant": "food",
    "italian_restaurant": "food",
    "fast_food_restaurant": "food",
    "meal_takeaway": "food",
    "meal_delivery": "food",
    # cafe
    "cafe": "cafe",
    "coffee_shop": "cafe",
    "bakery": "cafe",
    "cake_shop": "cafe",
    # nightlife
    "bar": "nightlife",
    "night_club": "nightlife",
    # culture
    "museum": "culture",
    "art_gallery": "culture",
    "history_museum": "culture",
    "tourist_attraction": "culture",
    # entertainment
    "movie_theater": "entertainment",
    "bowling_alley": "entertainment",
    # accommodation
    "hotel": "accommodation",
    "lodging": "accommodation",
}

COLUMN_RENAME_MAP = {
    "places/internationalPhoneNumber": "phone_number",
    "places/location/latitude": "latitude",
    "places/location/longitude": "longitude",
    "places/rating": "rating",
    "places/userRatingCount": "user_rating_count",
    "places/displayName/text": "name",
    "places/primaryType": "subtype",
    "places/regularOpeningHours/weekdayDescriptions/0": "monday",
    "places/regularOpeningHours/weekdayDescriptions/1": "tuesday",
    "places/regularOpeningHours/weekdayDescriptions/2": "wednesday",
    "places/regularOpeningHours/weekdayDescriptions/3": "thursday",
    "places/regularOpeningHours/weekdayDescriptions/4": "friday",
    "places/regularOpeningHours/weekdayDescriptions/5": "saturday",
    "places/regularOpeningHours/weekdayDescriptions/6": "sunday",
}

DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


# -------------------------------------------------------------------
# COLUMN CLEANING
# -------------------------------------------------------------------

def load_raw_data(path: str) -> pd.DataFrame:
    """
    Read the TSV file using pandas.
    The TSV is tab-separated and uses messy nested column names like
    'places/displayName/text'.
    """
    df = pd.read_csv(path, sep='\t', dtype=str)
    # dtype=str keeps everything raw and removes possibility of pandas mangling data
    return df


def drop_unused_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove columns we don't need:
    - places/id           (Google's internal ID, not used downstream)
    - places/displayName/languageCode  (always 'en')
    - places/priceLevel   (sparse, not part of our schema)
    """
    cols_to_drop = [
        "places/id",
        "places/displayName/languageCode",
        "places/priceLevel",
    ]
    return df.drop(columns=cols_to_drop, errors="ignore")


def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Rename columns to match the Activity model:
        places/internationalPhoneNumber -> phone_number
        places/location/latitude        -> latitude
        places/location/longitude       -> longitude
        places/rating                   -> rating
        places/userRatingCount          -> user_rating_count
        places/displayName/text         -> name
        places/primaryType              -> subtype
    """
    return df.rename(columns=COLUMN_RENAME_MAP)

# -------------------------------------------------------------------
# VALUE NORMALIZATION
# -------------------------------------------------------------------

def normalize_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean up cell values:
    - Trim whitespace from text fields (name, phone_number)
    - Empty subtype -> 'other' (and type also -> 'other')
    - Convert latitude, longitude, rating to numeric (float)
    - Empty user_rating_count -> 0
    - Empty phone_number stays empty (will become null in DB)
    """
    # Trim whitespace from text fields
    df["name"] = df["name"].str.strip()
    df["phone_number"] = df["phone_number"].str.strip()

    # Empty subtype -> 'other' (type will also become 'other' via the map)
    df["subtype"] = df["subtype"].str.strip().fillna("other").replace("", "other")

    # Coerce numeric columns - invalid / missing become NaN
    for col in ["latitude", "longitude", "rating"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Empty user_rating_count -> 0
    df["user_rating_count"] = pd.to_numeric(df["user_rating_count"], errors="coerce").fillna(0).astype(int)

    # phone_number: Leave NaN as-is (null in DB)

    return df

def add_type_category(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create the 'type' column by mapping subtype -> broad category
    using TYPE_CATEGORY_MAP. Anything not in the map -> 'other'.
    """
    df["type"] = df["subtype"].map(TYPE_CATEGORY_MAP).fillna("other")
    return df


# -------------------------------------------------------------------
# WORKING HOURS TRANSFORMATION
# -------------------------------------------------------------------
# This is the hardest part. The TSV has 7 columns (one per weekday),
# each containing a human-readable string like:
#     "Monday: 9:00 AM – 11:30 PM"
# We collapse all 7 into a single JSON column called 'working_hours'.
#
# Output shape:
#   {
#     "monday":    [{"open": "09:00", "close": "23:30"}],
#     "tuesday":   [{"open": "09:00", "close": "23:30"}],
#     ...
#     "sunday":    []
#   }
#
# Edge cases to handle:
#   - "Open 24 hours"     -> [{"open": "00:00", "close": "23:59"}]
#   - "Closed"            -> []
#   - Missing/empty       -> the day's value is None
#   - Split intervals     -> multiple entries in the array
#       e.g. "9:00 AM – 1:00 PM, 3:00 PM – 7:00 PM"
#       -> [{"open": "09:00", "close": "13:00"},
#           {"open": "15:00", "close": "19:00"}]
# -------------------------------------------------------------------

def _parse_time(t: str) -> str:
    t = t.strip()
    try:
        return datetime.strptime(t, "%I:%M %p").strftime("%H:%M")
    except ValueError:
        return datetime.strptime(t, "%H:%M").strftime("%H:%M")

def _parse_interval(interval: str) -> dict:
    parts = re.split(r"\s[–—-]\s", interval)
    open_str, close_str = parts[0].strip(), parts[1].strip()

    # If open has no AM/PM but close has PM, inherit PM
    has_ampm = lambda s: s.endswith("AM") or s.endswith("PM")
    if not has_ampm(open_str) and close_str.endswith("PM"):
        open_str += " PM"

    return {"open": _parse_time(open_str), "close": _parse_time(close_str)}

def parse_day_string(day_string: str) -> list | None:
    """
    Convert a single day string like 'Monday: 9:00 AM – 11:30 PM'
    into a list of {open, close} dicts.

    Returns None if the input is missing/empty.
    Returns [] if the day is 'Closed'.
    """
    if pd.isna(day_string) or str(day_string).strip() == "":
        return None

    # Strip the "DayName: " prefix
    rest = day_string.split(": ", 1)[1] if ": " in day_string else day_string.strip()

    if rest == "Open 24 hours":
        return [ { "open": "00:00", "close": "23:59" } ]

    if rest == "Closed":
        return []

    # One or more intervals, e.g. "9:00 AM - 1:00 PM, 3:00 PM - 7:00 PM"
    result = []
    for interval in rest.split(", "):
        result.append(_parse_interval(interval))
    return result

def build_working_hours_json(row: pd.Series) -> str:
    """
    For a single row, combine the 7 weekday columns into one JSON dict.
    Returns a JSON-encoded string ready for the CSV.

    Note: we save as a JSON string in the CSV. The insert script will
    parse it back with json.loads() before inserting into the DB.
    """
    return json.dumps( { day: parse_day_string(row[day]) for day in DAYS } )


def transform_working_hours(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply build_working_hours_json to each row, add as a 'working_hours'
    column, and drop the 7 original weekday columns.
    """
    df["working_hours"] = df.apply(build_working_hours_json, axis=1)
    return df.drop(columns=DAYS)


# -------------------------------------------------------------------
# MAIN PIPELINE
# -------------------------------------------------------------------

def main():
    print("Loading raw TSV...")
    df = load_raw_data(INPUT_PATH)
    print(f"  Loaded {len(df)} rows")

    print("Dropping unused columns...")
    df = drop_unused_columns(df)

    print("Renaming columns...")
    df = rename_columns(df)

    print("Normalizing values...")
    df = normalize_values(df)

    print("Mapping types to broad categories...")
    df = add_type_category(df)

    print("Transforming working hours...")
    df = transform_working_hours(df)

    print(f"\nWriting output to {OUTPUT_PATH}...")
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"  Wrote {len(df)} rows")

    # Summary stats — useful for verification and the team report
    print("\n--- Summary ---")
    print(f"Total activities:          {len(df)}")
    print(f"Type distribution:")
    print(df["type"].value_counts().to_string())


if __name__ == "__main__":
    main()