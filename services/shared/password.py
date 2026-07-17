"""Small SHA-256 hashing helpers for deterministic string checks."""

import hashlib
import hmac


def hash_string(value: str) -> str:
    """Return a SHA-256 hexadecimal digest for a string value."""
    if not isinstance(value, str):
        raise TypeError("Value must be a string.")
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def verify_hash(value: str, hashed_value: str) -> bool:
    """Safely compare a value's digest with a previously calculated digest."""
    return hmac.compare_digest(hash_string(value), hashed_value)
