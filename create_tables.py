from app.database import engine, Base
import app.models

print("Creating tables...")
Base.metadata.create_all(bind=engine)
print("Done. Tables created")