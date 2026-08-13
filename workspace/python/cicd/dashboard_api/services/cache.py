import hashlib
import json
import time
from typing import Any, Optional, Dict
from metrics import cache_hits_total, cache_misses_total, cache_entries

_cache: Dict[str, tuple] = {}


def _make_key(provider: str, token: str, path: str, params: dict) -> str:
    token_hash = hashlib.sha256(token.encode()).hexdigest()[:16]
    return f"{provider}:{token_hash}:{path}:{json.dumps(sorted((params or {}).items()))}"


def get_cached(provider: str, token: str, path: str, params: dict, ttl: int) -> Optional[Any]:
    key = _make_key(provider, token, path, params)
    if key in _cache:
        data, ts = _cache[key]
        if time.time() - ts < ttl:
            cache_hits_total.inc()
            return data
    cache_misses_total.inc()
    return None


def set_cached(provider: str, token: str, path: str, params: dict, data: Any) -> None:
    key = _make_key(provider, token, path, params)
    _cache[key] = (data, time.time())
    cache_entries.set(len(_cache))
