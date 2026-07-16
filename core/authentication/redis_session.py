import json
import threading
from datetime import datetime, timedelta, timezone
from typing import Optional

import redis
from django.conf import settings

_MEMORY_STORE = {}
_LOCK = threading.Lock()


def _get_client():
    try:
        return redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
    except Exception:
        return None


def create_redis_session(user_id: int, username: str, jti: str, expires_at: datetime):
    payload = {
        "user_id": user_id,
        "username": username,
        "jti": jti,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "expires_at": expires_at.isoformat(),
        "is_active": True,
    }
    client = _get_client()
    if client is not None:
        try:
            client.setex(f"nls:session:{user_id}:{jti}", int((expires_at - datetime.now(timezone.utc)).total_seconds()), json.dumps(payload))
            return payload
        except Exception:
            pass
    with _LOCK:
        _MEMORY_STORE[f"nls:session:{user_id}:{jti}"] = payload
    return payload


def get_redis_session(user_id: int, jti: str) -> Optional[dict]:
    client = _get_client()
    if client is not None:
        try:
            raw = client.get(f"nls:session:{user_id}:{jti}")
            if raw:
                return json.loads(raw)
        except Exception:
            pass
    with _LOCK:
        return _MEMORY_STORE.get(f"nls:session:{user_id}:{jti}")


def delete_redis_session(user_id: int, jti: str) -> None:
    client = _get_client()
    if client is not None:
        try:
            client.delete(f"nls:session:{user_id}:{jti}")
        except Exception:
            pass
    with _LOCK:
        _MEMORY_STORE.pop(f"nls:session:{user_id}:{jti}", None)
