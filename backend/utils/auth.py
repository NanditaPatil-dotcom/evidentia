import hashlib
import hmac
import os

try:
    from passlib.context import CryptContext
except ModuleNotFoundError:
    CryptContext = None


if CryptContext is not None:
    pwd_context = CryptContext(schemes=["bcrypt"])
else:
    pwd_context = None


def _hash_with_pbkdf2(password: str) -> str:
    salt = os.urandom(16).hex()
    iterations = 100_000
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(salt),
        iterations,
    ).hex()
    return f"pbkdf2_sha256${iterations}${salt}${digest}"


def _verify_with_pbkdf2(password: str, hashed_value: str) -> bool:
    try:
        _, iterations, salt, digest = hashed_value.split("$", 3)
    except ValueError:
        return False

    candidate = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(salt),
        int(iterations),
    ).hex()
    return hmac.compare_digest(candidate, digest)


def hash_password(p):
    if pwd_context is not None:
        return pwd_context.hash(p)
    return _hash_with_pbkdf2(p)


def verify_password(p, h):
    if pwd_context is not None:
        return pwd_context.verify(p, h)
    if not isinstance(h, str) or not h.startswith("pbkdf2_sha256$"):
        return False
    return _verify_with_pbkdf2(p, h)
