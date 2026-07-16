import hashlib
import hmac


def hash_string(value: str) -> str:
    if not isinstance(value, str):
        raise TypeError("Value must be a string.")
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def verify_hash(value: str, hashed_value: str) -> bool:
    return hmac.compare_digest(hash_string(value), hashed_value)
