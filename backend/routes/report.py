from fastapi import APIRouter
from fastapi.responses import FileResponse
import json, os
from datetime import datetime

try:
    from backend.database import SessionLocal
    from backend.models import Record
    from backend.utils.pdf_generator import generate_pdf
except ModuleNotFoundError:
    from database import SessionLocal
    from models import Record
    from utils.pdf_generator import generate_pdf

router = APIRouter()


def _format_record(record: Record) -> dict:
    return {
        "english_text": record.english_text,
        "events": json.loads(record.events),
        "entities": json.loads(record.entities),
        "laws": json.loads(record.laws),
        "statements": json.loads(record.statements),
        "logged_at": record.logged_at,
        "coordinates": json.loads(record.coordinates),
    }


@router.get("/generate-report/")
def generate_report():
    db = SessionLocal()

    records = db.query(Record).all()

    db.close()

    return {
        "total": len(records),
        "records": [_format_record(record) for record in records]
    }


@router.get("/generate-pdf/")
def generate_pdf_api():

    db = SessionLocal()
    records = db.query(Record).all()
    db.close()

    formatted_data = [_format_record(record) for record in records]

    os.makedirs("reports", exist_ok=True)
    filename = f"report_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.pdf"
    path = f"reports/{filename}"

    generate_pdf(formatted_data, path)

    return FileResponse(path, media_type="application/pdf", filename="report.pdf")
