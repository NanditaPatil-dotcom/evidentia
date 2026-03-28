from fastapi import APIRouter
from fastapi.responses import FileResponse
from database import SessionLocal
from models import Record
import json, os

from utils.pdf_generator import generate_pdf

router = APIRouter()


@router.get("/generate-report/")
def generate_report(user_id: int):
    db = SessionLocal()

    records = db.query(Record).filter(Record.user_id == user_id).all()

    db.close()

    return {
        "total": len(records),
        "records": [
            {
                "transcript": r.transcript,
                "events": json.loads(r.events),
                "laws": json.loads(r.laws),
                "statements": json.loads(r.statements)
            }
            for r in records
        ]
    }


@router.get("/generate-pdf/")
def generate_pdf_api(user_id: int):

    db = SessionLocal()
    records = db.query(Record).filter(Record.user_id == user_id).all()
    db.close()

    data = [
        {
            "transcript": r.transcript,
            "events": json.loads(r.events),
            "laws": json.loads(r.laws),
            "statements": json.loads(r.statements)
        }
        for r in records
    ]

    os.makedirs("temp", exist_ok=True)
    path = f"temp/report_{user_id}.pdf"

    generate_pdf(data, path)

    return FileResponse(path, media_type="application/pdf", filename="report.pdf")