"""
Redis caching service for Scopus API results with optional Redis backend and in-memory fallback.
"""

from __future__ import annotations

import hashlib
import json
import time
from fnmatch import fnmatch
from threading import RLock
from typing import Any, Optional

try:
    import redis  # type: ignore
except ImportError:  # pragma: no cover
    redis = None

from app.core.config import settings


class RedisCache:
    """Cache service that uses Redis when available, otherwise falls back to local memory."""

    def __init__(self) -> None:
        self.redis_client = None
        self._memory_store: dict[str, tuple[float, str]] = {}
        self._lock = RLock()
        self._memory_mode = False

        redis_url = (getattr(settings, "redis_url", "") or "").strip()

        if redis is None:
            self._memory_mode = True
            print("ℹ️  redis package not installed. Using in-memory cache only.")
            return

        if not redis_url:
            self._memory_mode = True
            print("ℹ️  No REDIS_URL provided. Using in-memory cache only.")
            return

        try:
            if redis_url.startswith("rediss://"):
                import ssl

                self.redis_client = redis.from_url(
                    redis_url,
                    decode_responses=True,
                    ssl_cert_reqs=ssl.CERT_NONE,
                    ssl_check_hostname=False,
                )
            else:
                self.redis_client = redis.from_url(redis_url, decode_responses=True)

            self.redis_client.ping()
            print("✅ Redis connected successfully")
        except Exception as exc:
            self._switch_to_memory(f"Redis connection failed: {exc}")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _switch_to_memory(self, reason: str) -> None:
        if not self._memory_mode:
            print(f"⚠️  {reason}. Falling back to in-memory cache.")
        self._memory_mode = True
        self.redis_client = None

    @staticmethod
    def _default_ttl() -> int:
        return getattr(settings, "redis_cache_ttl", 3600) or 3600

    def _memory_set(self, key: str, value: Any, ttl: int) -> bool:
        expires_at = time.time() + ttl
        with self._lock:
            self._memory_store[key] = (expires_at, json.dumps(value))
        return True

    def _memory_get(self, key: str) -> Optional[Any]:
        with self._lock:
            entry = self._memory_store.get(key)
            if not entry:
                return None
            expires_at, payload = entry
            if expires_at < time.time():
                self._memory_store.pop(key, None)
                return None
            return json.loads(payload)

    def _memory_delete(self, key: str) -> bool:
        with self._lock:
            existed = key in self._memory_store
            self._memory_store.pop(key, None)
        return existed

    def _memory_clear_pattern(self, pattern: str) -> int:
        with self._lock:
            matching = [k for k in self._memory_store if fnmatch(k, pattern)]
            for key in matching:
                self._memory_store.pop(key, None)
        return len(matching)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def get(self, key: str) -> Optional[Any]:
        if self.redis_client:
            try:
                value = self.redis_client.get(key)
                if value is not None:
                    return json.loads(value)
                return None
            except Exception as exc:
                self._switch_to_memory(f"Redis get error: {exc}")

        return self._memory_get(key)

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        ttl = ttl or self._default_ttl()

        if self.redis_client:
            try:
                self.redis_client.setex(key, ttl, json.dumps(value))
                return True
            except Exception as exc:
                self._switch_to_memory(f"Redis set error: {exc}")

        return self._memory_set(key, value, ttl)

    def delete(self, key: str) -> bool:
        if self.redis_client:
            try:
                self.redis_client.delete(key)
                return True
            except Exception as exc:
                self._switch_to_memory(f"Redis delete error: {exc}")

        return self._memory_delete(key)

    def clear_pattern(self, pattern: str) -> int:
        if self.redis_client:
            try:
                keys = list(self.redis_client.scan_iter(match=pattern))
                if keys:
                    return self.redis_client.delete(*keys)
                return 0
            except Exception as exc:
                self._switch_to_memory(f"Redis clear pattern error: {exc}")

        return self._memory_clear_pattern(pattern)

    def cache_search_results(self, query: str, limit: int, filters: dict, results: Any) -> bool:
        key = self._generate_key("search", query=query, limit=limit, **filters)
        return self.set(key, results)

    def get_cached_search(self, query: str, limit: int, filters: dict) -> Optional[Any]:
        key = self._generate_key("search", query=query, limit=limit, **filters)
        return self.get(key)

    def _generate_key(self, prefix: str, **kwargs) -> str:
        params_str = json.dumps(kwargs, sort_keys=True)
        digest = hashlib.md5(params_str.encode(), usedforsecurity=False)
        return f"{prefix}:{digest.hexdigest()}"


redis_cache = RedisCache()

if redis_cache.redis_client is None:
    print("ℹ️  Redis cache running in in-memory mode. Data will reset on process restart.")
