import sys
import os
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import text
from backend.database import engine
from backend.models import Base
from backend.utils.encryption import store_encrypted_record


def _ensure_records_hash_column(conn):
    columns = conn.execute(text("PRAGMA table_info(records)")).fetchall()
    column_names = {column[1] for column in columns}

    if "record_hash" not in column_names:
        conn.execute(text("ALTER TABLE records ADD COLUMN record_hash TEXT"))

    conn.execute(text("CREATE INDEX IF NOT EXISTS ix_records_record_hash ON records(record_hash)"))

    return column_names


def _parse_legacy_json(value):
    if value in (None, ""):
        return None

    try:
        return json.loads(value)
    except (TypeError, json.JSONDecodeError):
        return value


def _migrate_legacy_records(conn, column_names):
    legacy_columns = [
        "regional_text",
        "english_text",
        "logged_at",
        "coordinates",
        "events",
        "entities",
        "laws",
        "statements",
        "accused_details",
        "encrypted_audio_path",
    ]
    available_columns = [column for column in legacy_columns if column in column_names]

    if not available_columns:
        return

    select_columns = ", ".join(["id"] + available_columns)
    legacy_rows = conn.execute(
        text(f"SELECT {select_columns} FROM records WHERE record_hash IS NULL")
    ).fetchall()

    for row in legacy_rows:
        row_data = row._mapping
        payload = {
            "regional_text": row_data.get("regional_text"),
            "english_text": row_data.get("english_text"),
            "logged_at": row_data.get("logged_at"),
            "coordinates": _parse_legacy_json(row_data.get("coordinates")),
            "events": _parse_legacy_json(row_data.get("events")) or [],
            "entities": _parse_legacy_json(row_data.get("entities")) or {},
            "laws": _parse_legacy_json(row_data.get("laws")) or [],
            "statements": _parse_legacy_json(row_data.get("statements")),
            "accused_details": _parse_legacy_json(row_data.get("accused_details")),
            "encrypted_audio_path": row_data.get("encrypted_audio_path"),
        }
        record_hash = store_encrypted_record(payload)

        assignments = ["record_hash = :record_hash"]
        params = {"record_hash": record_hash, "id": row_data["id"]}

        for column in available_columns:
            assignments.append(f"{column} = NULL")

        conn.execute(
            text(f"UPDATE records SET {', '.join(assignments)} WHERE id = :id"),
            params,
        )


def init_db():
    # Create all tables defined in models.py
    Base.metadata.create_all(bind=engine)

    # Apply SQLite hardening PRAGMAs
    with engine.connect() as conn:
        column_names = _ensure_records_hash_column(conn)
        _migrate_legacy_records(conn, column_names)

        # WAL mode: better write reliability, allows concurrent reads
        conn.execute(text("PRAGMA journal_mode=WAL"))

        # Enforce foreign key constraints (SQLite ignores them by default)
        conn.execute(text("PRAGMA foreign_keys=ON"))

        # Overwrite deleted rows with zeros on disk
        # Without this, deleted records are physically recoverable
        conn.execute(text("PRAGMA secure_delete=ON"))

        conn.commit()

    print("Database initialised with hash-only record storage and hardened PRAGMAs.")


if __name__ == "__main__":
    init_db()
