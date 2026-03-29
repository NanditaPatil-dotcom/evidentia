from fastapi import APIRouter
import json

try:
    from backend.database import SessionLocal
    from backend.models import Record
except ModuleNotFoundError:
    from database import SessionLocal
    from models import Record

router = APIRouter()


@router.post("/save-record/")
def save_record(data: dict):
    db = SessionLocal()

    record = Record(
        regional_text=data["regional_text"],
        english_text=data["english_text"],
        logged_at=data["logged_at"],
        coordinates=json.dumps(data["coordinates"]),
        events=json.dumps(data["events"]),
        entities=json.dumps(data["entities"]),
        laws=json.dumps(data["laws"]),
        statements=json.dumps(data["statements"]),
        accused_details=json.dumps(data.get("accused_details")),
        encrypted_audio_path=data.get("encrypted_audio_path"),
    )
    # ↑ Nothing changes here — the @property setters in the model
    #   intercept each assignment and encrypt before it hits the DB.

    db.add(record)
    db.commit()
    db.close()

    return {"message": "saved"}


@router.get("/get-records/")
def get_records():
    db = SessionLocal()
    records = db.query(Record).all()

    result = []

    for r in records:
        # r.english_text, r.events etc. are already decrypted by @property getters.
        # json.loads still needed for the fields that were stored as JSON strings.
        result.append({
            "id": r.id,
            "regional_text": r.regional_text,
            "english_text":  r.english_text,
            "events":        json.loads(r.events)         if r.events         else [],
            "entities":      json.loads(r.entities)       if r.entities       else {},
            "laws":          json.loads(r.laws)           if r.laws           else [],
            "statements":    json.loads(r.statements)     if r.statements     else [],
            "accused_details": json.loads(r.accused_details) if r.accused_details else None,
            "logged_at":     r.logged_at,
            "coordinates":   json.loads(r.coordinates)   if r.coordinates    else None,
            "encrypted_audio_path": r.encrypted_audio_path,
        })

    db.close()
    return result