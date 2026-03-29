# backend/utils/encryption.py

import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from dotenv import load_dotenv

load_dotenv()

# AES-256-GCM replaces Fernet for audio file encryption.
# Reasons:
#   - Faster on binary data (audio files)
#   - Explicit nonce prepended to file (transparent format)
#   - Authenticated encryption: detects tampering (same guarantee as Fernet)
#   - Does not load entire file into RAM in one Fernet token
#   - Industry standard for file-level encryption

_key_hex = os.getenv("AUDIO_ENCRYPTION_KEY")

if not _key_hex:
    raise RuntimeError(
        "AUDIO_ENCRYPTION_KEY must be set in .env before the app can start. "
        "Generate one with: python -c \"import os; print(os.urandom(32).hex())\""
    )

# Key must be exactly 32 bytes for AES-256
try:
    _key = bytes.fromhex(_key_hex)
    if len(_key) != 32:
        raise ValueError
except ValueError:
    raise RuntimeError(
        "AUDIO_ENCRYPTION_KEY must be a 64-character hex string (32 bytes). "
        "Generate one with: python -c \"import os; print(os.urandom(32).hex())\""
    )

_aesgcm = AESGCM(_key)


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

    # 12-byte (96-bit) nonce — standard for AES-GCM, never reuse
    nonce = os.urandom(12)
    encrypted = _aesgcm.encrypt(nonce, data, None)

    enc_path = path + ".enc"
    with open(enc_path, "wb") as f:
        # Prepend nonce so decrypt_file can extract it without storing separately
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

    # First 12 bytes are the nonce written by encrypt_file
    nonce = raw[:12]
    ciphertext = raw[12:]

    decrypted = _aesgcm.decrypt(nonce, ciphertext, None)

    with open(output_path, "wb") as f:
        f.write(decrypted)

    return output_path