"""디스크 JSON 캐시 — 같은 API 호출·LLM 분석을 반복하지 않도록 한다 (호출 한도·비용 절감)."""
import hashlib
import json
import time
from typing import Any, Callable

from config import CACHE_DIR


def _path(namespace: str, key: Any):
    digest = hashlib.sha1(json.dumps(key, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    return CACHE_DIR / namespace / f"{digest}.json"


def get(namespace: str, key: Any, ttl: float | None = None):
    path = _path(namespace, key)
    if not path.exists():
        return None
    if ttl is not None and time.time() - path.stat().st_mtime > ttl:
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def put(namespace: str, key: Any, value: Any) -> None:
    path = _path(namespace, key)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")


def cached(namespace: str, key: Any, fn: Callable[[], Any], ttl: float | None = None):
    hit = get(namespace, key, ttl)
    if hit is not None:
        return hit
    value = fn()
    if value is not None:
        put(namespace, key, value)
    return value
