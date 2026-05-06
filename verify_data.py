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
    total = session.query(Activity).count()
    print(f"  Total activities: {total}")

    print("\n  Distribution by type:")
    type_counts = (
        session.query(Activity.type, func.count(Activity.type))
        .group_by(Activity.type)
        .order_by(func.count(Activity.type).desc())
        .all()
    )
    for activity_type, count in type_counts:
        print(f"    {activity_type or '(null)':<20} {count}")

    null_hours = session.query(Activity).filter(Activity.working_hours == None).count()
    print(f"\n  Activities with null working_hours: {null_hours}")

    print("\n  Sample rows (first 5):")
    samples = session.query(Activity).limit(5).all()
    for a in samples:
        wh_preview = str(a.working_hours)[:60] + "..." if a.working_hours else "NULL"
        print(f"    [{a.id}] {a.name} | {a.type} | {a.subtype} | rating={a.rating} | wh={wh_preview}")


def verify_users(session) -> None:
    """
    Print user-related stats:
    - Total count
    - Distribution by destination
    - A few sample rows
    """
    total = session.query(User).count()
    print(f"  Total users: {total}")

    if total == 0:
        print("  (No users yet — Person 4 hasn't inserted them yet. That's fine!)")
        return

    print("\n  Distribution by destination:")
    dest_counts = (
        session.query(User.destination, func.count(User.destination))
        .group_by(User.destination)
        .order_by(func.count(User.destination).desc())
        .all()
    )
    for destination, count in dest_counts:
        print(f"    {destination or '(null)':<30} {count}")

    print("\n  Sample rows (first 3):")
    samples = session.query(User).limit(3).all()
    for u in samples:
        print(f"    [{u.id}] {u}")


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