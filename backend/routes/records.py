from fastapi import APIRouter
from database import SessionLocal
from models import Record
import json

router = APIRouter()

@router.post("/save-record/")
def save_record(data: dict):
    db = SessionLocal()

    record = Record(
        user_id=data["user_id"],
        transcript=data["transcript"],
        events=json.dumps(data["events"]),
        entities=json.dumps(data["entities"]),
        laws=json.dumps(data["laws"]),
        statements=json.dumps(data["statements"]),
        timestamp=data["timestamp"],
        location=json.dumps(data["location"]),
        encrypted_audio_path=data["encrypted_audio_path"]
    )

    db.add(record)
    db.commit()
    db.close()

    return {"message": "saved"}


@router.get("/get-records/")
def get_records(user_id: int):
    db = SessionLocal()

    records = db.query(Record).filter(Record.user_id == user_id).all()

    result = []

    for r in records:
        result.append({
            "id": r.id,
            "transcript": r.transcript,
            "events": json.loads(r.events),
            "entities": json.loads(r.entities),
            "laws": json.loads(r.laws),
            "statements": json.loads(r.statements),
            "timestamp": r.timestamp,
            "location": json.loads(r.location)
        })

    db.close()
    return result