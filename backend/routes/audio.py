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
    accused: str | None = Form(None),
):
    parsed_browser_location = None
    parsed_accused = None
    if browser_location:
        try:
            parsed_browser_location = json.loads(browser_location)
        except json.JSONDecodeError as exc:
            raise HTTPException(status_code=400, detail="Invalid browser_location JSON") from exc
    if accused:
        try:
            parsed_accused = json.loads(accused)
        except json.JSONDecodeError as exc:
            raise HTTPException(status_code=400, detail="Invalid accused JSON") from exc

    os.makedirs("temp", exist_ok=True)

    file_path = f"temp/{file.filename}"
    enc_path = None
    dec_path = f"temp/dec_{file.filename}"

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        enc_path = encrypt_file(file_path)
        os.remove(file_path)

        decrypt_file(enc_path, dec_path)

        result = full_pipeline(
            dec_path,
            browser_location=parsed_browser_location,
            accused=parsed_accused,
        )

        result.setdefault("accused_details", {
            "name": None,
            "relation": None,
            "description": None,
        })

        result["encrypted_audio_path"] = enc_path

        return result
    except HTTPException:
        raise
    except Exception as exc:
        error_message = str(exc).lower()
        if "temporary failure in name resolution" in error_message or "connecterror" in error_message:
            raise HTTPException(
                status_code=503,
                detail="Audio transcription service is unreachable right now. Check your internet connection and API service access, then retry.",
            ) from exc
        raise HTTPException(
            status_code=500,
            detail=f"Audio processing failed: {exc}",
        ) from exc
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
        if os.path.exists(dec_path):
            os.remove(dec_path)
