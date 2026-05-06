from app.database import engine, Base
import app.models  # critical: registers User and Activity with Base


def main():
    print("This will DROP all existing tables and recreate them.")
    print("All data will be lost.\n")

    confirm = input("Type 'yes' to continue: ").strip().lower()
    if confirm != "yes":
        print("Cancelled. No changes made.")
        return

    print("\nDropping tables...")
    Base.metadata.drop_all(bind=engine)
    print("Tables dropped.")

    print("\nCreating tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created.")

    print("\nDone. Database schema is now up to date.")


if __name__ == "__main__":
    main()