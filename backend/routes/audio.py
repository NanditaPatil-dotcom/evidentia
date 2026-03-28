from fastapi import APIRouter, Form, HTTPException, UploadFile
import json
import shutil, os

from core.main import full_pipeline
try:
    from backend.utils.encryption import encrypt_file, decrypt_file
except ModuleNotFoundError:
    from utils.encryption import encrypt_file, decrypt_file

router = APIRouter()


@router.post("/process-audio/")
async def process_audio(
    file: UploadFile,
    browser_location: str | None = Form(None),
):
    parsed_browser_location = None
    if browser_location:
        try:
            parsed_browser_location = json.loads(browser_location)
        except json.JSONDecodeError as exc:
            raise HTTPException(status_code=400, detail="Invalid browser_location JSON") from exc

    os.makedirs("temp", exist_ok=True)

    file_path = f"temp/{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    enc_path = encrypt_file(file_path)
    os.remove(file_path)

    dec_path = f"temp/dec_{file.filename}"
    decrypt_file(enc_path, dec_path)

    result = full_pipeline(dec_path, browser_location=parsed_browser_location)

    os.remove(dec_path)

    result["encrypted_audio_path"] = enc_path

    return result
