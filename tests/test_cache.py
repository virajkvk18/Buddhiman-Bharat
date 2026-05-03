"""
tests/test_cache.py — Tests for utils/cache.py
"""

import time
import pytest
from utils.cache import get, set, invalidate, clear, cached, cache_stats, TTL_ELECTION_DATA


class TestCacheGetSet:
    def setup_method(self):
        clear()

    def test_set_and_get(self):
        set("key1", "value1", ttl=60)
        assert get("key1") == "value1"

    def test_get_missing_key_returns_none(self):
        assert get("nonexistent_key_xyz") is None

    def test_expired_key_returns_none(self):
        set("expiring", "data", ttl=1)
        time.sleep(1.1)
        assert get("expiring") is None

    def test_invalidate_removes_key(self):
        set("to_remove", "data", ttl=60)
        assert get("to_remove") == "data"
        invalidate("to_remove")
        assert get("to_remove") is None

    def test_invalidate_missing_key_no_error(self):
        invalidate("never_set_key")  # should not raise

    def test_clear_removes_all(self):
        set("a", 1, 60)
        set("b", 2, 60)
        clear()
        assert get("a") is None
        assert get("b") is None

    def test_overwrite_key(self):
        set("key", "original", ttl=60)
        set("key", "updated", ttl=60)
        assert get("key") == "updated"

    def test_store_dict_value(self):
        data = {"state": "Bihar", "seats": 243}
        set("election:BR", data, ttl=60)
        assert get("election:BR") == data

    def test_store_list_value(self):
        data = [1, 2, 3]
        set("list_key", data, ttl=60)
        assert get("list_key") == [1, 2, 3]


class TestCacheDecorator:
    def setup_method(self):
        clear()

    def test_cached_function_called_once(self):
        call_count = {"n": 0}

        @cached(ttl=60)
        def expensive(x: int) -> int:
            call_count["n"] += 1
            return x * 2

        assert expensive(5) == 10
        assert expensive(5) == 10   # should hit cache
        assert call_count["n"] == 1  # only called once

    def test_cached_different_args_separate_entries(self):
        call_count = {"n": 0}

        @cached(ttl=60)
        def fn(x: int) -> int:
            call_count["n"] += 1
            return x

        fn(1)
        fn(2)
        assert call_count["n"] == 2  # different args → different cache entries

    def test_cached_expiry_triggers_recompute(self):
        call_count = {"n": 0}

        @cached(ttl=1)
        def fn() -> int:
            call_count["n"] += 1
            return 42

        fn()
        time.sleep(1.1)
        fn()
        assert call_count["n"] == 2  # expired, recomputed


class TestCacheStats:
    def setup_method(self):
        clear()

    def test_empty_stats(self):
        stats = cache_stats()
        assert stats["total_keys"] == 0
        assert stats["active_keys"] == 0

    def test_stats_after_set(self):
        set("k1", "v", ttl=60)
        set("k2", "v", ttl=60)
        stats = cache_stats()
        assert stats["total_keys"] == 2
        assert stats["active_keys"] == 2

    def test_expired_counted_separately(self):
        set("fresh", "v", ttl=60)
        set("stale", "v", ttl=1)
        time.sleep(1.1)
        stats = cache_stats()
        assert stats["active_keys"] == 1
        assert stats["expired_keys"] == 1
