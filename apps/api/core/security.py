import hashlib
import secrets
from pwdlib import PasswordHash

password_hasher = PasswordHash.recommended()


def hash_secret(raw_secret: str) -> str:
    return hashlib.sha256(raw_secret.encode("utf-8")).hexdigest()


def generate_api_key() -> tuple[str, str, str]:
    raw_key = f"ap_live_{secrets.token_urlsafe(32)}"
    prefix = raw_key[:16]
    return raw_key, prefix, hash_secret(raw_key)


def generate_session_token() -> tuple[str, str]:
    raw_token = secrets.token_urlsafe(32)
    return raw_token, hash_secret(raw_token)


def hash_password(raw_password: str) -> str:
    return password_hasher.hash(raw_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return password_hasher.verify(plain_password, hashed_password)
    except Exception:
        return False
