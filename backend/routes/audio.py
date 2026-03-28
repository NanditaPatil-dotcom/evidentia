from fastapi import APIRouter, UploadFile
import shutil, os

from core.main import full_pipeline
from utils.encryption import encrypt_file, decrypt_file

router = APIRouter()

@router.post("/process-audio/")
async def process_audio(file: UploadFile):

    os.makedirs("temp", exist_ok=True)

    file_path = f"temp/{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    enc_path = encrypt_file(file_path)
    os.remove(file_path)

    dec_path = f"temp/dec_{file.filename}"
    decrypt_file(enc_path, dec_path)

    result = full_pipeline(dec_path)

    os.remove(dec_path)

    result["encrypted_audio_path"] = enc_path

    return result