from fastapi import APIRouter, HTTPException

try:
    from backend.database import SessionLocal
    from backend.models import Record
    from backend.utils.encryption import load_encrypted_record, store_encrypted_record
except ModuleNotFoundError:
    from database import SessionLocal
    from models import Record
    from utils.encryption import load_encrypted_record, store_encrypted_record

router = APIRouter()


@router.post("/save-record/")
def save_record(data: dict):
    db = SessionLocal()
    try:
        payload = {
            "regional_text": data["regional_text"],
            "english_text": data["english_text"],
            "logged_at": data["logged_at"],
            "coordinates": data.get("coordinates"),
            "events": data.get("events", []),
            "entities": data.get("entities", {}),
            "laws": data.get("laws", []),
            "statements": data.get("statements"),
            "accused_details": data.get("accused_details"),
            "encrypted_audio_path": data.get("encrypted_audio_path"),
        }

        record_hash = store_encrypted_record(payload)
        record = Record(record_hash=record_hash)

        db.add(record)
        db.commit()
        db.refresh(record)

        return {"message": "saved", "id": record.id, "record_hash": record_hash}
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to securely store record: {exc}") from exc
    finally:
        db.close()


@router.get("/get-records/")
def get_records():
    db = SessionLocal()
    try:
        records = db.query(Record).all()
        result = []

        for record in records:
            payload = load_encrypted_record(record.record_hash)
            payload["id"] = record.id
            payload["record_hash"] = record.record_hash
            result.append(payload)

        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to read secure records: {exc}") from exc
    finally:
        db.close()
