try:
    from backend.database import engine
    from backend.models import Base
except ModuleNotFoundError:
    from database import engine
    from models import Base

# Create tables
Base.metadata.create_all(bind=engine)

print("Database & tables created successfully!")
