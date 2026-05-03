"""
utils/cache.py — Smart in-memory caching with TTL for Buddhiman Bharat.

Wraps cachetools TTLCache so expensive API calls (election data, fact-check)
are not repeated within the same session window.
"""

import logging
import time
from functools import wraps
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)

# TTL values (seconds)
TTL_ELECTION_DATA: int = 300        # 5 min — election data is mostly static
TTL_FACT_CHECK: int = 3600          # 1 hour — fact-check results don't change often
TTL_GEMINI_QUICK: int = 86400       # 24 hours — quick answers never change

_store: dict[str, tuple[Any, float]] = {}   # key → (value, expiry_ts)


def _make_key(*args: Any, **kwargs: Any) -> str:
    """Build a deterministic cache key from arguments."""
    return str(args) + str(sorted(kwargs.items()))


def get(key: str) -> Optional[Any]:
    """Return cached value if still valid, else None."""
    if key in _store:
        value, expiry = _store[key]
        if time.monotonic() < expiry:
            logger.debug("Cache HIT: %s", key[:60])
            return value
        del _store[key]
        logger.debug("Cache EXPIRED: %s", key[:60])
    return None


def set(key: str, value: Any, ttl: int = TTL_ELECTION_DATA) -> None:
    """Store value in cache with TTL seconds lifetime."""
    _store[key] = (value, time.monotonic() + ttl)
    logger.debug("Cache SET: %s (ttl=%ds)", key[:60], ttl)


def invalidate(key: str) -> None:
    """Remove a key from cache immediately."""
    _store.pop(key, None)


def clear() -> None:
    """Clear all cached values."""
    _store.clear()
    logger.info("Cache cleared")


def cached(ttl: int = TTL_ELECTION_DATA) -> Callable:
    """
    Decorator: cache the return value of a function for `ttl` seconds.

    Usage::

        @cached(ttl=300)
        def get_election_data(state_code: str) -> dict:
            ...
    """
    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            key = f"{fn.__module__}.{fn.__qualname__}:{_make_key(*args, **kwargs)}"
            cached_val = get(key)
            if cached_val is not None:
                return cached_val
            result = fn(*args, **kwargs)
            set(key, result, ttl)
            return result
        return wrapper
    return decorator


def cache_stats() -> dict:
    """Return basic cache statistics for monitoring."""
    now = time.monotonic()
    active = sum(1 for _, (_, exp) in _store.items() if now < exp)
    return {
        "total_keys": len(_store),
        "active_keys": active,
        "expired_keys": len(_store) - active,
    }
