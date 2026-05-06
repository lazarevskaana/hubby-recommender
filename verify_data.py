"""
verify_data.py

Sanity-check the data in PostgreSQL after running the insert scripts.
Prints counts, distributions, and spot-checks a few rows.

Run with:
    python verify_data.py

PREREQUISITES:
    - Docker container running
    - Activities and users have been inserted

"""

from sqlalchemy import func

from app.database import SessionLocal
from app.models import Activity, User


def verify_activities(session) -> None:
    """
    Print activity-related stats:
    - Total count
    - Distribution by type
    - How many have null working_hours
    - A few sample rows
    """
    # TODO: implement
    # Hint: session.query(Activity).count()
    # Hint: session.query(Activity.type, func.count()).group_by(Activity.type).all()
    pass


def verify_users(session) -> None:
    """
    Print user-related stats:
    - Total count
    - Distribution by destination
    - A few sample rows
    """
    # TODO: implement
    pass


def main():
    print("=" * 50)
    print("DATABASE VERIFICATION REPORT")
    print("=" * 50)

    session = SessionLocal()
    try:
        print("\n--- Activities ---")
        verify_activities(session)

        print("\n--- Users ---")
        verify_users(session)
    finally:
        session.close()

    print("\n" + "=" * 50)
    print("Verification complete.")


if __name__ == "__main__":
    main()