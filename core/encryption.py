import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

# Both values come from .env
# DB_ENCRYPTION_KEY  — your raw password/secret
# FIELD_ENCRYPTION_SALT — a fixed random salt, generated once

_password = os.getenv("DB_ENCRYPTION_KEY")
_salt_raw = os.getenv("FIELD_ENCRYPTION_SALT")

if not _password or not _salt_raw:
    raise RuntimeError(
        "DB_ENCRYPTION_KEY and FIELD_ENCRYPTION_SALT must be set in .env "
        "before the app can start."
    )

def _derive_fernet_key(password: str, salt: str) -> Fernet:
    """
    Derives a Fernet key from your .env password using PBKDF2.
    100,000 iterations means brute-forcing the .env value is extremely slow
    even if someone sees the raw string.
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt.encode(),
        iterations=100_000,
    )
    derived = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return Fernet(derived)


_fernet = _derive_fernet_key(_password, _salt_raw)


def encrypt_field(value: str) -> str:
    """
    Encrypts a string value before it goes into the database.
    Returns a string (Fernet token) safe to store in a Text column.
    Returns None if value is None.
    """
    if value is None:
        return None
    if not isinstance(value, str):
        raise TypeError(f"encrypt_field expects str, got {type(value)}")
    return _fernet.encrypt(value.encode()).decode()


def decrypt_field(value: str) -> str:
    """
    Decrypts a Fernet token read from the database.
    Returns the original plain string.
    Returns None if value is None.
    """
    if value is None:
        return None
    return _fernet.decrypt(value.encode()).decode()