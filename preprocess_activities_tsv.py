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


# -------------------------------------------------------------------
# COLUMN CLEANING
# -------------------------------------------------------------------

def load_raw_data(path: str) -> pd.DataFrame:
    """
    Read the TSV file using pandas.
    The TSV is tab-separated and uses messy nested column names like
    'places/displayName/text'.
    """
    # TODO: implement
    pass


def drop_unused_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove columns we don't need:
    - places/id           (Google's internal ID, not used downstream)
    - places/displayName/languageCode  (always 'en')
    - places/priceLevel   (sparse, not part of our schema)
    """
    # TODO: implement
    pass


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
    # TODO: implement
    pass


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
    # TODO: implement
    pass


def add_type_category(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create the 'type' column by mapping subtype -> broad category
    using TYPE_CATEGORY_MAP. Anything not in the map -> 'other'.
    """
    # TODO: implement
    pass


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

def parse_day_string(day_string: str) -> list | None:
    """
    Convert a single day string like 'Monday: 9:00 AM – 11:30 PM'
    into a list of {open, close} dicts.

    Returns None if the input is missing/empty.
    Returns [] if the day is 'Closed'.
    """
    # TODO: implement
    pass


def build_working_hours_json(row: pd.Series) -> str:
    """
    For a single row, combine the 7 weekday columns into one JSON dict.
    Returns a JSON-encoded string ready for the CSV.

    Note: we save as a JSON string in the CSV. The insert script will
    parse it back with json.loads() before inserting into the DB.
    """
    # TODO: implement
    pass


def transform_working_hours(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply build_working_hours_json to each row, add as a 'working_hours'
    column, and drop the 7 original weekday columns.
    """
    # TODO: implement
    pass


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