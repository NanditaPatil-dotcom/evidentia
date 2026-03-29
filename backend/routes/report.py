from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os
from datetime import datetime

try:
    from backend.database import SessionLocal
    from backend.models import Record
    from backend.utils.encryption import load_encrypted_record
    from backend.utils.pdf_generator import generate_pdf
except ModuleNotFoundError:
    from database import SessionLocal
    from models import Record
    from utils.encryption import load_encrypted_record
    from utils.pdf_generator import generate_pdf

router = APIRouter()
REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports")


def _format_record(record: Record) -> dict:
    payload = load_encrypted_record(record.record_hash)
    payload["id"] = record.id
    payload["record_hash"] = record.record_hash
    return payload


@router.get("/generate-report/")
def generate_report():
    db = SessionLocal()
    try:
        records = db.query(Record).all()
        return {
            "total": len(records),
            "records": [_format_record(record) for record in records],
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {exc}") from exc
    finally:
        db.close()


@router.get("/generate-pdf/")
def generate_pdf_api():

    db = SessionLocal()
    try:
        records = db.query(Record).all()
        formatted_data = [_format_record(record) for record in records]

        os.makedirs(REPORTS_DIR, exist_ok=True)
        filename = f"report_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.pdf"
        path = os.path.join(REPORTS_DIR, filename)

        generate_pdf(formatted_data, path)

        return FileResponse(path, media_type="application/pdf", filename="report.pdf")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {exc}") from exc
    finally:
        db.close()
