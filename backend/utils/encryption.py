# backend/utils/encryption.py

import hashlib
import json
import os

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from dotenv import load_dotenv

load_dotenv()

# AES-256-GCM for audio file encryption.
#   - Faster on binary data (audio files)
#   - Explicit nonce prepended to file (transparent format)
#   - Authenticated encryption: detects tampering (same guarantee as Fernet)

_key_hex = os.getenv("AUDIO_ENCRYPTION_KEY")

if not _key_hex:
    raise RuntimeError(
        "AUDIO_ENCRYPTION_KEY must be set in .env before the app can start. "
        'Generate one with: python -c "import os; print(os.urandom(32).hex())"'
    )

try:
    _key = bytes.fromhex(_key_hex)
    if len(_key) != 32:
        raise ValueError
except ValueError:
    raise RuntimeError(
        "AUDIO_ENCRYPTION_KEY must be a 64-character hex string (32 bytes). "
        'Generate one with: python -c "import os; print(os.urandom(32).hex())"'
    )

_aesgcm = AESGCM(_key)

# Fernet for encrypted record payloads stored on disk (separate from field-level DB encryption).
_key_raw = os.getenv("ENCRYPTION_KEY")
if not _key_raw:
    raise RuntimeError("ENCRYPTION_KEY must be set before the app can start.")

fernet = Fernet(_key_raw)

RECORDS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "secure_records")


def _ensure_records_dir():
    os.makedirs(RECORDS_DIR, exist_ok=True)


def _record_path(record_hash):
    return os.path.join(RECORDS_DIR, f"{record_hash}.bin")


def _canonicalize_record(record):
    return json.dumps(record, sort_keys=True, default=str).encode("utf-8")


def encrypt_file(path: str) -> str:
    """
    Encrypts an audio file using AES-256-GCM.

    Reads the file at `path`, encrypts it, writes the result to `path + .enc`.
    The output file format is:
        [12-byte nonce][AES-GCM ciphertext + 16-byte auth tag]

    The nonce is random per encryption — same plaintext encrypted twice
    produces different ciphertext, preventing pattern analysis.

    Returns the path to the encrypted file.
    Original file is NOT deleted here — caller (audio.py) handles cleanup.
    """
    with open(path, "rb") as f:
        data = f.read()

    nonce = os.urandom(12)
    encrypted = _aesgcm.encrypt(nonce, data, None)

    enc_path = path + ".enc"
    with open(enc_path, "wb") as f:
        f.write(nonce + encrypted)

    return enc_path


def decrypt_file(enc_path: str, output_path: str) -> str:
    """
    Decrypts an AES-256-GCM encrypted audio file.

    Reads the file at `enc_path`, extracts the 12-byte nonce from the
    beginning, decrypts and authenticates the rest, writes plaintext
    to `output_path`.

    Raises cryptography.exceptions.InvalidTag if the file has been
    tampered with — this is automatic AES-GCM behaviour.

    Returns output_path.
    """
    with open(enc_path, "rb") as f:
        raw = f.read()

    nonce = raw[:12]
    ciphertext = raw[12:]

    decrypted = _aesgcm.decrypt(nonce, ciphertext, None)

    with open(output_path, "wb") as f:
        f.write(decrypted)

    return output_path


def store_encrypted_record(record):
    _ensure_records_dir()
    payload = _canonicalize_record(record)
    encrypted_payload = fernet.encrypt(payload)
    record_hash = hashlib.sha256(encrypted_payload).hexdigest()

    with open(_record_path(record_hash), "wb") as f:
        f.write(encrypted_payload)

    return record_hash


def load_encrypted_record(record_hash):
    path = _record_path(record_hash)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Encrypted record payload not found for hash {record_hash}")

    with open(path, "rb") as f:
        encrypted_payload = f.read()

    actual_hash = hashlib.sha256(encrypted_payload).hexdigest()
    if actual_hash != record_hash:
        raise ValueError("Encrypted record payload hash mismatch")

    decrypted_payload = fernet.decrypt(encrypted_payload)
    return json.loads(decrypted_payload.decode("utf-8"))
