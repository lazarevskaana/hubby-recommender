"""
generate_dummy_users.py

Generates ~70 realistic dummy users for testing the recommendation
system. Users have Macedonian names (Faker locale 'mk_MK') since the
destination is Skopje, and their coordinates are near actual activity
locations so the recommendation logic in Week 5 has realistic input.

OUTPUT: data/dummy_users.csv

Run with:
    python generate_dummy_users.py

PREREQUISITES:
    - data/cleaned_activities.csv must exist (used to pick coordinates)
    - faker library installed (pip install faker)
"""

import random
import pandas as pd
from faker import Faker

# -------------------------------------------------------------------
# CONFIGURATION
# -------------------------------------------------------------------

ACTIVITIES_PATH = "data/cleaned_activities.csv"
OUTPUT_PATH = "data/dummy_users.csv"
NUM_USERS = 70
DESTINATION = "Skopje"

# Random offset added to activity coordinates to scatter users around
# (roughly 500m–1km in lat/lng terms).
COORD_OFFSET_RANGE = 0.005

# Use Macedonian locale for realistic names matching the destination.
fake = Faker("mk_MK")
random.seed(42)  # reproducible results — same users every run


# -------------------------------------------------------------------
# HELPERS
# -------------------------------------------------------------------

def load_activity_coordinates(path: str) -> list[tuple[float, float]]:
    """
    Read the cleaned activities CSV and return a list of (lat, lng) pairs.
    These are used as anchor points for placing dummy users nearby.
    """
    # TODO: implement
    pass


def generate_unique_email(name: str, surname: str, used: set) -> str:
    """
    Build an email like 'marko.petrov@example.com' or, if taken,
    add digits until unique. Add the result to 'used' before returning.
    """
    # TODO: implement
    pass


def generate_user(activity_coords: list, used_emails: set) -> dict:
    """
    Build a single user dict matching the User model:
        - name, surname (Faker, Macedonian)
        - email (unique)
        - destination = "Skopje"
        - latitude, longitude — pick a random activity, add small offset
    """
    # TODO: implement
    pass


# -------------------------------------------------------------------
# MAIN PIPELINE
# -------------------------------------------------------------------

def main():
    print(f"Loading activity coordinates from {ACTIVITIES_PATH}...")
    activity_coords = load_activity_coordinates(ACTIVITIES_PATH)
    print(f"  Loaded {len(activity_coords)} coordinate pairs")

    print(f"Generating {NUM_USERS} dummy users...")
    used_emails = set()
    users = [generate_user(activity_coords, used_emails) for _ in range(NUM_USERS)]

    print(f"Writing output to {OUTPUT_PATH}...")
    df = pd.DataFrame(users)
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"  Wrote {len(df)} users")

    print("\n--- Summary ---")
    print(f"Total users generated: {len(df)}")
    print(f"Sample names:")
    print(df[["name", "surname", "email"]].head(5).to_string(index=False))


if __name__ == "__main__":
    main()