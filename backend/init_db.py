import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import text
from backend.database import engine
from backend.models import Base


def init_db():
    # Create all tables defined in models.py
    Base.metadata.create_all(bind=engine)

    # Apply SQLite hardening PRAGMAs
    with engine.connect() as conn:
        # WAL mode: better write reliability, allows concurrent reads
        conn.execute(text("PRAGMA journal_mode=WAL"))

        # Enforce foreign key constraints (SQLite ignores them by default)
        conn.execute(text("PRAGMA foreign_keys=ON"))

        # Overwrite deleted rows with zeros on disk
        # Without this, deleted records are physically recoverable
        conn.execute(text("PRAGMA secure_delete=ON"))

        conn.commit()

    print("Database initialised with encryption-ready schema and hardened PRAGMAs.")


if __name__ == "__main__":
    init_db()