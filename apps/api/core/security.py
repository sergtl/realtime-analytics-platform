import hashlib
import secrets

def hash_api_key(raw_key: str) -> str:
    return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

def generate_api_key() -> tuple[str, str, str]:
    raw_key = f"ap_live_{secrets.token_urlsafe(32)}"
    prefix = raw_key[:16]
    return raw_key, prefix, hash_api_key(raw_key)
